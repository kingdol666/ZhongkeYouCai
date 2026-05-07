#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产线仿真客户端 —— 模拟 CSV 动态生产、换卷、跨天，验证文件夹监控 + 自动处理 + 存档 + 零点切换全流程

目录结构模拟:
  {sim_root}/
  ├── 2026_05/
  │   ├── 07/
  │   │   ├── Test_Tes...OverLmt_141_0/
  │   │   │   ├── 定量/            ← CSV 生产到这里（被监控）
  │   │   │   ├── 定量_Roll/       ← 被忽略
  │   │   │   └── 定量_RollTrend/  ← 被忽略
  │   │   └── Test_Tes...OverLmt_142_0/  ← 换卷后新建
  │   │       └── 定量/
  │   └── 08/  ← "过了一天" 后
  │       └── Test_Tes...OverLmt_143_0/
  │           └── 定量/
"""

import os
import sys
import shutil
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QFileDialog, QLabel,
    QGroupBox, QGridLayout, QProgressBar,
    QMessageBox, QScrollArea, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

# 确保项目路径可导入
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from logic.folder_monitor import MonitorCore, extract_roll_number
from logic.data_processor import SingleFolderProcessorThread


# ======================== 仿真核心 ========================
class ProductionSimulator:
    """产线仿真器：管理模拟目录（含日期层级）、CSV 源队列、换卷/跨天逻辑"""

    def __init__(self, sim_root: str, source_dir: str):
        self.sim_root = sim_root          # CustomProfile 根目录
        self.source_dir = source_dir
        self._sim_date = datetime.now()   # 仿真日期
        self._roll_counter = 141
        self._current_test_dir: str | None = None
        self._current_dingliang_dir: str | None = None
        self._source_queue: list[str] = []
        self._queue_index = 0

    # ---- 日期管理 ----
    @property
    def sim_date(self) -> datetime:
        return self._sim_date

    @property
    def sim_date_str(self) -> str:
        """返回 'YYYY_MM/DD' 格式的日期路径"""
        d = self._sim_date
        return f"{d.year}_{d.month:02d}/{d.day:02d}"

    @property
    def date_root(self) -> str:
        """当前仿真日期对应的文件夹：{sim_root}/{year}_{month}/{day}"""
        return os.path.join(self.sim_root, self.sim_date_str)

    def advance_day(self) -> str:
        """
        过了一天：仿真日期 +1，创建新日期对应的目录结构，
        重置卷膜计数器，创建第一个 Test_* 目录。
        返回新的 date_root。
        """
        self._sim_date += timedelta(days=1)
        new_root = self.date_root
        os.makedirs(new_root, exist_ok=True)
        self._roll_counter = 141  # 重置卷膜编号
        test_name = self._make_test_dir_name()
        test_dir = os.path.join(new_root, test_name)
        self._create_test_structure(test_dir)
        self._current_test_dir = test_dir
        self._current_dingliang_dir = os.path.join(test_dir, "定量")
        return new_root

    # ---- 源 CSV 队列 ----
    def load_source_queue(self):
        files = []
        for root, dirs, fnames in os.walk(self.source_dir):
            for fn in fnames:
                if fn.upper().endswith('.CSV'):
                    files.append(os.path.join(root, fn))
        self._source_queue = sorted(files)
        self._queue_index = 0
        return len(self._source_queue)

    @property
    def queue_total(self) -> int:
        return len(self._source_queue)

    @property
    def queue_remaining(self) -> int:
        return max(0, len(self._source_queue) - self._queue_index)

    def _next_source_csv(self) -> str | None:
        if self._queue_index >= len(self._source_queue):
            return None
        path = self._source_queue[self._queue_index]
        self._queue_index += 1
        return path

    # ---- 目录管理 ----
    def _make_test_dir_name(self) -> str:
        ts = self._sim_date.strftime("%Y%m%d%H%M%S")
        name = f"Test_Tes{ts}OverLmt_{self._roll_counter}_0"
        self._roll_counter += 1
        return name

    def setup_initial(self) -> str:
        """创建初始环境：日期文件夹 + 第一个 Test_* 目录"""
        date_root = self.date_root
        os.makedirs(date_root, exist_ok=True)
        test_name = self._make_test_dir_name()
        test_dir = os.path.join(date_root, test_name)
        self._create_test_structure(test_dir)
        self._current_test_dir = test_dir
        self._current_dingliang_dir = os.path.join(test_dir, "定量")
        return test_dir

    def change_roll(self) -> str:
        """换卷：当前日期下新建 Test_* 文件夹"""
        date_root = self.date_root
        if not os.path.isdir(date_root):
            os.makedirs(date_root, exist_ok=True)
        test_name = self._make_test_dir_name()
        test_dir = os.path.join(date_root, test_name)
        self._create_test_structure(test_dir)
        self._current_test_dir = test_dir
        self._current_dingliang_dir = os.path.join(test_dir, "定量")
        return test_dir

    def _create_test_structure(self, test_dir: str):
        os.makedirs(os.path.join(test_dir, "定量"), exist_ok=True)
        os.makedirs(os.path.join(test_dir, "定量_Roll"), exist_ok=True)
        os.makedirs(os.path.join(test_dir, "定量_RollTrend"), exist_ok=True)

    def produce_csv(self) -> tuple[str, str] | None:
        """生产一个 CSV 到当前 定量 文件夹。返回 (dst_path, parent_dir) 或 None"""
        if not self._current_dingliang_dir:
            return None
        src = self._next_source_csv()
        if src is None:
            return None
        dst = os.path.join(self._current_dingliang_dir, os.path.basename(src))
        shutil.copy2(src, dst)
        return dst, self._current_dingliang_dir

    @property
    def current_test_dir(self) -> str | None:
        return self._current_test_dir

    @property
    def current_dingliang_dir(self) -> str | None:
        return self._current_dingliang_dir


# ======================== 仿真 UI ========================
class SimulationWindow(QWidget):
    """产线仿真主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("产线仿真 — 文件夹监控验证")
        self.resize(1050, 780)

        self._sim: ProductionSimulator | None = None
        self._monitor: MonitorCore | None = None
        self._processor: SingleFolderProcessorThread | None = None
        self._monitor_busy = False
        self._monitor_current_csv: str | None = None
        self._monitor_current_image: str | None = None
        self._monitor_current_parent: str | None = None
        self._monitor_queue: list[tuple[str, bool]] = []
        self._params: dict = {}
        self._csv_produced = 0

        self._auto_timer = QTimer()
        self._auto_timer.timeout.connect(self._auto_produce)

        self._init_ui()
        self._set_defaults()

    # ==================== UI ====================
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # ---- 仿真目录设置 ----
        g1 = QGroupBox("仿真环境设置")
        g1_layout = QGridLayout()
        g1_layout.setSpacing(8)

        g1_layout.addWidget(QLabel("源数据文件夹:"), 0, 0)
        self.src_edit = QLineEdit()
        self.src_edit.setReadOnly(True)
        g1_layout.addWidget(self.src_edit, 0, 1)
        btn_src = QPushButton("浏览...")
        btn_src.clicked.connect(self._browse_src)
        g1_layout.addWidget(btn_src, 0, 2)

        g1_layout.addWidget(QLabel("仿真根目录:"), 1, 0)
        self.root_edit = QLineEdit()
        self.root_edit.setReadOnly(True)
        g1_layout.addWidget(self.root_edit, 1, 1)
        btn_root = QPushButton("浏览...")
        btn_root.clicked.connect(self._browse_root)
        g1_layout.addWidget(btn_root, 1, 2)

        g1_layout.addWidget(QLabel("忽略文件夹:"), 2, 0)
        self.ignore_edit = QLineEdit("定量_Roll, 定量_RollTrend")
        g1_layout.addWidget(self.ignore_edit, 2, 1)

        g1_layout.addWidget(QLabel("输出文件夹:"), 3, 0)
        self.out_edit = QLineEdit()
        self.out_edit.setReadOnly(True)
        g1_layout.addWidget(self.out_edit, 3, 1)
        btn_out = QPushButton("浏览...")
        btn_out.clicked.connect(self._browse_out)
        g1_layout.addWidget(btn_out, 3, 2)

        g1_layout.addWidget(QLabel("存档文件夹:"), 4, 0)
        self.save_edit = QLineEdit()
        self.save_edit.setReadOnly(True)
        g1_layout.addWidget(self.save_edit, 4, 1)
        btn_save = QPushButton("浏览...")
        btn_save.clicked.connect(self._browse_save)
        g1_layout.addWidget(btn_save, 4, 2)

        g1.setLayout(g1_layout)
        layout.addWidget(g1)

        # ---- 仿真控制 ----
        g2 = QGroupBox("仿真控制")
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.btn_setup = QPushButton("1. 设置模拟环境")
        self.btn_setup.clicked.connect(self._setup_env)
        ctrl_layout.addWidget(self.btn_setup)

        self.btn_produce = QPushButton("2. 生产CSV")
        self.btn_produce.clicked.connect(self._produce_one)
        self.btn_produce.setEnabled(False)
        ctrl_layout.addWidget(self.btn_produce)

        self.btn_change = QPushButton("3. 换卷")
        self.btn_change.clicked.connect(self._change_roll)
        self.btn_change.setEnabled(False)
        ctrl_layout.addWidget(self.btn_change)

        self.btn_next_day = QPushButton("4. 过了一天")
        self.btn_next_day.setObjectName("nextDayButton")
        self.btn_next_day.clicked.connect(self._advance_day)
        self.btn_next_day.setEnabled(False)
        ctrl_layout.addWidget(self.btn_next_day)

        self.btn_auto = QPushButton("自动生产(2s)")
        self.btn_auto.clicked.connect(self._toggle_auto)
        self.btn_auto.setEnabled(False)
        ctrl_layout.addWidget(self.btn_auto)

        self.btn_start_mon = QPushButton("启动监控")
        self.btn_start_mon.clicked.connect(self._start_monitor)
        self.btn_start_mon.setEnabled(False)
        ctrl_layout.addWidget(self.btn_start_mon)

        self.btn_stop_mon = QPushButton("停止监控")
        self.btn_stop_mon.clicked.connect(self._stop_monitor)
        self.btn_stop_mon.setEnabled(False)
        ctrl_layout.addWidget(self.btn_stop_mon)

        ctrl_layout.addStretch()
        g2.setLayout(ctrl_layout)
        layout.addWidget(g2)

        # ---- 状态信息 ----
        g3 = QGroupBox("当前状态")
        st_layout = QGridLayout()
        st_layout.setSpacing(6)
        self.lbl_date = QLabel("仿真日期: -")
        self.lbl_date.setStyleSheet("font-weight: bold; color: #e67e22;")
        st_layout.addWidget(self.lbl_date, 0, 0)
        self.lbl_roll = QLabel("当前卷膜: -")
        st_layout.addWidget(self.lbl_roll, 0, 1)
        self.lbl_csv_count = QLabel("已生产: 0")
        st_layout.addWidget(self.lbl_csv_count, 0, 2)
        self.lbl_last_parent = QLabel("last_parent: -")
        st_layout.addWidget(self.lbl_last_parent, 1, 0, 1, 2)
        self.lbl_queue = QLabel("剩余队列: -")
        st_layout.addWidget(self.lbl_queue, 1, 2)
        g3.setLayout(st_layout)
        layout.addWidget(g3)

        # ---- 进度条 ----
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # ---- 图像显示 ----
        g4 = QGroupBox("实时热力云图")
        img_layout = QVBoxLayout()
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(200)
        self.img_label = QLabel("云图将在此显示")
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label.setStyleSheet(
            "QLabel { background-color: white; border: 2px solid #ccc; border-radius: 6px; }")
        self._orig_pixmap = None
        self._zoomed = False
        self.img_label.mouseDoubleClickEvent = self._img_dbl_click
        self.scroll.setWidget(self.img_label)
        img_layout.addWidget(self.scroll)
        g4.setLayout(img_layout)
        layout.addWidget(g4, 1)

        # ---- 日志 ----
        g5 = QGroupBox("事件日志")
        log_layout = QVBoxLayout()
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setFont(QFont("Consolas", 9))
        self.log_edit.setMaximumHeight(150)
        log_layout.addWidget(self.log_edit)
        g5.setLayout(log_layout)
        layout.addWidget(g5)

    def _set_defaults(self):
        project_root = PROJECT_ROOT
        self.src_edit.setText(os.path.join(project_root, "Data", "1-5"))
        self.root_edit.setText(os.path.join(project_root, "sim_test"))
        self.out_edit.setText(os.path.join(project_root, "sim_test_output"))
        self.save_edit.setText(os.path.join(project_root, "sim_test_saved"))

    # ==================== 按钮回调 ====================
    def _browse_src(self):
        d = QFileDialog.getExistingDirectory(self, "源数据文件夹", self.src_edit.text())
        if d: self.src_edit.setText(d)

    def _browse_root(self):
        d = QFileDialog.getExistingDirectory(self, "仿真根目录", self.root_edit.text())
        if d: self.root_edit.setText(d)

    def _browse_out(self):
        d = QFileDialog.getExistingDirectory(self, "输出文件夹", self.out_edit.text())
        if d: self.out_edit.setText(d)

    def _browse_save(self):
        d = QFileDialog.getExistingDirectory(self, "存档文件夹", self.save_edit.text())
        if d: self.save_edit.setText(d)

    def _setup_env(self):
        """初始化仿真环境"""
        src = self.src_edit.text()
        root = self.root_edit.text()
        if not os.path.isdir(src):
            QMessageBox.warning(self, "错误", "源数据文件夹不存在")
            return

        self._log("=" * 50)
        self._log("初始化仿真环境")
        self._log(f"  仿真根目录: {root}")

        os.makedirs(root, exist_ok=True)
        os.makedirs(self.out_edit.text(), exist_ok=True)
        os.makedirs(self.save_edit.text(), exist_ok=True)

        self._sim = ProductionSimulator(root, src)
        count = self._sim.load_source_queue()
        self._log(f"  源数据加载: {count} 个 CSV 文件")

        test_dir = self._sim.setup_initial()
        self._log(f"  仿真日期: {self._sim.sim_date_str}")
        self._log(f"  日期文件夹: {self._sim.date_root}")
        self._log(f"  初始卷膜: {os.path.basename(test_dir)}")
        self._log(f"  定量文件夹: {self._sim.current_dingliang_dir}")
        self._log(f"  定量_Roll / 定量_RollTrend 已创建（将被忽略）")

        self._csv_produced = 0
        self._update_status()
        self.btn_produce.setEnabled(True)
        self.btn_change.setEnabled(True)
        self.btn_next_day.setEnabled(True)
        self.btn_auto.setEnabled(True)
        self.btn_start_mon.setEnabled(True)

    def _produce_one(self):
        """生产一个 CSV 文件"""
        if not self._sim:
            return
        result = self._sim.produce_csv()
        if result is None:
            self._log("[队列耗尽] 没有更多 CSV 文件可生产")
            self.btn_produce.setEnabled(False)
            self.btn_auto.setEnabled(False)
            return
        dst_path, parent_dir = result
        self._csv_produced += 1
        self._log(f"[生产] {os.path.basename(dst_path)} -> {os.path.basename(parent_dir)}/")
        self._update_status()

    def _change_roll(self):
        """换卷：当前日期下创建新 Test_* 文件夹"""
        if not self._sim:
            return
        new_dir = self._sim.change_roll()
        self._log("-" * 40)
        self._log(f"[换卷] 新卷膜: {os.path.basename(new_dir)}")
        self._log(f"  日期: {self._sim.sim_date_str}")
        if self._monitor:
            self._monitor.reset_last_parent()
            self._log("  last_parent 已重置，下一个 CSV 将触发 different_parent")
        self._update_status()

    def _advance_day(self):
        """过了一天：仿真日期 +1，创建新日期文件夹 + 初始卷膜，触发监控切换"""
        if not self._sim:
            return
        old_date = self._sim.sim_date_str
        new_root = self._sim.advance_day()
        self._csv_produced = 0
        self._log("=" * 50)
        self._log(f"[过了一天] 日期变更: {old_date} -> {self._sim.sim_date_str}")
        self._log(f"  新日期文件夹: {new_root}")
        self._log(f"  新卷膜: {os.path.basename(self._sim.current_test_dir or '-')}")

        # 如果监控正在运行，模拟零点切换：停止旧监控 → 重启到新日期文件夹
        if self._monitor:
            self._log("  >>> 模拟零点切换：重启监控到新日期文件夹 <<<")
            self._restart_monitor_for_new_day(new_root)

        self._update_status()

    def _toggle_auto(self):
        if self._auto_timer.isActive():
            self._auto_timer.stop()
            self.btn_auto.setText("自动生产(2s)")
            self._log("[自动生产] 已停止")
        else:
            self._auto_timer.start(2000)
            self.btn_auto.setText("停止自动")
            self._log("[自动生产] 已启动 (每2秒产出一个CSV)")

    def _auto_produce(self):
        if self._monitor_busy:
            return
        self._produce_one()

    # ==================== 监控 ====================
    def _start_monitor(self):
        raw = self.ignore_edit.text().strip()
        ignore = {n.strip() for n in raw.split(',') if n.strip()} if raw else set()

        self._monitor_queue.clear()
        self._monitor_busy = False
        self._monitor_current_csv = None
        self._monitor_current_image = None
        self._params = {
            'start_row': 8, 'end_row': 190,
            'start_pos': 2.50, 'end_pos': 14.39
        }

        # 监控当前仿真日期对应的文件夹（模拟 CustomProfile/{date}）
        monitor_root = self._sim.date_root if self._sim else self.root_edit.text()
        self._monitor = MonitorCore(ignore_dir_names=ignore)
        self._monitor.same_parent_detected.connect(self._on_same_parent)
        self._monitor.different_parent_detected.connect(self._on_different_parent)
        self._monitor.status_changed.connect(self._log)
        self._monitor.start_monitoring(monitor_root)

        self.btn_start_mon.setEnabled(False)
        self.btn_stop_mon.setEnabled(True)
        self._log("=" * 50)
        self._log(f"监控已启动")
        self._log(f"  监控路径: {monitor_root}")
        self._log(f"  忽略文件夹: {ignore}")

    def _stop_monitor(self):
        if self._monitor:
            self._monitor.stop_monitoring()
            self._monitor = None
        self._auto_timer.stop()
        self.btn_auto.setText("自动生产(2s)")
        self.btn_start_mon.setEnabled(True)
        self.btn_stop_mon.setEnabled(False)
        self._log("=" * 50)
        self._log("监控已停止")

    def _restart_monitor_for_new_day(self, new_root: str):
        """零点切换：停止旧监控，在新日期文件夹上重启监控"""
        raw = self.ignore_edit.text().strip()
        ignore = {n.strip() for n in raw.split(',') if n.strip()} if raw else set()

        # 停止旧监控
        old = self._monitor
        if old:
            old.same_parent_detected.disconnect()
            old.different_parent_detected.disconnect()
            old.status_changed.disconnect()
            old.stop_monitoring()

        if self._processor and self._processor.isRunning():
            self._processor.stop()

        self._monitor_queue.clear()
        self._monitor_busy = False
        self._monitor_current_csv = None
        self._monitor_current_image = None

        # 启动新监控
        self._monitor = MonitorCore(ignore_dir_names=ignore)
        self._monitor.same_parent_detected.connect(self._on_same_parent)
        self._monitor.different_parent_detected.connect(self._on_different_parent)
        self._monitor.status_changed.connect(self._log)
        self._monitor.start_monitoring(new_root)

        self.progress_bar.setValue(0)
        self._log(f"  监控已切换到新日期文件夹: {new_root}")

    # ---- MonitorCore 信号 ----
    def _on_same_parent(self, parent_dir, filename):
        self._log(f"  >>> [SAME_PARENT] {os.path.basename(parent_dir)}/{filename}")
        self.lbl_last_parent.setText(f"last_parent: ...{parent_dir[-45:]}")
        self._enqueue_or_process(parent_dir, is_same_parent=True)

    def _on_different_parent(self, parent_dir, filename):
        self._log(f"  >>> [DIFFERENT_PARENT] {os.path.basename(parent_dir)}/{filename}")
        self.lbl_last_parent.setText(f"last_parent: ...{parent_dir[-45:]}")
        self._enqueue_or_process(parent_dir, is_same_parent=False)

    def _enqueue_or_process(self, parent_dir, is_same_parent):
        for q_dir, _ in self._monitor_queue:
            if q_dir == parent_dir:
                return
        if self._monitor_busy:
            self._monitor_queue.append((parent_dir, is_same_parent))
            self._log(f"    (queued, len={len(self._monitor_queue)})")
        else:
            self._run_processor(parent_dir, is_same_parent)

    def _run_processor(self, parent_dir, is_same_parent):
        self._monitor_busy = True
        self._monitor_current_parent = parent_dir
        if not is_same_parent:
            self._auto_save()

        p = self._params
        self._processor = SingleFolderProcessorThread(
            parent_dir, self.out_edit.text(),
            p['start_row'], p['end_row'],
            p['start_pos'], p['end_pos']
        )
        self._processor.progress_updated.connect(self.progress_bar.setValue)
        self._processor.status_updated.connect(self._log)
        self._processor.image_ready.connect(self._display_image)
        self._processor.finished.connect(self._proc_finished)
        self._processor.start()
        self._log(f"    [处理] {os.path.basename(parent_dir)}")

    def _auto_save(self):
        csv_path = self._monitor_current_csv
        img_path = self._monitor_current_image
        if not csv_path or not img_path:
            return
        if not os.path.exists(csv_path) or not os.path.exists(img_path):
            return
        save_dir = self.save_edit.text()
        try:
            roll_number = extract_roll_number(self._monitor_current_parent) \
                if self._monitor_current_parent else None
            target, _, _ = MonitorCore.save_results(
                csv_path, img_path, save_dir, roll_number=roll_number)
            self._log(f"    [自动存档] {target}")
        except Exception as e:
            self._log(f"    [自动存档失败] {e}")

    def _proc_finished(self, success, message):
        self._monitor_busy = False
        self._log(f"    [完成] {message}")
        if self._monitor_queue:
            next_dir, next_same = self._monitor_queue.pop(0)
            self._log(f"    (dequeue) {os.path.basename(next_dir)}")
            self._run_processor(next_dir, next_same)

    def _display_image(self, image_path, title):
        self._monitor_current_image = image_path
        folder = os.path.basename(self._processor.folder_path)
        csv_path = os.path.join(self.out_edit.text(), f"merged_{folder}.csv")
        if os.path.exists(csv_path):
            self._monitor_current_csv = csv_path

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self._log("    [错误] 无法加载图像")
            return
        self._orig_pixmap = pixmap
        self._zoomed = False
        self._scale_image(pixmap)
        self.img_label.setText("")

    def _scale_image(self, pixmap):
        w = self.scroll.width() - 10 or 600
        h = self.scroll.height() - 10 or 250
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)

    def _img_dbl_click(self, event):
        if not self._orig_pixmap:
            return
        self._zoomed = not self._zoomed
        if self._zoomed:
            self.img_label.setPixmap(self._orig_pixmap)
            self.img_label.setMinimumSize(self._orig_pixmap.size())
        else:
            self.img_label.setMinimumSize(1, 1)
            self._scale_image(self._orig_pixmap)

    # ==================== 辅助 ====================
    def _update_status(self):
        if self._sim:
            self.lbl_date.setText(f"仿真日期: {self._sim.sim_date_str}")
            self.lbl_roll.setText(f"当前卷膜: {os.path.basename(self._sim.current_test_dir or '-')}")
            self.lbl_csv_count.setText(f"已生产: {self._csv_produced}")
            self.lbl_queue.setText(f"剩余队列: {self._sim.queue_remaining}")

    def _log(self, msg):
        self.log_edit.append(msg)
        sb = self.log_edit.verticalScrollBar()
        sb.setValue(sb.maximum())


# ======================== 入口 ========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SimulationWindow()
    win.show()
    sys.exit(app.exec())
