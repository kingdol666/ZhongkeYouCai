#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV数据批处理工具 - 主窗口界面
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar,
                            QTextEdit, QGroupBox, QGridLayout, QMessageBox,
                            QTextBrowser, QScrollArea, QSizePolicy, QCheckBox,
                            QStackedWidget, QFrame, QDateEdit, QRubberBand)
from PyQt6.QtCore import Qt, QTimer, QDate, QPoint, QRect, QSize
from PyQt6.QtGui import QFont, QPixmap, QCursor

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic.data_processor import DataProcessorThread, SingleFolderProcessorThread
from logic.folder_monitor import MonitorCore
from logic.database import init_db, insert_record, query_records, update_record, delete_record

# 导入热力云图组件
from ui.heatmap_widget import HeatmapWidget
# 导入现代风格样式
from ui.modern_style import MODERN_STYLE
from ui.image_viewer import ImageViewerWindow
# 导入Markdown支持
import markdown


class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.processor_thread = None
        self.single_folder_thread = None
        # 文件夹监控相关状态
        self._monitor_core = None
        self._monitor_thread = None
        self._monitor_current_csv: str | None = None
        self._monitor_current_image: str | None = None
        self._monitor_current_parent: str | None = None
        self._monitor_queue: list[tuple[str, bool]] = []  # [(parent_dir, is_same_parent), ...]
        self._monitor_busy = False
        self._midnight_timer: QTimer | None = None
        self._last_midnight_date: str | None = None  # 记录上次触发的日期，避免重复

        # 放大模式状态（单文件夹、监控、历史 三个预览共用此模式）
        for prefix in ('_sf', '_mf', '_hist'):
            setattr(self, f'{prefix}_zoom_mode', False)
            setattr(self, f'{prefix}_rubber_band', None)
            setattr(self, f'{prefix}_rubber_origin', None)
            setattr(self, f'{prefix}_zoom_history', [])
            setattr(self, f'{prefix}_current_image_path', '')

        self.init_ui()
        
    def init_ui(self):
        """初始化UI — 左侧可折叠导航 + 右侧内容区"""
        self.setWindowTitle("CSV数据批处理工具")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(MODERN_STYLE)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ---------- 先创建所有内容页 ----------
        self.data_process_tab = QWidget()
        self.init_data_process_tab()

        self.single_folder_tab = QWidget()
        self.init_single_folder_tab()

        self.monitor_tab = QWidget()
        self.init_monitor_tab()

        self.heatmap_tab = HeatmapWidget()

        init_db()
        self.history_tab = QWidget()
        self.init_history_tab()

        self.usage_tab = QWidget()
        self.init_usage_tab()

        # ---------- 左侧导航栏 ----------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo 区
        logo_frame = QFrame()
        logo_frame.setObjectName("logoFrame")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 24, 20, 18)
        self._logo_title = QLabel("📊  CSV批处理工具")
        self._logo_title.setObjectName("logoTitle")
        self._logo_subtitle = QLabel("ZhongkeYouCai")
        self._logo_subtitle.setObjectName("logoSubtitle")
        logo_layout.addWidget(self._logo_title)
        logo_layout.addWidget(self._logo_subtitle)
        sidebar_layout.addWidget(logo_frame)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sidebarSeparator")
        sidebar_layout.addWidget(sep)

        # 导航按钮
        self.nav_stack = QStackedWidget()
        self.nav_buttons: list[QPushButton] = []

        self._nav_data = [
            ("📊", "数据处理", self.data_process_tab),
            ("📁", "单文件夹分析", self.single_folder_tab),
            ("👁", "文件夹监控", self.monitor_tab),
            ("🌡", "热力云图", self.heatmap_tab),
            ("📋", "历史数据", self.history_tab),
            ("📖", "使用说明", self.usage_tab),
        ]

        for i, (icon, label, widget) in enumerate(self._nav_data):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self._on_nav_clicked(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.nav_stack.addWidget(widget)

        sidebar_layout.addStretch()

        # 折叠按钮
        self.collapse_btn = QPushButton("◀  折叠导航")
        self.collapse_btn.setObjectName("collapseButton")
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.clicked.connect(self._toggle_sidebar)
        sidebar_layout.addWidget(self.collapse_btn)

        root_layout.addWidget(self.sidebar)

        # ---------- 右侧内容区 ----------
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.nav_stack)
        root_layout.addWidget(content_frame, 1)

        # 默认选中第一个
        self.nav_buttons[0].setChecked(True)
        self.nav_stack.setCurrentIndex(0)
        
    def init_data_process_tab(self):
        """初始化数据处理标签页"""
        # 创建主布局
        main_layout = QVBoxLayout(self.data_process_tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 创建参数设置组
        param_group = QGroupBox("参数设置")
        param_layout = QGridLayout()
        param_layout.setContentsMargins(15, 20, 15, 15)
        param_layout.setSpacing(12)
        
        # 输入文件夹
        param_layout.addWidget(QLabel("输入文件夹:"), 0, 0)
        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setReadOnly(True)
        param_layout.addWidget(self.input_folder_edit, 0, 1)
        input_folder_btn = QPushButton("浏览...")
        input_folder_btn.setObjectName("browseButton")
        input_folder_btn.clicked.connect(self.browse_input_folder)
        param_layout.addWidget(input_folder_btn, 0, 2)
        
        # 输出文件夹
        param_layout.addWidget(QLabel("输出文件夹:"), 1, 0)
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        param_layout.addWidget(self.output_folder_edit, 1, 1)
        output_folder_btn = QPushButton("浏览...")
        output_folder_btn.setObjectName("browseButton")
        output_folder_btn.clicked.connect(self.browse_output_folder)
        param_layout.addWidget(output_folder_btn, 1, 2)
        
        # 起始行号
        param_layout.addWidget(QLabel("起始行号:"), 2, 0)
        self.start_row_edit = QLineEdit("8")
        param_layout.addWidget(self.start_row_edit, 2, 1)
        
        # 终止行号
        param_layout.addWidget(QLabel("终止行号:"), 3, 0)
        self.end_row_edit = QLineEdit("190")
        param_layout.addWidget(self.end_row_edit, 3, 1)
        
        # 起始模头位置
        param_layout.addWidget(QLabel("起始模头位置:"), 4, 0)
        self.start_pos_edit = QLineEdit("2.50")
        param_layout.addWidget(self.start_pos_edit, 4, 1)
        
        # 终止模头位置
        param_layout.addWidget(QLabel("终止模头位置:"), 5, 0)
        self.end_pos_edit = QLineEdit("14.39")
        param_layout.addWidget(self.end_pos_edit, 5, 1)
        
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)
        
        # 创建控制按钮组
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止处理")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # 创建状态显示区域
        status_group = QGroupBox("处理状态")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 20, 15, 15)
        status_layout.setSpacing(10)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Consolas", 9))
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 设置默认文件夹路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.input_folder_edit.setText(os.path.join(project_root, "Data"))
        self.output_folder_edit.setText(os.path.join(project_root, "ProcessedData"))
        
    def browse_input_folder(self):
        """浏览输入文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输入文件夹", self.input_folder_edit.text())
        if folder:
            self.input_folder_edit.setText(folder)
            
    def browse_output_folder(self):
        """浏览输出文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.output_folder_edit.text())
        if folder:
            self.output_folder_edit.setText(folder)
            
    def validate_inputs(self):
        """验证输入参数"""
        try:
            start_row = int(self.start_row_edit.text())
            end_row = int(self.end_row_edit.text())
            start_pos = float(self.start_pos_edit.text())
            end_pos = float(self.end_pos_edit.text())
            
            if start_row >= end_row:
                QMessageBox.warning(self, "参数错误", "起始行号必须小于终止行号")
                return None
                
            if start_pos >= end_pos:
                QMessageBox.warning(self, "参数错误", "起始模头位置必须小于终止模头位置")
                return None
                
            if not os.path.exists(self.input_folder_edit.text()):
                QMessageBox.warning(self, "路径错误", "输入文件夹不存在")
                return None
                
            return {
                'start_row': start_row,
                'end_row': end_row,
                'start_pos': start_pos,
                'end_pos': end_pos
            }
        except ValueError:
            QMessageBox.warning(self, "参数错误", "请输入有效的数字")
            return None
            
    def start_processing(self):
        """开始处理"""
        params = self.validate_inputs()
        if not params:
            return
            
        # 禁用输入控件
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_text.clear()
        
        # 创建并启动处理线程
        self.processor_thread = DataProcessorThread(
            self.input_folder_edit.text(),
            self.output_folder_edit.text(),
            params['start_row'],
            params['end_row'],
            params['start_pos'],
            params['end_pos']
        )
        
        # 连接信号
        self.processor_thread.progress_updated.connect(self.progress_bar.setValue)
        self.processor_thread.status_updated.connect(self.update_status)
        self.processor_thread.finished.connect(self.processing_finished)
        
        # 启动线程
        self.processor_thread.start()
        
    def stop_processing(self):
        """停止处理"""
        if self.processor_thread and self.processor_thread.isRunning():
            self.processor_thread.stop()
            
    def update_status(self, message):
        """更新状态信息"""
        self.status_text.append(message)
        # 自动滚动到底部
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def processing_finished(self, success, message):
        """处理完成"""
        # 启用输入控件
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 显示完成消息
        if success:
            QMessageBox.information(self, "处理完成", message)
        else:
            QMessageBox.warning(self, "处理失败", message)
            
    def init_single_folder_tab(self):
        """初始化单文件夹处理标签页"""
        main_layout = QVBoxLayout(self.single_folder_tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # --- 参数设置组 ---
        param_group = QGroupBox("参数设置")
        param_layout = QGridLayout()
        param_layout.setContentsMargins(15, 20, 15, 15)
        param_layout.setSpacing(12)

        # 文件夹选择
        param_layout.addWidget(QLabel("处理文件夹:"), 0, 0)
        self.sf_folder_edit = QLineEdit()
        self.sf_folder_edit.setReadOnly(True)
        param_layout.addWidget(self.sf_folder_edit, 0, 1)
        sf_folder_btn = QPushButton("浏览...")
        sf_folder_btn.setObjectName("browseButton")
        sf_folder_btn.clicked.connect(self.browse_sf_folder)
        param_layout.addWidget(sf_folder_btn, 0, 2)

        # 输出文件夹
        param_layout.addWidget(QLabel("输出文件夹:"), 1, 0)
        self.sf_output_edit = QLineEdit()
        self.sf_output_edit.setReadOnly(True)
        param_layout.addWidget(self.sf_output_edit, 1, 1)
        sf_output_btn = QPushButton("浏览...")
        sf_output_btn.setObjectName("browseButton")
        sf_output_btn.clicked.connect(self.browse_sf_output)
        param_layout.addWidget(sf_output_btn, 1, 2)

        # 起始行号
        param_layout.addWidget(QLabel("起始行号:"), 2, 0)
        self.sf_start_row = QLineEdit("8")
        param_layout.addWidget(self.sf_start_row, 2, 1)

        # 终止行号
        param_layout.addWidget(QLabel("终止行号:"), 3, 0)
        self.sf_end_row = QLineEdit("190")
        param_layout.addWidget(self.sf_end_row, 3, 1)

        # 起始模头位置
        param_layout.addWidget(QLabel("起始模头位置:"), 4, 0)
        self.sf_start_pos = QLineEdit("2.50")
        param_layout.addWidget(self.sf_start_pos, 4, 1)

        # 终止模头位置
        param_layout.addWidget(QLabel("终止模头位置:"), 5, 0)
        self.sf_end_pos = QLineEdit("14.39")
        param_layout.addWidget(self.sf_end_pos, 5, 1)

        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        # --- 控制按钮 ---
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)

        self.sf_start_btn = QPushButton("开始分析")
        self.sf_start_btn.clicked.connect(self.start_single_folder)
        self.sf_start_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.sf_start_btn)

        self.sf_stop_btn = QPushButton("停止分析")
        self.sf_stop_btn.setObjectName("stopButton")
        self.sf_stop_btn.clicked.connect(self.stop_single_folder)
        self.sf_stop_btn.setEnabled(False)
        control_layout.addWidget(self.sf_stop_btn)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        # --- 进度条 ---
        self.sf_progress = QProgressBar()
        main_layout.addWidget(self.sf_progress)

        # --- 图像显示区域 ---
        image_group = QGroupBox("热力云图")
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(5, 5, 5, 5)

        self.sf_scroll = QScrollArea()
        self.sf_scroll.setWidgetResizable(True)
        self.sf_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sf_scroll.setMinimumHeight(300)

        self.sf_image_label = QLabel()
        self.sf_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sf_image_label.setText("请选择文件夹并开始分析")
        self.sf_image_label.setStyleSheet(
            "QLabel { background-color: rgba(255,255,255,0.5);"
            " border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; }")
        self.sf_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.sf_image_label.setMinimumSize(1, 1)
        self.sf_original_pixmap = None
        self.sf_is_zoomed = False
        self.sf_image_label.mouseDoubleClickEvent = self._sf_image_double_click

        self.sf_scroll.setWidget(self.sf_image_label)
        image_layout.addWidget(self.sf_scroll)
        image_group.setLayout(image_layout)
        image_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(image_group, 1)

        # 放大模式控制按钮
        sf_zoom_ctrl = QHBoxLayout()
        sf_zoom_ctrl.setSpacing(8)
        self.sf_zoom_mode_btn = QPushButton("🔍 放大模式")
        self.sf_zoom_mode_btn.setToolTip("进入放大模式后，在图片上拖拽选中区域即可局部放大")
        self.sf_zoom_mode_btn.clicked.connect(self._sf_toggle_zoom_mode)
        sf_zoom_ctrl.addWidget(self.sf_zoom_mode_btn)
        self.sf_restore_btn = QPushButton("↩ 还原")
        self.sf_restore_btn.setToolTip("还原到原始视图")
        self.sf_restore_btn.clicked.connect(self._sf_restore_zoom)
        self.sf_restore_btn.hide()
        sf_zoom_ctrl.addWidget(self.sf_restore_btn)
        sf_zoom_ctrl.addStretch()
        main_layout.addLayout(sf_zoom_ctrl)

        # --- 状态显示 ---
        status_group = QGroupBox("处理状态")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 20, 15, 15)

        self.sf_status = QTextEdit()
        self.sf_status.setReadOnly(True)
        self.sf_status.setFont(QFont("Consolas", 9))
        self.sf_status.setMaximumHeight(120)
        status_layout.addWidget(self.sf_status)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 默认路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sf_output_edit.setText(os.path.join(project_root, "ProcessedData"))

    def browse_sf_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择要处理的文件夹", "")
        if folder:
            self.sf_folder_edit.setText(folder)

    def browse_sf_output(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹", self.sf_output_edit.text())
        if folder:
            self.sf_output_edit.setText(folder)

    def _validate_sf_params(self):
        try:
            start_row = int(self.sf_start_row.text())
            end_row = int(self.sf_end_row.text())
            start_pos = float(self.sf_start_pos.text())
            end_pos = float(self.sf_end_pos.text())
            if start_row >= end_row:
                QMessageBox.warning(self, "参数错误", "起始行号必须小于终止行号")
                return None
            if start_pos >= end_pos:
                QMessageBox.warning(self, "参数错误", "起始模头位置必须小于终止模头位置")
                return None
            if not os.path.isdir(self.sf_folder_edit.text()):
                QMessageBox.warning(self, "路径错误", "请选择有效的处理文件夹")
                return None
            return dict(start_row=start_row, end_row=end_row,
                        start_pos=start_pos, end_pos=end_pos)
        except ValueError:
            QMessageBox.warning(self, "参数错误", "请输入有效的数字")
            return None

    def start_single_folder(self):
        params = self._validate_sf_params()
        if not params:
            return

        self.sf_start_btn.setEnabled(False)
        self.sf_stop_btn.setEnabled(True)
        self.sf_progress.setValue(0)
        self.sf_status.clear()

        self.single_folder_thread = SingleFolderProcessorThread(
            self.sf_folder_edit.text(),
            self.sf_output_edit.text(),
            params['start_row'], params['end_row'],
            params['start_pos'], params['end_pos']
        )
        self.single_folder_thread.progress_updated.connect(self.sf_progress.setValue)
        self.single_folder_thread.status_updated.connect(self._sf_update_status)
        self.single_folder_thread.image_ready.connect(self._sf_display_image)
        self.single_folder_thread.finished.connect(self._sf_finished)
        self.single_folder_thread.start()

    def stop_single_folder(self):
        if self.single_folder_thread and self.single_folder_thread.isRunning():
            self.single_folder_thread.stop()

    def _sf_update_status(self, message):
        self.sf_status.append(message)
        sb = self.sf_status.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _sf_display_image(self, image_path, title):
        self._sf_current_image_path = image_path
        self._sf_current_title = title
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.sf_status.append("无法加载图像")
            return
        self.sf_original_pixmap = pixmap
        self.sf_is_zoomed = False
        self._sf_zoom_history.clear()
        self.sf_restore_btn.hide()
        self._sf_scale_image(pixmap)
        self.sf_image_label.setText("")
        self.sf_status.append("提示: 双击图片可在全功能查看器中打开")
        self.sf_status.append("提示: 点击「🔍 放大模式」可在图上框选区域局部放大")

    def _sf_scale_image(self, pixmap):
        w = self.sf_scroll.width() - 10
        h = self.sf_scroll.height() - 10
        if w <= 10:
            w = 600
        if h <= 10:
            h = 400
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.sf_image_label.setPixmap(scaled)

    def _sf_image_double_click(self, event):
        """双击 — 在全功能查看器中打开；放大模式中则还原"""
        if not self.sf_original_pixmap:
            return
        if self._sf_zoom_mode:
            self._sf_restore_zoom()
            return
        try:
            self._sf_viewer = ImageViewerWindow(
                self._sf_current_image_path, getattr(self, '_sf_current_title', ''), self)
            self._sf_viewer.show()
        except Exception as e:
            self.sf_status.append(f"打开图片查看器失败: {e}")

    def _sf_finished(self, success, message):
        self.sf_start_btn.setEnabled(True)
        self.sf_stop_btn.setEnabled(False)
        if success:
            QMessageBox.information(self, "分析完成", message)
        else:
            QMessageBox.warning(self, "分析失败", message)

    # ========== 单文件夹放大模式 ==========

    def _sf_toggle_zoom_mode(self):
        self._sf_zoom_mode = not self._sf_zoom_mode
        if self._sf_zoom_mode:
            self.sf_zoom_mode_btn.setText("✕ 退出放大")
            self.sf_zoom_mode_btn.setStyleSheet(
                "QPushButton { background: #f43f5e; color: white; font-weight: 700; }")
            self.sf_image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.sf_image_label.installEventFilter(self)
            self.sf_status.append("放大模式已开启：在图片上拖拽鼠标选择区域进行局部放大")
        else:
            self._sf_exit_zoom_mode()

    def _sf_exit_zoom_mode(self):
        self._sf_zoom_mode = False
        self.sf_zoom_mode_btn.setText("🔍 放大模式")
        self.sf_zoom_mode_btn.setStyleSheet("")
        self.sf_image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.sf_image_label.removeEventFilter(self)
        self._sf_clear_rubber_band()
        self.sf_restore_btn.hide()
        if self.sf_original_pixmap:
            self._sf_zoom_history.clear()
            self.sf_is_zoomed = False
            self.sf_image_label.setMinimumSize(1, 1)
            self._sf_scale_image(self.sf_original_pixmap)

    def _sf_restore_zoom(self):
        if self._sf_zoom_history:
            self._sf_zoom_history.pop()
        if self._sf_zoom_history:
            prev = self._sf_zoom_history[-1]
            scaled = prev.scaled(self.sf_image_label.size(),
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            self.sf_image_label.setPixmap(scaled)
        else:
            self.sf_restore_btn.hide()
            if self.sf_original_pixmap:
                self.sf_image_label.setMinimumSize(1, 1)
                self._sf_scale_image(self.sf_original_pixmap)
        if not self._sf_zoom_history:
            self.sf_restore_btn.hide()

    def _sf_clear_rubber_band(self):
        if self._sf_rubber_band:
            self._sf_rubber_band.hide()
            self._sf_rubber_band = None
        self._sf_rubber_origin = None

    def _sf_zoom_to_region(self, label_rect: QRect):
        if not self.sf_original_pixmap:
            return
        current_pixmap = self.sf_image_label.pixmap()
        if not current_pixmap:
            return
        label_size = self.sf_image_label.size()
        pixmap_rect = current_pixmap.rect()
        offset_x = (label_size.width() - pixmap_rect.width()) // 2
        offset_y = (label_size.height() - pixmap_rect.height()) // 2
        px = max(0, label_rect.x() - offset_x)
        py = max(0, label_rect.y() - offset_y)
        pw = min(label_rect.width(), pixmap_rect.width() - px)
        ph = min(label_rect.height(), pixmap_rect.height() - py)
        if pw <= 0 or ph <= 0:
            return
        scale_x = self.sf_original_pixmap.width() / pixmap_rect.width()
        scale_y = self.sf_original_pixmap.height() / pixmap_rect.height()
        orig_x = int(px * scale_x)
        orig_y = int(py * scale_y)
        orig_w = max(1, min(int(pw * scale_x), self.sf_original_pixmap.width() - orig_x))
        orig_h = max(1, min(int(ph * scale_y), self.sf_original_pixmap.height() - orig_y))
        cropped = self.sf_original_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        zoomed = cropped.scaled(label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        self._sf_zoom_history.append(current_pixmap)
        self.sf_image_label.setPixmap(zoomed)
        self.sf_restore_btn.show()
        self.sf_status.append(f"已放大区域: ({orig_x},{orig_y}) {orig_w}×{orig_h}")

    # ==================== 文件夹监控标签页 ====================
    def init_monitor_tab(self):
        """初始化文件夹监控标签页"""
        main_layout = QVBoxLayout(self.monitor_tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- 参数设置组 ---
        param_group = QGroupBox("参数设置")
        param_layout = QGridLayout()
        param_layout.setContentsMargins(15, 20, 15, 15)
        param_layout.setSpacing(10)

        # 监控文件夹
        param_layout.addWidget(QLabel("监控文件夹:"), 0, 0)
        self.mf_folder_edit = QLineEdit()
        self.mf_folder_edit.setReadOnly(True)
        param_layout.addWidget(self.mf_folder_edit, 0, 1)
        mf_folder_btn = QPushButton("浏览...")
        mf_folder_btn.setObjectName("browseButton")
        mf_folder_btn.clicked.connect(self.browse_mf_folder)
        param_layout.addWidget(mf_folder_btn, 0, 2)

        # 输出文件夹（临时处理结果）
        param_layout.addWidget(QLabel("输出文件夹:"), 1, 0)
        self.mf_output_edit = QLineEdit()
        self.mf_output_edit.setReadOnly(True)
        param_layout.addWidget(self.mf_output_edit, 1, 1)
        mf_output_btn = QPushButton("浏览...")
        mf_output_btn.setObjectName("browseButton")
        mf_output_btn.clicked.connect(self.browse_mf_output)
        param_layout.addWidget(mf_output_btn, 1, 2)

        # 保存文件夹（父目录切换时自动存档）
        param_layout.addWidget(QLabel("存档文件夹:"), 2, 0)
        self.mf_save_edit = QLineEdit()
        self.mf_save_edit.setReadOnly(True)
        param_layout.addWidget(self.mf_save_edit, 2, 1)
        mf_save_btn = QPushButton("浏览...")
        mf_save_btn.setObjectName("browseButton")
        mf_save_btn.clicked.connect(self.browse_mf_save)
        param_layout.addWidget(mf_save_btn, 2, 2)

        # 忽略文件夹名（逗号分隔，不监控这些名称的子文件夹）
        param_layout.addWidget(QLabel("忽略文件夹:"), 3, 0)
        self.mf_ignore_edit = QLineEdit("定量_Roll, 定量_RollTrend")
        self.mf_ignore_edit.setPlaceholderText("逗号分隔的文件夹名，如：定量_Roll, 定量_RollTrend")
        param_layout.addWidget(self.mf_ignore_edit, 3, 1, 1, 3)

        # 起始行号 / 终止行号
        param_layout.addWidget(QLabel("起始行号:"), 4, 0)
        self.mf_start_row = QLineEdit("8")
        param_layout.addWidget(self.mf_start_row, 4, 1)
        param_layout.addWidget(QLabel("终止行号:"), 4, 2)
        self.mf_end_row = QLineEdit("190")
        param_layout.addWidget(self.mf_end_row, 4, 3)

        # 起始模头位置 / 终止模头位置
        param_layout.addWidget(QLabel("起始模头位置:"), 5, 0)
        self.mf_start_pos = QLineEdit("2.50")
        param_layout.addWidget(self.mf_start_pos, 5, 1)
        param_layout.addWidget(QLabel("终止模头位置:"), 5, 2)
        self.mf_end_pos = QLineEdit("14.39")
        param_layout.addWidget(self.mf_end_pos, 5, 3)

        # 每日零点自动切换
        self.mf_auto_switch_cb = QCheckBox("每日零点自动切换")
        self.mf_auto_switch_cb.setToolTip("启用后，每日零点自动将监控文件夹切换为当天日期对应的子文件夹")
        self.mf_auto_switch_cb.stateChanged.connect(self._on_auto_switch_toggled)
        param_layout.addWidget(self.mf_auto_switch_cb, 6, 0)
        param_layout.addWidget(QLabel("CustomProfile路径:"), 6, 1)
        self.mf_customprofile_edit = QLineEdit()
        self.mf_customprofile_edit.setPlaceholderText("D:\\...\\Data\\CustomProfile")
        self.mf_customprofile_edit.setEnabled(False)
        param_layout.addWidget(self.mf_customprofile_edit, 6, 2)
        btn_cp = QPushButton("浏览...")
        btn_cp.setObjectName("browseButton")
        btn_cp.clicked.connect(self.browse_mf_customprofile)
        btn_cp.setEnabled(False)
        self._btn_cp_browse = btn_cp
        param_layout.addWidget(btn_cp, 6, 3)

        # 自动跟随最新文件夹（独立于零点切换）
        self.mf_auto_follow_cb = QCheckBox("自动跟随最新文件夹")
        self.mf_auto_follow_cb.setToolTip(
            "启用后，定时扫描磁盘上的最新日期文件夹并自动切换监控目标；\n"
            "关闭则始终监控下方设置的固定文件夹，不会自动跳转")
        self.mf_auto_follow_cb.stateChanged.connect(self._on_auto_switch_toggled)
        param_layout.addWidget(self.mf_auto_follow_cb, 7, 0, 1, 4)

        # 异常标记 & 备注
        param_layout.addWidget(QLabel("是否异常:"), 8, 0)
        self.mf_abnormal_cb = QCheckBox("标记为异常")
        param_layout.addWidget(self.mf_abnormal_cb, 8, 1)
        param_layout.addWidget(QLabel("备注:"), 8, 2)
        self.mf_remarks_edit = QLineEdit()
        self.mf_remarks_edit.setPlaceholderText("可选备注信息...")
        param_layout.addWidget(self.mf_remarks_edit, 8, 3)

        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)

        # --- 控制按钮行 ---
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(12)

        self.mf_start_btn = QPushButton("开始监控")
        self.mf_start_btn.clicked.connect(self.start_monitoring)
        self.mf_start_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        ctrl_layout.addWidget(self.mf_start_btn)

        self.mf_stop_btn = QPushButton("停止监控")
        self.mf_stop_btn.setObjectName("stopButton")
        self.mf_stop_btn.clicked.connect(self.stop_monitoring)
        self.mf_stop_btn.setEnabled(False)
        ctrl_layout.addWidget(self.mf_stop_btn)

        self.mf_save_btn = QPushButton("手动存档")
        self.mf_save_btn.clicked.connect(self._monitor_manual_save)
        self.mf_save_btn.setEnabled(False)
        ctrl_layout.addWidget(self.mf_save_btn)

        self.mf_test_midnight_btn = QPushButton("模拟零点切换")
        self.mf_test_midnight_btn.setToolTip("手动触发零点切换逻辑（用于测试），将监控切换到当前日期对应的文件夹")
        self.mf_test_midnight_btn.clicked.connect(self._test_midnight_switch)
        self.mf_test_midnight_btn.setEnabled(False)
        ctrl_layout.addWidget(self.mf_test_midnight_btn)

        ctrl_layout.addStretch()
        main_layout.addLayout(ctrl_layout)

        # --- 进度条 ---
        self.mf_progress = QProgressBar()
        main_layout.addWidget(self.mf_progress)

        # --- 图像显示区域 ---
        img_group = QGroupBox("实时热力云图")
        img_layout = QVBoxLayout()
        img_layout.setContentsMargins(5, 5, 5, 5)

        self.mf_scroll = QScrollArea()
        self.mf_scroll.setWidgetResizable(True)
        self.mf_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.mf_scroll.setMinimumHeight(280)

        self.mf_image_label = QLabel()
        self.mf_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mf_image_label.setText("等待监控启动...")
        self.mf_image_label.setStyleSheet(
            "QLabel { background-color: rgba(255,255,255,0.5);"
            " border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; }")
        self.mf_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.mf_image_label.setMinimumSize(1, 1)
        self._mf_original_pixmap = None
        self._mf_is_zoomed = False
        self.mf_image_label.mouseDoubleClickEvent = self._mf_image_double_click

        self.mf_scroll.setWidget(self.mf_image_label)
        img_layout.addWidget(self.mf_scroll)
        img_group.setLayout(img_layout)
        img_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(img_group, 1)

        # 放大模式控制按钮
        mf_zoom_ctrl = QHBoxLayout()
        mf_zoom_ctrl.setSpacing(8)
        self.mf_zoom_mode_btn = QPushButton("🔍 放大模式")
        self.mf_zoom_mode_btn.setToolTip("进入放大模式后，在图片上拖拽选中区域即可局部放大")
        self.mf_zoom_mode_btn.clicked.connect(self._mf_toggle_zoom_mode)
        mf_zoom_ctrl.addWidget(self.mf_zoom_mode_btn)
        self.mf_restore_btn = QPushButton("↩ 还原")
        self.mf_restore_btn.setToolTip("还原到原始视图")
        self.mf_restore_btn.clicked.connect(self._mf_restore_zoom)
        self.mf_restore_btn.hide()
        mf_zoom_ctrl.addWidget(self.mf_restore_btn)
        mf_zoom_ctrl.addStretch()
        main_layout.addLayout(mf_zoom_ctrl)

        # --- 状态显示 ---
        status_group = QGroupBox("监控日志")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 20, 15, 15)

        self.mf_status = QTextEdit()
        self.mf_status.setReadOnly(True)
        self.mf_status.setFont(QFont("Consolas", 9))
        self.mf_status.setMaximumHeight(100)
        status_layout.addWidget(self.mf_status)

        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 默认路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mf_output_edit.setText(os.path.join(project_root, "ProcessedData"))
        self.mf_save_edit.setText(os.path.join(project_root, "SavedResults"))

    # --- 文件夹浏览 ---
    def browse_mf_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择要监控的文件夹", "")
        if folder:
            self.mf_folder_edit.setText(folder)

    def browse_mf_output(self):
        folder = QFileDialog.getExistingDirectory(self, "选择临时输出文件夹", self.mf_output_edit.text())
        if folder:
            self.mf_output_edit.setText(folder)

    def browse_mf_save(self):
        folder = QFileDialog.getExistingDirectory(self, "选择存档文件夹", self.mf_save_edit.text())
        if folder:
            self.mf_save_edit.setText(folder)

    # --- 参数校验 ---
    def _validate_mf_params(self):
        try:
            start_row = int(self.mf_start_row.text())
            end_row = int(self.mf_end_row.text())
            start_pos = float(self.mf_start_pos.text())
            end_pos = float(self.mf_end_pos.text())
            if start_row >= end_row:
                QMessageBox.warning(self, "参数错误", "起始行号必须小于终止行号")
                return None
            if start_pos >= end_pos:
                QMessageBox.warning(self, "参数错误", "起始模头位置必须小于终止模头位置")
                return None
            if not os.path.isdir(self.mf_folder_edit.text()):
                if self.mf_auto_switch_cb.isChecked() or self.mf_auto_follow_cb.isChecked():
                    # 自动模式下，日期文件夹可能尚未创建，尝试自动创建
                    try:
                        os.makedirs(self.mf_folder_edit.text(), exist_ok=True)
                    except OSError:
                        QMessageBox.warning(self, "路径错误",
                                            f"无法创建监控文件夹: {self.mf_folder_edit.text()}")
                        return None
                else:
                    QMessageBox.warning(self, "路径错误", "请选择有效的监控文件夹")
                    return None
            return dict(start_row=start_row, end_row=end_row,
                        start_pos=start_pos, end_pos=end_pos)
        except ValueError:
            QMessageBox.warning(self, "参数错误", "请输入有效的数字")
            return None

    # --- 启动 / 停止监控 ---
    def start_monitoring(self):
        # 如果启用了自动切换或自动跟随，将监控文件夹设为当天日期路径
        if self.mf_auto_switch_cb.isChecked() or self.mf_auto_follow_cb.isChecked():
            base = self.mf_customprofile_edit.text().strip()
            if not base:
                QMessageBox.warning(self, "路径错误", "请先设置CustomProfile路径")
                return
            today_path = self._build_date_folder()
            if not today_path:
                QMessageBox.warning(self, "路径错误", "无法构建日期路径，请检查CustomProfile路径设置")
                return
            if not os.path.isdir(today_path):
                latest = self._find_latest_date_folder(base)
                if latest:
                    self._mf_append_log(f"当天路径不存在，使用最新日期文件夹: {latest}")
                    self.mf_folder_edit.setText(latest)
                else:
                    os.makedirs(today_path, exist_ok=True)
                    self.mf_folder_edit.setText(today_path)
            else:
                self.mf_folder_edit.setText(today_path)

        params = self._validate_mf_params()
        if not params:
            return

        self._monitor_params = params
        self._monitor_queue.clear()
        self._monitor_busy = False
        self._monitor_current_csv = None
        self._monitor_current_image = None
        self._monitor_current_parent = None

        self.mf_start_btn.setEnabled(False)
        self.mf_stop_btn.setEnabled(True)
        self.mf_save_btn.setEnabled(False)
        self.mf_test_midnight_btn.setEnabled(
            self.mf_auto_switch_cb.isChecked() or self.mf_auto_follow_cb.isChecked())
        self.mf_progress.setValue(0)
        self.mf_status.clear()

        # 确保输出和存档目录存在
        os.makedirs(self.mf_output_edit.text(), exist_ok=True)
        os.makedirs(self.mf_save_edit.text(), exist_ok=True)

        # 解析忽略文件夹名
        raw = self.mf_ignore_edit.text().strip()
        ignore_names = {name.strip() for name in raw.split(',') if name.strip()} if raw else set()
        if ignore_names:
            self._mf_append_log(f"忽略文件夹: {ignore_names}")

        # 创建 MonitorCore 并连接信号
        self._monitor_core = MonitorCore(ignore_dir_names=ignore_names)
        self._monitor_core.same_parent_detected.connect(self._on_monitor_same_parent)
        self._monitor_core.different_parent_detected.connect(self._on_monitor_different_parent)
        self._monitor_core.status_changed.connect(self._mf_append_log)
        self._monitor_core.start_monitoring(self.mf_folder_edit.text())

        # 启动午夜定时器
        if self.mf_auto_switch_cb.isChecked():
            self._start_midnight_timer()

        self._mf_append_log(f"开始监控: {self.mf_folder_edit.text()}")

    def stop_monitoring(self):
        if self._monitor_core:
            self._monitor_core.stop_monitoring()
            self._monitor_core = None
        if self._monitor_thread and self._monitor_thread.isRunning():
            self._monitor_thread.stop()
            self._monitor_thread = None
        self._monitor_queue.clear()
        self._monitor_busy = False
        self._stop_midnight_timer()

        self.mf_start_btn.setEnabled(True)
        self.mf_stop_btn.setEnabled(False)
        self.mf_test_midnight_btn.setEnabled(False)
        self.mf_progress.setValue(0)
        self._mf_append_log("监控已停止")

    # --- 每日零点自动切换 ---
    def browse_mf_customprofile(self):
        folder = QFileDialog.getExistingDirectory(self, "选择CustomProfile文件夹", self.mf_customprofile_edit.text())
        if folder:
            self.mf_customprofile_edit.setText(folder)

    def _on_auto_switch_toggled(self, checked):
        self._sync_customprofile_state()
        # 如果监控已在运行，同步定时器状态
        self._sync_midnight_timer()

    def _sync_customprofile_state(self):
        """当任一自动功能启用时，需要CustomProfile路径"""
        need_cp = self.mf_auto_switch_cb.isChecked() or self.mf_auto_follow_cb.isChecked()
        self.mf_customprofile_edit.setEnabled(need_cp)
        self._btn_cp_browse.setEnabled(need_cp)
        if need_cp and not self.mf_customprofile_edit.text():
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_cp = os.path.join(project_root, "Data", "CustomProfile")
            if os.path.isdir(default_cp):
                self.mf_customprofile_edit.setText(default_cp)

    def _sync_midnight_timer(self):
        """根据复选框状态决定是否启停午夜定时器"""
        need_timer = self.mf_auto_switch_cb.isChecked() or self.mf_auto_follow_cb.isChecked()
        if self._monitor_core and self._monitor_core.is_monitoring():
            if need_timer:
                if not self._midnight_timer or not self._midnight_timer.isActive():
                    self._start_midnight_timer()
                self.mf_test_midnight_btn.setEnabled(True)
            else:
                self._stop_midnight_timer()
                self.mf_test_midnight_btn.setEnabled(False)

    def _build_date_folder(self) -> str | None:
        """根据当前日期构建文件夹路径：{CustomProfile}/{year}_{month}/{day}"""
        base = self.mf_customprofile_edit.text().strip()
        if not base:
            return None
        from datetime import datetime
        now = datetime.now()
        date_folder = os.path.join(base, f"{now.year}_{now.month:02d}", f"{now.day:02d}")
        return date_folder

    def _find_latest_date_folder(self, base_path: str) -> str | None:
        """扫描 base_path 下匹配 YYYY_MM/DD 模式的最新日期文件夹"""
        import re
        if not base_path or not os.path.isdir(base_path):
            return None
        pattern = re.compile(r'^\d{4}_\d{2}$')
        latest = None
        latest_date = None
        try:
            for year_month in os.listdir(base_path):
                ym_path = os.path.join(base_path, year_month)
                if not pattern.match(year_month) or not os.path.isdir(ym_path):
                    continue
                for day_name in os.listdir(ym_path):
                    day_path = os.path.join(ym_path, day_name)
                    if day_name.isdigit() and len(day_name) == 2 and os.path.isdir(day_path):
                        try:
                            parts = year_month.split('_')
                            from datetime import datetime
                            d = datetime(int(parts[0]), int(parts[1]), int(day_name))
                            if latest_date is None or d > latest_date:
                                latest_date = d
                                latest = day_path
                        except ValueError:
                            continue
        except OSError:
            pass
        return latest

    def _start_midnight_timer(self):
        """启动午夜检查定时器（每30秒检查一次是否跨天）"""
        self._stop_midnight_timer()
        from datetime import datetime
        self._last_midnight_date = datetime.now().strftime("%Y%m%d")
        self._midnight_timer = QTimer()
        self._midnight_timer.timeout.connect(self._check_midnight)
        self._midnight_timer.start(30000)  # 每30秒检查
        self._mf_append_log(f"每日零点切换已启用 (CustomProfile: {self.mf_customprofile_edit.text()})")

    def _stop_midnight_timer(self):
        if self._midnight_timer:
            self._midnight_timer.stop()
            self._midnight_timer = None
        self._last_midnight_date = None

    def _check_midnight(self):
        """检查是否已跨天（零点自动切换），以及磁盘扫描（自动跟随最新文件夹）。"""
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        switched = False

        # 零点切换：由"每日零点自动切换"控制
        if self._last_midnight_date and today != self._last_midnight_date \
                and self.mf_auto_switch_cb.isChecked():
            self._mf_append_log(f"========== 零点触发 ==========")
            self._mf_append_log(f"日期变更: {self._last_midnight_date} -> {today}")
            self._switch_to_today_folder()
            switched = True
        self._last_midnight_date = today

        # 磁盘扫描：由"自动跟随最新文件夹"控制
        if not switched and self.mf_auto_follow_cb.isChecked():
            base = self.mf_customprofile_edit.text().strip()
            if base and os.path.isdir(base):
                latest = self._find_latest_date_folder(base)
                if latest and self._monitor_core and self._monitor_core.monitor_root \
                        and os.path.abspath(latest) != os.path.abspath(self._monitor_core.monitor_root):
                    self._mf_append_log(f"========== 检测到磁盘新日期文件夹 ==========")
                    self._mf_append_log(f"切换至: {latest}")
                    self._switch_to_today_folder(target_path=latest)

    def _switch_to_today_folder(self, target_path: str | None = None):
        """切换到目标日期文件夹并重启监控。"""
        if target_path is None:
            target_path = self._build_date_folder()
        if not target_path:
            self._mf_append_log("[零点切换失败] 无法构建日期路径")
            return

        self._mf_append_log(f"切换监控文件夹: {target_path}")

        # 如果目标文件夹不存在，自动创建
        if not os.path.isdir(target_path):
            try:
                os.makedirs(target_path, exist_ok=True)
                self._mf_append_log(f"目标文件夹不存在，已自动创建: {target_path}")
            except OSError as e:
                self._mf_append_log(f"[零点切换失败] 无法创建目标文件夹: {e}")
                return

        # 先存档当前批次，防止数据丢失
        self._auto_save_previous()

        # 等待正在处理的线程完成
        if self._monitor_thread and self._monitor_thread.isRunning():
            self._mf_append_log("等待当前处理完成...")
            self._monitor_thread.wait(10000)  # 最多等10秒

        # 停止当前监控
        old_monitor = self._monitor_core
        if old_monitor:
            old_monitor.same_parent_detected.disconnect()
            old_monitor.different_parent_detected.disconnect()
            old_monitor.status_changed.disconnect()
            old_monitor.stop_monitoring()

        self._monitor_queue.clear()
        self._monitor_busy = False
        self._monitor_current_csv = None
        self._monitor_current_image = None
        self._monitor_current_parent = None

        # 更新路径
        self.mf_folder_edit.setText(target_path)
        self.mf_progress.setValue(0)

        # 重新启动监控
        raw = self.mf_ignore_edit.text().strip()
        ignore_names = {name.strip() for name in raw.split(',') if name.strip()} if raw else set()

        self._monitor_core = MonitorCore(ignore_dir_names=ignore_names)
        self._monitor_core.same_parent_detected.connect(self._on_monitor_same_parent)
        self._monitor_core.different_parent_detected.connect(self._on_monitor_different_parent)
        self._monitor_core.status_changed.connect(self._mf_append_log)
        self._monitor_core.start_monitoring(target_path)

        self._mf_append_log(f"零点切换完成，正在监控: {target_path}")

    def _test_midnight_switch(self):
        """手动触发零点切换（测试用）。
        优先扫描磁盘上最新日期文件夹，否则使用当天日期。"""
        if not self._monitor_core:
            QMessageBox.warning(self, "未监控", "请先启动监控")
            return
        if not self.mf_auto_switch_cb.isChecked() and not self.mf_auto_follow_cb.isChecked():
            QMessageBox.warning(self, "未启用",
                               '请先勾选"每日零点自动切换"或"自动跟随最新文件夹"')
            return

        base = self.mf_customprofile_edit.text().strip()
        target = self._find_latest_date_folder(base) or self._build_date_folder()
        if not target:
            QMessageBox.warning(self, "错误", "无法确定目标日期文件夹")
            return

        reply = QMessageBox.question(
            self, "确认切换",
            f"将模拟零点切换：停止当前监控并切换到：\n{target}\n\n确定要执行吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._mf_append_log("========== [测试] 手动触发零点切换 ==========")
        self._switch_to_today_folder(target_path=target)

    # --- MonitorCore 信号处理 ---
    def _on_monitor_same_parent(self, parent_dir: str, filename: str):
        """CSV出现在与上次相同的父目录 -> 直接处理，不存档"""
        self._mf_append_log(f"[相同父目录] {os.path.basename(parent_dir)}/{filename}")
        self._enqueue_or_process(parent_dir, is_same_parent=True)

    def _on_monitor_different_parent(self, parent_dir: str, filename: str):
        """CSV出现在与上次不同的父目录 -> 先存档上一批，再处理新的"""
        self._mf_append_log(f"[不同父目录] {os.path.basename(parent_dir)}/{filename}")
        self._enqueue_or_process(parent_dir, is_same_parent=False)

    def _enqueue_or_process(self, parent_dir: str, is_same_parent: bool):
        """将处理请求入队，或在空闲时直接处理"""
        # 如果是同一父目录且已在队列中，跳过重复
        for q_dir, q_same in self._monitor_queue:
            if q_dir == parent_dir:
                return

        if self._monitor_busy:
            self._monitor_queue.append((parent_dir, is_same_parent))
            self._mf_append_log(f"  处理中，已加入队列: {os.path.basename(parent_dir)}")
        else:
            self._run_monitor_process(parent_dir, is_same_parent)

    # --- 执行单文件夹处理 ---
    def _run_monitor_process(self, parent_dir: str, is_same_parent: bool):
        """对指定父目录执行合并+热力图生成"""
        self._monitor_busy = True
        self._monitor_current_parent = parent_dir

        # 如果不是同一父目录，先存档上一批结果
        if not is_same_parent:
            self._auto_save_previous()

        params = self._monitor_params
        self._monitor_thread = SingleFolderProcessorThread(
            parent_dir,
            self.mf_output_edit.text(),
            params['start_row'], params['end_row'],
            params['start_pos'], params['end_pos']
        )
        self._monitor_thread.progress_updated.connect(self.mf_progress.setValue)
        self._monitor_thread.status_updated.connect(self._mf_append_log)
        self._monitor_thread.image_ready.connect(self._mf_display_image)
        self._monitor_thread.finished.connect(self._monitor_process_finished)
        self._monitor_thread.start()

    # --- 自动存档 ---
    def _auto_save_previous(self):
        """将上一批处理结果自动保存到存档文件夹，并写入历史数据库"""
        csv_path = self._monitor_current_csv
        img_path = self._monitor_current_image
        if not csv_path or not img_path:
            return
        if not os.path.exists(csv_path) or not os.path.exists(img_path):
            return
        save_dir = self.mf_save_edit.text()
        if not save_dir:
            return
        try:
            target, dst_csv, dst_img = MonitorCore.save_results(csv_path, img_path, save_dir)
            is_abnormal = 1 if self.mf_abnormal_cb.isChecked() else 0
            remarks = self.mf_remarks_edit.text().strip()
            insert_record(dst_csv, dst_img, target, is_abnormal=is_abnormal, remarks=remarks)
            self._mf_append_log(f"[自动存档] 已保存到: {target}")
            # 清空异常标记和备注
            self.mf_abnormal_cb.setChecked(False)
            self.mf_remarks_edit.clear()
        except Exception as e:
            self._mf_append_log(f"[自动存档失败] {e}")

    # --- 处理完成回调 ---
    def _monitor_process_finished(self, success: bool, message: str):
        """单次处理完成后的回调"""
        self._monitor_busy = False

        if success:
            self.mf_save_btn.setEnabled(True)

        self._mf_append_log(message)

        # 处理队列中的下一个
        if self._monitor_queue:
            next_parent, next_same = self._monitor_queue.pop(0)
            self._mf_append_log(f"处理队列中的: {os.path.basename(next_parent)}")
            self._run_monitor_process(next_parent, next_same)

    # --- 图像显示 ---
    def _mf_display_image(self, image_path: str, title: str):
        """在监控标签页显示热力云图"""
        self._monitor_current_image = image_path
        self._mf_current_image_path = image_path

        if self._monitor_thread:
            folder_name = os.path.basename(self._monitor_current_parent or "")
            csv_path = os.path.join(self.mf_output_edit.text(), f"merged_{folder_name}.csv")
            if os.path.exists(csv_path):
                self._monitor_current_csv = csv_path

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self._mf_append_log("无法加载热力图图像")
            return
        self._mf_original_pixmap = pixmap
        self._mf_is_zoomed = False
        self._mf_zoom_history.clear()
        self.mf_restore_btn.hide()
        self._mf_scale_image(pixmap)
        self.mf_image_label.setText("")

    def _mf_scale_image(self, pixmap):
        w = self.mf_scroll.width() - 10
        h = self.mf_scroll.height() - 10
        if w <= 10:
            w = 600
        if h <= 10:
            h = 350
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.mf_image_label.setPixmap(scaled)

    def _mf_image_double_click(self, event):
        """双击 — 在全功能查看器中打开；放大模式中则还原"""
        if not self._mf_original_pixmap:
            return
        if self._mf_zoom_mode:
            self._mf_restore_zoom()
            return
        try:
            self._mf_viewer = ImageViewerWindow(
                self._mf_current_image_path, '', self)
            self._mf_viewer.show()
        except Exception as e:
            self._mf_append_log(f"打开图片查看器失败: {e}")

    # --- 手动存档 ---
    def _monitor_manual_save(self):
        """手动将当前显示的云图和数据保存"""
        csv_path = self._monitor_current_csv
        img_path = self._monitor_current_image
        if not csv_path or not os.path.exists(csv_path):
            QMessageBox.warning(self, "无数据", "当前没有可保存的处理结果")
            return
        if not img_path or not os.path.exists(img_path):
            QMessageBox.warning(self, "无图像", "当前没有可保存的热力图")
            return

        save_dir = self.mf_save_edit.text()
        if not save_dir:
            QMessageBox.warning(self, "路径错误", "请先设置存档文件夹")
            return

        try:
            target, dst_csv, dst_img = MonitorCore.save_results(csv_path, img_path, save_dir)
            is_abnormal = 1 if self.mf_abnormal_cb.isChecked() else 0
            remarks = self.mf_remarks_edit.text().strip()
            insert_record(dst_csv, dst_img, target, is_abnormal=is_abnormal, remarks=remarks)
            self._mf_append_log(f"[手动存档] 已保存到: {target}")
            # 清空异常标记和备注
            self.mf_abnormal_cb.setChecked(False)
            self.mf_remarks_edit.clear()
            QMessageBox.information(self, "存档完成",
                                    f"已保存到:\n{target}\n\nCSV: {os.path.basename(dst_csv)}\n云图: {os.path.basename(dst_img)}")
        except Exception as e:
            QMessageBox.warning(self, "存档失败", str(e))

    # ========== 监控放大模式 ==========

    def _mf_toggle_zoom_mode(self):
        self._mf_zoom_mode = not self._mf_zoom_mode
        if self._mf_zoom_mode:
            self.mf_zoom_mode_btn.setText("✕ 退出放大")
            self.mf_zoom_mode_btn.setStyleSheet(
                "QPushButton { background: #f43f5e; color: white; font-weight: 700; }")
            self.mf_image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.mf_image_label.installEventFilter(self)
            self._mf_append_log("放大模式已开启：在图片上拖拽鼠标选择区域进行局部放大")
        else:
            self._mf_exit_zoom_mode()

    def _mf_exit_zoom_mode(self):
        self._mf_zoom_mode = False
        self.mf_zoom_mode_btn.setText("🔍 放大模式")
        self.mf_zoom_mode_btn.setStyleSheet("")
        self.mf_image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.mf_image_label.removeEventFilter(self)
        self._mf_clear_rubber_band()
        self.mf_restore_btn.hide()
        if self._mf_original_pixmap:
            self._mf_zoom_history.clear()
            self._mf_is_zoomed = False
            self.mf_image_label.setMinimumSize(1, 1)
            self._mf_scale_image(self._mf_original_pixmap)

    def _mf_restore_zoom(self):
        if self._mf_zoom_history:
            self._mf_zoom_history.pop()
        if self._mf_zoom_history:
            prev = self._mf_zoom_history[-1]
            scaled = prev.scaled(self.mf_image_label.size(),
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            self.mf_image_label.setPixmap(scaled)
        else:
            self.mf_restore_btn.hide()
            if self._mf_original_pixmap:
                self.mf_image_label.setMinimumSize(1, 1)
                self._mf_scale_image(self._mf_original_pixmap)
        if not self._mf_zoom_history:
            self.mf_restore_btn.hide()

    def _mf_clear_rubber_band(self):
        if self._mf_rubber_band:
            self._mf_rubber_band.hide()
            self._mf_rubber_band = None
        self._mf_rubber_origin = None

    def _mf_zoom_to_region(self, label_rect: QRect):
        if not self._mf_original_pixmap:
            return
        current_pixmap = self.mf_image_label.pixmap()
        if not current_pixmap:
            return
        label_size = self.mf_image_label.size()
        pixmap_rect = current_pixmap.rect()
        offset_x = (label_size.width() - pixmap_rect.width()) // 2
        offset_y = (label_size.height() - pixmap_rect.height()) // 2
        px = max(0, label_rect.x() - offset_x)
        py = max(0, label_rect.y() - offset_y)
        pw = min(label_rect.width(), pixmap_rect.width() - px)
        ph = min(label_rect.height(), pixmap_rect.height() - py)
        if pw <= 0 or ph <= 0:
            return
        scale_x = self._mf_original_pixmap.width() / pixmap_rect.width()
        scale_y = self._mf_original_pixmap.height() / pixmap_rect.height()
        orig_x = int(px * scale_x)
        orig_y = int(py * scale_y)
        orig_w = max(1, min(int(pw * scale_x), self._mf_original_pixmap.width() - orig_x))
        orig_h = max(1, min(int(ph * scale_y), self._mf_original_pixmap.height() - orig_y))
        cropped = self._mf_original_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        zoomed = cropped.scaled(label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        self._mf_zoom_history.append(current_pixmap)
        self.mf_image_label.setPixmap(zoomed)
        self.mf_restore_btn.show()
        self._mf_append_log(f"已放大区域: ({orig_x},{orig_y}) {orig_w}×{orig_h}")

    # --- 日志 ---
    def _mf_append_log(self, message: str):
        self.mf_status.append(message)
        sb = self.mf_status.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _on_nav_clicked(self, index: int):
        """侧边栏导航点击"""
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        self.nav_stack.setCurrentIndex(index)
        # 切换到历史数据时自动刷新
        if index == 4:  # 历史数据
            self._refresh_history_table(
                self.hist_search_edit.text() if hasattr(self, 'hist_search_edit') else "")

    def _toggle_sidebar(self):
        """折叠/展开侧边栏"""
        collapsed = self.sidebar.width() > 60
        if collapsed:
            self.sidebar.setFixedWidth(60)
            self._logo_title.setText("📊")
            self._logo_subtitle.hide()
            self.collapse_btn.setText(" ▶")
            for btn, (icon, label, _) in zip(self.nav_buttons, self._nav_data):
                btn.setText(f" {icon}")
                btn.setToolTip(label)
            self.collapse_btn.setToolTip("展开导航")
        else:
            self.sidebar.setFixedWidth(220)
            self._logo_title.setText("📊  CSV批处理工具")
            self._logo_subtitle.show()
            self.collapse_btn.setText("◀  折叠导航")
            for btn, (icon, label, _) in zip(self.nav_buttons, self._nav_data):
                btn.setText(f"  {icon}  {label}")
                btn.setToolTip("")
            self.collapse_btn.setToolTip("")

    def _on_tab_changed(self, index):
        """保留兼容，由 _on_nav_clicked 处理"""
        pass

    # ===================== 历史数据标签页 =====================
    def init_history_tab(self):
        layout = QVBoxLayout(self.history_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # --- 筛选栏 ---
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        filter_layout.addWidget(QLabel("关键词:"))
        self.hist_search_edit = QLineEdit()
        self.hist_search_edit.setPlaceholderText("搜索路径或备注...")
        self.hist_search_edit.textChanged.connect(self._history_search)
        filter_layout.addWidget(self.hist_search_edit, 1)

        filter_layout.addWidget(QLabel("异常:"))
        from PyQt6.QtWidgets import QComboBox
        self.hist_abnormal_combo = QComboBox()
        self.hist_abnormal_combo.addItems(["全部", "正常", "异常"])
        self.hist_abnormal_combo.currentIndexChanged.connect(self._history_search)
        filter_layout.addWidget(self.hist_abnormal_combo)

        filter_layout.addWidget(QLabel("日期从:"))
        self.hist_date_from = QDateEdit()
        self.hist_date_from.setCalendarPopup(True)
        self.hist_date_from.setDisplayFormat("yyyy-MM-dd")
        self.hist_date_from.setDate(QDate(2020, 1, 1))
        self.hist_date_from.setMaximumWidth(120)
        self.hist_date_from.dateChanged.connect(self._history_search)
        filter_layout.addWidget(self.hist_date_from)

        filter_layout.addWidget(QLabel("至:"))
        self.hist_date_to = QDateEdit()
        self.hist_date_to.setCalendarPopup(True)
        self.hist_date_to.setDisplayFormat("yyyy-MM-dd")
        self.hist_date_to.setDate(QDate(2099, 12, 31))
        self.hist_date_to.setMaximumWidth(120)
        self.hist_date_to.dateChanged.connect(self._history_search)
        filter_layout.addWidget(self.hist_date_to)

        btn_refresh = QPushButton("刷新")
        btn_refresh.clicked.connect(lambda: self._refresh_history_table())
        filter_layout.addWidget(btn_refresh)

        btn_clear = QPushButton("清除筛选")
        btn_clear.clicked.connect(self._history_clear_filters)
        filter_layout.addWidget(btn_clear)

        layout.addLayout(filter_layout)

        # --- 表格 ---
        from PyQt6.QtWidgets import QTableWidget, QHeaderView, QAbstractItemView
        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(6)
        self.hist_table.setHorizontalHeaderLabels(["ID", "保存时间", "CSV路径", "图像路径", "异常", "备注"])
        self.hist_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.hist_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.hist_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.hist_table.setAlternatingRowColors(True)
        self.hist_table.verticalHeader().setVisible(False)
        self.hist_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.hist_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.hist_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.hist_table.horizontalHeader().setStretchLastSection(True)
        self.hist_table.setColumnHidden(0, True)  # 隐藏 ID 列
        self.hist_table.itemSelectionChanged.connect(self._on_history_selection_changed)
        layout.addWidget(self.hist_table, 2)

        # --- 详情 & 操作区 ---
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        # 左侧：图像预览
        img_box = QGroupBox("图像预览")
        img_layout = QVBoxLayout()

        self.hist_scroll = QScrollArea()
        self.hist_scroll.setWidgetResizable(True)
        self.hist_scroll.setMinimumHeight(200)

        self.hist_preview_label = QLabel("选择一条记录查看云图")
        self.hist_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hist_preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.hist_preview_label.setMinimumSize(1, 1)
        self.hist_preview_label.setStyleSheet(
            "QLabel { background-color: rgba(255,255,255,0.5);"
            " border: 1px solid rgba(0,0,0,0.06); border-radius: 12px; }")
        self.hist_preview_label.mouseDoubleClickEvent = self._hist_image_dbl_click
        self._hist_orig_pixmap = None
        self._hist_zoomed = False
        self.hist_scroll.setWidget(self.hist_preview_label)
        img_layout.addWidget(self.hist_scroll)

        # 放大模式控制按钮
        hist_zoom_ctrl = QHBoxLayout()
        hist_zoom_ctrl.setSpacing(8)
        self.hist_zoom_mode_btn = QPushButton("🔍 放大模式")
        self.hist_zoom_mode_btn.setToolTip("进入放大模式后，在图片上拖拽选中区域即可局部放大")
        self.hist_zoom_mode_btn.clicked.connect(self._hist_toggle_zoom_mode)
        hist_zoom_ctrl.addWidget(self.hist_zoom_mode_btn)
        self.hist_restore_btn = QPushButton("↩ 还原")
        self.hist_restore_btn.setToolTip("还原到原始视图")
        self.hist_restore_btn.clicked.connect(self._hist_restore_zoom)
        self.hist_restore_btn.hide()
        hist_zoom_ctrl.addWidget(self.hist_restore_btn)
        hist_zoom_ctrl.addStretch()
        img_layout.addLayout(hist_zoom_ctrl)

        img_box.setLayout(img_layout)
        bottom.addWidget(img_box, 1)

        # 右侧：操作按钮
        btn_box = QGroupBox("操作")
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self.hist_abnormal_btn = QPushButton("标记异常 / 正常")
        self.hist_abnormal_btn.clicked.connect(self._history_toggle_abnormal)
        self.hist_abnormal_btn.setEnabled(False)
        btn_layout.addWidget(self.hist_abnormal_btn)

        self.hist_remark_btn = QPushButton("编辑备注")
        self.hist_remark_btn.clicked.connect(self._history_edit_remarks)
        self.hist_remark_btn.setEnabled(False)
        btn_layout.addWidget(self.hist_remark_btn)

        self.hist_open_btn = QPushButton("打开所在文件夹")
        self.hist_open_btn.clicked.connect(self._history_open_folder)
        self.hist_open_btn.setEnabled(False)
        btn_layout.addWidget(self.hist_open_btn)

        self.hist_delete_btn = QPushButton("删除记录")
        self.hist_delete_btn.setObjectName("histDeleteButton")
        self.hist_delete_btn.clicked.connect(self._history_delete_record)
        self.hist_delete_btn.setEnabled(False)
        btn_layout.addWidget(self.hist_delete_btn)

        btn_layout.addStretch()
        btn_box.setLayout(btn_layout)
        bottom.addWidget(btn_box)

        layout.addLayout(bottom, 1)

        self._refresh_history_table()

    def _refresh_history_table(self, search: str = ""):
        # 解析异常筛选
        abnormal_text = self.hist_abnormal_combo.currentText()
        is_abnormal = None if abnormal_text == "全部" else (1 if abnormal_text == "异常" else 0)

        from_date = self.hist_date_from.date()
        date_from = from_date.toString("yyyy-MM-dd") if from_date > QDate(2020, 1, 1) else ""
        to_date = self.hist_date_to.date()
        date_to = to_date.toString("yyyy-MM-dd") if to_date < QDate(2099, 12, 31) else ""

        records = query_records(search, is_abnormal=is_abnormal,
                                date_from=date_from, date_to=date_to)
        self.hist_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            items = [
                str(rec["id"]),
                rec["saved_at"],
                rec["csv_path"],
                rec["image_path"],
                "⚠ 异常" if rec["is_abnormal"] else "正常",
                rec["remarks"]
            ]
            for col, text in enumerate(items):
                from PyQt6.QtWidgets import QTableWidgetItem
                item = QTableWidgetItem(text)
                if col == 4 and rec["is_abnormal"]:
                    item.setForeground(Qt.GlobalColor.red)
                self.hist_table.setItem(row, col, item)
        self.hist_table.resizeColumnsToContents()

    def _on_history_selection_changed(self):
        row = self.hist_table.currentRow()
        has_row = row >= 0
        self.hist_abnormal_btn.setEnabled(has_row)
        self.hist_remark_btn.setEnabled(has_row)
        self.hist_open_btn.setEnabled(has_row)
        self.hist_delete_btn.setEnabled(has_row)

        if not has_row:
            self.hist_preview_label.setText("选择一条记录查看云图")
            self._hist_orig_pixmap = None
            return

        img_path = self.hist_table.item(row, 3).text()
        self._hist_current_image_path = img_path
        self._hist_zoom_history.clear()
        self.hist_restore_btn.hide()
        self._hist_zoomed = False
        if os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            if not pixmap.isNull():
                self._hist_orig_pixmap = pixmap
                self._scale_hist_image(pixmap)
                return
        self.hist_preview_label.setText("(图像文件不存在)")
        self._hist_orig_pixmap = None

    def _scale_hist_image(self, pixmap):
        w = self.hist_scroll.width() - 10 or 300
        h = self.hist_scroll.height() - 10 or 200
        scaled = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
        self.hist_preview_label.setPixmap(scaled)

    def _hist_image_dbl_click(self, event):
        """双击 — 在全功能查看器中打开；放大模式中则还原"""
        if not self._hist_orig_pixmap:
            return
        if self._hist_zoom_mode:
            self._hist_restore_zoom()
            return
        try:
            self._hist_viewer = ImageViewerWindow(
                self._hist_current_image_path, '', self)
            self._hist_viewer.show()
        except Exception as e:
            pass

    def _history_toggle_abnormal(self):
        row = self.hist_table.currentRow()
        if row < 0:
            return
        record_id = int(self.hist_table.item(row, 0).text())
        current = self.hist_table.item(row, 4).text()
        new_val = 0 if "异常" in current else 1
        update_record(record_id, is_abnormal=new_val)
        self._refresh_history_table(self.hist_search_edit.text())

    def _history_edit_remarks(self):
        row = self.hist_table.currentRow()
        if row < 0:
            return
        record_id = int(self.hist_table.item(row, 0).text())
        current = self.hist_table.item(row, 5).text()
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "编辑备注", "备注内容:", text=current)
        if ok:
            update_record(record_id, remarks=text)
            self._refresh_history_table(self.hist_search_edit.text())

    def _history_open_folder(self):
        row = self.hist_table.currentRow()
        if row < 0:
            return
        csv_path = self.hist_table.item(row, 2).text()
        folder = os.path.dirname(csv_path)
        if os.path.isdir(folder):
            os.startfile(folder)

    def _history_delete_record(self):
        row = self.hist_table.currentRow()
        if row < 0:
            return
        record_id = int(self.hist_table.item(row, 0).text())
        reply = QMessageBox.question(
            self, "确认删除", f"确定要删除记录 #{record_id} 吗？\n（仅删除数据库记录，文件保留）",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_record(record_id)
            self._refresh_history_table(self.hist_search_edit.text())

    # ========== 历史数据放大模式 ==========

    def _hist_toggle_zoom_mode(self):
        self._hist_zoom_mode = not self._hist_zoom_mode
        if self._hist_zoom_mode:
            self.hist_zoom_mode_btn.setText("✕ 退出放大")
            self.hist_zoom_mode_btn.setStyleSheet(
                "QPushButton { background: #f43f5e; color: white; font-weight: 700; }")
            self.hist_preview_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.hist_preview_label.installEventFilter(self)
        else:
            self._hist_exit_zoom_mode()

    def _hist_exit_zoom_mode(self):
        self._hist_zoom_mode = False
        self.hist_zoom_mode_btn.setText("🔍 放大模式")
        self.hist_zoom_mode_btn.setStyleSheet("")
        self.hist_preview_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.hist_preview_label.removeEventFilter(self)
        self._hist_clear_rubber_band()
        self.hist_restore_btn.hide()
        if self._hist_orig_pixmap:
            self._hist_zoom_history.clear()
            self._hist_zoomed = False
            self._scale_hist_image(self._hist_orig_pixmap)

    def _hist_restore_zoom(self):
        if self._hist_zoom_history:
            self._hist_zoom_history.pop()
        if self._hist_zoom_history:
            prev = self._hist_zoom_history[-1]
            scaled = prev.scaled(self.hist_preview_label.size(),
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            self.hist_preview_label.setPixmap(scaled)
        else:
            self.hist_restore_btn.hide()
            if self._hist_orig_pixmap:
                self._scale_hist_image(self._hist_orig_pixmap)
        if not self._hist_zoom_history:
            self.hist_restore_btn.hide()

    def _hist_clear_rubber_band(self):
        if self._hist_rubber_band:
            self._hist_rubber_band.hide()
            self._hist_rubber_band = None
        self._hist_rubber_origin = None

    def _hist_zoom_to_region(self, label_rect: QRect):
        if not self._hist_orig_pixmap:
            return
        current_pixmap = self.hist_preview_label.pixmap()
        if not current_pixmap:
            return
        label_size = self.hist_preview_label.size()
        pixmap_rect = current_pixmap.rect()
        offset_x = (label_size.width() - pixmap_rect.width()) // 2
        offset_y = (label_size.height() - pixmap_rect.height()) // 2
        px = max(0, label_rect.x() - offset_x)
        py = max(0, label_rect.y() - offset_y)
        pw = min(label_rect.width(), pixmap_rect.width() - px)
        ph = min(label_rect.height(), pixmap_rect.height() - py)
        if pw <= 0 or ph <= 0:
            return
        scale_x = self._hist_orig_pixmap.width() / pixmap_rect.width()
        scale_y = self._hist_orig_pixmap.height() / pixmap_rect.height()
        orig_x = int(px * scale_x)
        orig_y = int(py * scale_y)
        orig_w = max(1, min(int(pw * scale_x), self._hist_orig_pixmap.width() - orig_x))
        orig_h = max(1, min(int(ph * scale_y), self._hist_orig_pixmap.height() - orig_y))
        cropped = self._hist_orig_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        zoomed = cropped.scaled(label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        self._hist_zoom_history.append(current_pixmap)
        self.hist_preview_label.setPixmap(zoomed)
        self.hist_restore_btn.show()

    def _history_search(self):
        self._refresh_history_table(self.hist_search_edit.text())

    def _history_clear_filters(self):
        """清除所有筛选条件"""
        self.hist_search_edit.clear()
        self.hist_abnormal_combo.setCurrentIndex(0)
        self.hist_date_from.setDate(QDate(2020, 1, 1))
        self.hist_date_to.setDate(QDate(2099, 12, 31))
        self._refresh_history_table()

    # ==================== 放大模式事件过滤器 ====================

    def eventFilter(self, obj, event):
        """在放大模式下处理鼠标事件进行区域框选（单文件夹/监控/历史 共用）"""
        from PyQt6.QtCore import QEvent

        # 确定是哪个标签
        if obj is self.sf_image_label and self._sf_zoom_mode:
            prefix = '_sf'
        elif obj is self.mf_image_label and self._mf_zoom_mode:
            prefix = '_mf'
        elif obj is self.hist_preview_label and self._hist_zoom_mode:
            prefix = '_hist'
        else:
            return super().eventFilter(obj, event)

        etype = event.type()
        rubber_band = getattr(self, f'{prefix}_rubber_band')

        if etype == QEvent.Type.MouseButtonPress and \
           event.button() == Qt.MouseButton.LeftButton:
            setattr(self, f'{prefix}_rubber_origin', event.pos())
            if not rubber_band:
                rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, obj)
                setattr(self, f'{prefix}_rubber_band', rubber_band)
            rubber_band.setGeometry(QRect(getattr(self, f'{prefix}_rubber_origin'), QSize()))
            rubber_band.show()
            return True

        if etype == QEvent.Type.MouseMove and rubber_band:
            origin = getattr(self, f'{prefix}_rubber_origin')
            if origin:
                rubber_band.setGeometry(QRect(origin, event.pos()).normalized())
            return True

        if etype == QEvent.Type.MouseButtonRelease and rubber_band:
            rect = rubber_band.geometry()
            # 清除
            rubber_band.hide()
            setattr(self, f'{prefix}_rubber_band', None)
            setattr(self, f'{prefix}_rubber_origin', None)
            if rect.width() > 10 and rect.height() > 10:
                zoom_method = getattr(self, f'{prefix}_zoom_to_region')
                zoom_method(rect)
            return True

        return super().eventFilter(obj, event)

    def init_usage_tab(self):
        """初始化使用说明标签页"""
        # 创建主布局
        main_layout = QVBoxLayout(self.usage_tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建QTextBrowser控件
        self.usage_browser = QTextBrowser()
        self.usage_browser.setOpenExternalLinks(True)
        
        # 设置美观简约的样式
        # 读取并显示ReadMe.md文件
        try:
            readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ReadMe.md")
            with open(readme_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 将Markdown转换为HTML
            html_content = markdown.markdown(markdown_content, extensions=['fenced_code', 'tables'])
            
            # 设置HTML内容
            self.usage_browser.setHtml(html_content)
        except Exception as e:
            self.usage_browser.setPlainText(f"无法读取使用说明文件: {str(e)}")
        
        main_layout.addWidget(self.usage_browser)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())