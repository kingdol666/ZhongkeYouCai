#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹监控核心模块：递归监视文件夹，检测新增CSV文件，
根据父目录是否与上次相同发射对应信号
"""

import os
import re
import shutil
from datetime import datetime

from PyQt5.QtCore import QObject, QFileSystemWatcher, QTimer, pyqtSignal


def extract_roll_number(parent_dir: str) -> str | None:
    """从父目录路径中提取卷号。

    例: /path/Test_Tes20260423150029OverLmt_143_0/定量 → '143'
    """
    test_dir = os.path.basename(os.path.dirname(parent_dir))
    match = re.search(r'OverLmt_(\d+)_\d+$', test_dir)
    return match.group(1) if match else None


class MonitorCore(QObject):
    """文件夹监控逻辑核心（非UI），通过信号通知外部"""

    # 新CSV出现在与上次相同的父目录 -> (父目录路径, CSV文件名)
    same_parent_detected = pyqtSignal(str, str)
    # 新CSV出现在与上次不同的父目录 -> (父目录路径, CSV文件名)
    different_parent_detected = pyqtSignal(str, str)
    # 状态/日志消息
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None, ignore_dir_names: set[str] | None = None):
        """
        Args:
            parent: Qt parent
            ignore_dir_names: 要跳过监控的文件夹名称集合（如 {'定量_Roll', '定量_RollTrend'}）
        """
        super().__init__(parent)
        self._ignore_dir_names = ignore_dir_names or set()
        self._watcher = QFileSystemWatcher()
        self._watcher.directoryChanged.connect(self._on_directory_changed)

        # 防抖定时器：目录变化后等待一段时间再处理，避免同一批文件触发多次
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._flush_pending)

        # {目录路径: set(文件名)}  缓存当前已知的文件列表
        self._dir_files: dict[str, set[str]] = {}
        # 上一次产生新CSV的父目录（绝对路径）
        self._last_parent: str | None = None
        # 当前监控的根目录
        self._monitor_root: str | None = None
        # 待处理的变更: {parent_dir: set(new_csv_filenames)}
        self._pending: dict[str, set[str]] = {}

    # ---------- 公共接口 ----------
    def start_monitoring(self, root_path: str):
        """启动对 root_path 及其所有子目录的递归监控"""
        self.stop_monitoring()
        self._monitor_root = os.path.abspath(root_path)
        self._add_all_subdirs(self._monitor_root)
        self._last_parent = None
        self._pending.clear()
        self.status_changed.emit(f"监控已启动: {self._monitor_root}")

    def stop_monitoring(self):
        """停止所有监控并清空状态"""
        dirs = self._watcher.directories()
        if dirs:
            self._watcher.removePaths(dirs)
        self._dir_files.clear()
        self._last_parent = None
        self._monitor_root = None
        self._pending.clear()
        self._debounce_timer.stop()
        self.status_changed.emit("监控已停止")

    def is_monitoring(self) -> bool:
        return self._monitor_root is not None and bool(self._watcher.directories())

    @property
    def monitor_root(self) -> str | None:
        return self._monitor_root

    def reset_last_parent(self):
        """手动重置 last_parent，下次任何新文件都视为 different_parent"""
        self._last_parent = None

    # ---------- 内部实现 ----------
    def _add_all_subdirs(self, root: str):
        """递归将 root 及其所有子目录加入监视，跳过忽略的文件夹名，并缓存初始文件列表"""
        if not os.path.isdir(root):
            return
        self._watcher.addPath(root)
        self._dir_files[root] = self._current_files(root)
        try:
            for entry in os.scandir(root):
                if entry.is_dir() and entry.name not in self._ignore_dir_names:
                    self._add_all_subdirs(entry.path)
        except OSError:
            pass

    @staticmethod
    def _current_files(directory: str) -> set[str]:
        """返回 directory 下所有文件的文件名集合"""
        try:
            with os.scandir(directory) as it:
                return {entry.name for entry in it if entry.is_file()}
        except OSError:
            return set()

    def _on_directory_changed(self, path: str):
        """目录发生变更时的槽函数"""
        current = self._current_files(path)
        previous = self._dir_files.get(path, set())
        new_files = current - previous

        # 只关注CSV文件
        for filename in sorted(new_files):
            if filename.upper().endswith('.CSV'):
                self._pending.setdefault(path, set()).add(filename)

        # 检查是否有新增子目录并加入监视
        self._add_new_subdirs(path)
        self._dir_files[path] = current

        if self._pending:
            # 重启防抖定时器（1.5秒内的变更合并处理）
            self._debounce_timer.start(1500)

    def _flush_pending(self):
        """防抖定时器到期，批量处理所有待处理的新CSV文件"""
        if not self._pending:
            return

        # 按父目录分组处理
        for parent_dir, filenames in self._pending.items():
            for filename in sorted(filenames):
                self._handle_new_file(parent_dir, filename)

        self._pending.clear()

    def _handle_new_file(self, parent_dir: str, filename: str):
        """根据父目录是否与上次相同，发射对应信号"""
        self.status_changed.emit(f"检测到新CSV: {os.path.join(parent_dir, filename)}")

        if self._last_parent is None:
            # 首次
            self.different_parent_detected.emit(parent_dir, filename)
            self._last_parent = parent_dir
        elif parent_dir == self._last_parent:
            self.same_parent_detected.emit(parent_dir, filename)
        else:
            self.different_parent_detected.emit(parent_dir, filename)
            self._last_parent = parent_dir

    def _add_new_subdirs(self, parent_dir: str):
        """将 parent_dir 下新出现的子目录加入监控（跳过忽略的文件夹名）"""
        try:
            for entry in os.scandir(parent_dir):
                if entry.is_dir() and entry.name not in self._ignore_dir_names \
                        and entry.path not in self._dir_files:
                    self._watcher.addPath(entry.path)
                    self._dir_files[entry.path] = self._current_files(entry.path)
                    self.status_changed.emit(f"新增子目录监控: {entry.path}")
                    # 递归处理更深层的新目录
                    self._add_all_subdirs(entry.path)
        except OSError:
            pass

    # ---------- 保存操作 ----------
    @staticmethod
    def save_results(csv_path: str, image_path: str, save_dir: str,
                     roll_number: str | None = None):
        """将处理结果保存到指定目录。

        若提供卷号则按卷号命名:  SavedResults/result_20260507_143_0
        否则使用时间戳命名:        SavedResults/result_20260507_193511
        """
        if roll_number:
            date_str = datetime.now().strftime("%Y%m%d")
            base = f"result_{date_str}_{roll_number}"
            target_dir = os.path.join(save_dir, base)
            seq = 0
            while os.path.exists(target_dir):
                seq += 1
                target_dir = os.path.join(save_dir, f"{base}_{seq}")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_dir = os.path.join(save_dir, f"result_{timestamp}")

        os.makedirs(target_dir, exist_ok=True)

        dst_csv = os.path.join(target_dir, os.path.basename(csv_path))
        dst_img = os.path.join(target_dir, os.path.basename(image_path))

        shutil.copy2(csv_path, dst_csv)
        shutil.copy2(image_path, dst_img)

        return target_dir, dst_csv, dst_img
