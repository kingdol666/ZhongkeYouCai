#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热力云图显示界面
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFileDialog, QTextEdit, QGroupBox,
                            QMessageBox, QScrollArea, QSizePolicy, QRubberBand,
                            QLineEdit)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QPixmap, QFont, QCursor

# 确保项目根目录在 sys.path 中
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic.heatmap_thread import HeatmapThread
from ui.image_viewer import ImageViewerWindow


class HeatmapWidget(QWidget):
    """热力云图显示界面"""
    
    def __init__(self):
        super().__init__()
        self.heatmap_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 创建文件选择组
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout()
        file_layout.setContentsMargins(15, 20, 15, 15)
        file_layout.setSpacing(12)
        
        file_layout.addWidget(QLabel("CSV文件:"))
        self.file_path_edit = QLabel("未选择文件")
        self.file_path_edit.setStyleSheet(
            "QLabel {"
            " background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            " stop:0 rgba(255,255,255,0.75), stop:1 rgba(255,255,255,0.5));"
            " border: 1px solid rgba(0,0,0,0.08);"
            " padding: 10px 14px; border-radius: 11px;"
            " color: #111827; font-weight: 600; }")
        file_layout.addWidget(self.file_path_edit, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("browseButton")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 创建参数设置组
        param_group = QGroupBox("参数设置")
        param_layout = QHBoxLayout()
        param_layout.setContentsMargins(15, 20, 15, 15)
        param_layout.setSpacing(15)
        
        param_layout.addWidget(QLabel("Target:"))
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("目标值")
        self.target_edit.setFixedWidth(100)
        param_layout.addWidget(self.target_edit)
        
        param_layout.addWidget(QLabel("上限:"))
        self.upper_edit = QLineEdit()
        self.upper_edit.setPlaceholderText("上限值")
        self.upper_edit.setFixedWidth(100)
        param_layout.addWidget(self.upper_edit)
        
        param_layout.addWidget(QLabel("下限:"))
        self.lower_edit = QLineEdit()
        self.lower_edit.setPlaceholderText("下限值")
        self.lower_edit.setFixedWidth(100)
        param_layout.addWidget(self.lower_edit)
        
        param_layout.addStretch()
        param_group.setLayout(param_layout)
        main_layout.addWidget(param_group)
        
        # 创建控制按钮组
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        self.generate_btn = QPushButton("生成热力图")
        self.generate_btn.clicked.connect(self.generate_heatmap)
        self.generate_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        control_layout.addWidget(self.generate_btn)
        
        self.stop_btn = QPushButton("停止生成")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
        
        # 创建图像显示区域
        image_group = QGroupBox("热力图显示")
        image_layout = QVBoxLayout()
        image_layout.setContentsMargins(5, 5, 5, 5)  # 减少内边距
        image_layout.setSpacing(2)  # 减少间距
        
        # 创建滚动区域用于显示图像
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setMinimumHeight(400)  # 设置最小高度
        
        # 创建图像标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("请选择CSV文件并生成热力图")
        self.image_label.setStyleSheet(
            "QLabel {"
            " background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            " stop:0 rgba(255,255,255,0.55), stop:1 rgba(255,255,255,0.3));"
            " border: 1px solid rgba(255,255,255,0.7);"
            " border-radius: 16px; }")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setMinimumSize(1, 1)  # 确保标签可以调整大小
        # 启用鼠标跟踪以支持双击事件
        self.image_label.mouseDoubleClickEvent = self.on_image_double_click
        self.scroll_area.setWidget(self.image_label)
        
        # 添加状态变量跟踪图片缩放状态
        self.is_zoomed = False
        self.original_pixmap = None

        # 放大模式状态
        self._zoom_mode = False
        self._rubber_band: QRubberBand | None = None
        self._rubber_origin: QPoint | None = None
        self._zoom_history: list[QPixmap] = []  # 用于还原
        
        image_layout.addWidget(self.scroll_area)
        image_group.setLayout(image_layout)
        image_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(image_group, 1)

        # 放大模式控制按钮
        zoom_ctrl = QHBoxLayout()
        zoom_ctrl.setSpacing(8)
        self.zoom_mode_btn = QPushButton("🔍 放大模式")
        self.zoom_mode_btn.setToolTip("进入放大模式后，在图片上拖拽选中区域即可局部放大")
        self.zoom_mode_btn.clicked.connect(self._toggle_zoom_mode)
        zoom_ctrl.addWidget(self.zoom_mode_btn)

        self.restore_btn = QPushButton("↩ 还原")
        self.restore_btn.setToolTip("还原到原始视图")
        self.restore_btn.clicked.connect(self._restore_zoom)
        self.restore_btn.hide()
        zoom_ctrl.addWidget(self.restore_btn)
        zoom_ctrl.addStretch()
        main_layout.addLayout(zoom_ctrl)
        
        # 创建状态显示区域
        status_group = QGroupBox("处理状态")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 20, 15, 15)
        status_layout.setSpacing(10)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Consolas", 9))
        self.status_text.setMaximumHeight(150)
        status_layout.addWidget(self.status_text)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # 设置默认输出目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(project_root, "Heatmaps")
        
    def browse_file(self):
        """浏览CSV文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择CSV文件", 
            "", 
            "CSV文件 (*.csv);;所有文件 (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            
    def generate_heatmap(self):
        """生成热力图"""
        file_path = self.file_path_edit.text()
        if file_path == "未选择文件":
            QMessageBox.warning(self, "文件错误", "请先选择CSV文件")
            return
        
        target = None
        upper = None
        lower = None
        
        target_text = self.target_edit.text().strip()
        upper_text = self.upper_edit.text().strip()
        lower_text = self.lower_edit.text().strip()
        
        if target_text and upper_text and lower_text:
            try:
                target = float(target_text)
                upper = float(upper_text)
                lower = float(lower_text)
            except ValueError:
                QMessageBox.warning(self, "参数错误", "请输入有效的数值")
                return
        elif target_text or upper_text or lower_text:
            QMessageBox.warning(self, "参数不完整", "请同时填写Target、上限和下限，或全部留空使用默认值")
            return
        
        # 禁用控制按钮
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_text.clear()
        
        # 创建并启动热力图生成线程
        self.heatmap_thread = HeatmapThread(file_path, self.output_dir,
                                           target=target, upper=upper, lower=lower)
        
        # 连接信号
        self.heatmap_thread.progress_updated.connect(self.update_progress)
        self.heatmap_thread.status_updated.connect(self.update_status)
        self.heatmap_thread.image_ready.connect(self.display_image)
        self.heatmap_thread.finished.connect(self.generation_finished)
        
        # 启动线程
        self.heatmap_thread.start()
        
    def stop_generation(self):
        """停止生成热力图"""
        if self.heatmap_thread and self.heatmap_thread.isRunning():
            self.heatmap_thread.stop()
            
    def update_progress(self, value):
        """更新进度"""
        # 这里可以添加进度条更新逻辑
        pass
        
    def update_status(self, message):
        """更新状态信息"""
        self.status_text.append(message)
        # 自动滚动到底部
        scrollbar = self.status_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def on_image_double_click(self, event):
        """双击图片 — 在全功能查看器中打开"""
        if not self.original_pixmap:
            return
        # 在放大模式中，双击还原
        if self._zoom_mode:
            self._restore_zoom()
            return
        try:
            self._viewer = ImageViewerWindow(
                self._current_image_path, self._current_title, self)
            self._viewer.show()
        except Exception as e:
            self.status_text.append(f"打开图片查看器失败: {e}")

    # ==================== 放大模式 ====================

    def _toggle_zoom_mode(self):
        """切换放大模式"""
        self._zoom_mode = not self._zoom_mode
        if self._zoom_mode:
            self.zoom_mode_btn.setText("✕ 退出放大")
            self.zoom_mode_btn.setStyleSheet(
                "QPushButton { background: #f43f5e; color: white; font-weight: 700; }")
            self.image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.image_label.installEventFilter(self)
            self.status_text.append("放大模式已开启：在图片上拖拽鼠标选择区域进行局部放大")
        else:
            self._exit_zoom_mode()

    def _exit_zoom_mode(self):
        """退出放大模式"""
        self._zoom_mode = False
        self.zoom_mode_btn.setText("🔍 放大模式")
        self.zoom_mode_btn.setStyleSheet("")
        self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.image_label.removeEventFilter(self)
        self._clear_rubber_band()
        self.restore_btn.hide()
        # 恢复适应窗口显示
        if self.original_pixmap and self._zoom_history:
            self._zoom_history.clear()
            self.display_image_scaled(self.original_pixmap)

    def _restore_zoom(self):
        """还原缩放：从 zoom_history 弹出上一级或直接回到原始"""
        if self._zoom_history:
            self._zoom_history.pop()  # 移除当前
        if self._zoom_history:
            prev = self._zoom_history[-1]
            scaled = prev.scaled(self.image_label.size(),
                                 Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.restore_btn.hide()
            if self.original_pixmap:
                self.display_image_scaled(self.original_pixmap)
        if not self._zoom_history:
            self.restore_btn.hide()

    def _clear_rubber_band(self):
        if self._rubber_band:
            self._rubber_band.hide()
            self._rubber_band = None
        self._rubber_origin = None

    def eventFilter(self, obj, event):
        """在放大模式下处理鼠标事件进行区域选择"""
        if obj is not self.image_label or not self._zoom_mode:
            return super().eventFilter(obj, event)

        from PyQt5.QtCore import QEvent
        etype = event.type()

        if etype == QEvent.Type.MouseButtonPress and \
           event.button() == Qt.MouseButton.LeftButton:
            self._rubber_origin = event.pos()
            if not self._rubber_band:
                self._rubber_band = QRubberBand(
                    QRubberBand.Shape.Rectangle, self.image_label)
            self._rubber_band.setGeometry(QRect(self._rubber_origin, QSize()))
            self._rubber_band.show()
            return True

        if etype == QEvent.Type.MouseMove and self._rubber_band:
            self._rubber_band.setGeometry(
                QRect(self._rubber_origin, event.pos()).normalized())
            return True

        if etype == QEvent.Type.MouseButtonRelease and self._rubber_band:
            rect = self._rubber_band.geometry()
            self._clear_rubber_band()
            if rect.width() > 10 and rect.height() > 10:
                self._zoom_to_region(rect)
            return True

        return super().eventFilter(obj, event)

    def _zoom_to_region(self, label_rect: QRect):
        """根据在 QLabel 上选中的区域裁剪原始图像并放大显示"""
        if not self.original_pixmap:
            return

        current_pixmap = self.image_label.pixmap()
        if not current_pixmap:
            return

        label_size = self.image_label.size()
        pixmap_rect = current_pixmap.rect()

        # 计算 pixmap 在 label 中的偏移（居中显示时）
        offset_x = (label_size.width() - pixmap_rect.width()) // 2
        offset_y = (label_size.height() - pixmap_rect.height()) // 2

        # 将 label 坐标映射到当前 pixmap 坐标
        px = max(0, label_rect.x() - offset_x)
        py = max(0, label_rect.y() - offset_y)
        pw = min(label_rect.width(), pixmap_rect.width() - px)
        ph = min(label_rect.height(), pixmap_rect.height() - py)

        if pw <= 0 or ph <= 0:
            return

        # 再映射到原始 pixmap 坐标
        scale_x = self.original_pixmap.width() / pixmap_rect.width()
        scale_y = self.original_pixmap.height() / pixmap_rect.height()

        orig_x = int(px * scale_x)
        orig_y = int(py * scale_y)
        orig_w = int(pw * scale_x)
        orig_h = int(ph * scale_y)

        orig_w = max(1, min(orig_w, self.original_pixmap.width() - orig_x))
        orig_h = max(1, min(orig_h, self.original_pixmap.height() - orig_y))

        cropped = self.original_pixmap.copy(orig_x, orig_y, orig_w, orig_h)
        # 缩放裁剪后的图片填充 label
        zoomed = cropped.scaled(label_size,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation)
        # 保存当前视图到历史
        self._zoom_history.append(current_pixmap)
        self.image_label.setPixmap(zoomed)
        self.restore_btn.show()
        self.status_text.append(f"已放大区域: ({orig_x},{orig_y}) {orig_w}×{orig_h}")
    
    def display_image_scaled(self, pixmap):
        """缩放显示图像以适应显示区域"""
        # 获取滚动区域的可用大小
        available_width = self.scroll_area.width() - 10  # 减少一些边距
        available_height = self.scroll_area.height() - 10
        
        # 如果滚动区域大小还没有正确计算，使用默认值
        if available_width <= 10:
            available_width = 600
        if available_height <= 10:
            available_height = 400
        
        # 缩放图像以适应可用空间
        scaled_pixmap = pixmap.scaled(
            available_width, 
            available_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        
    def display_image(self, image_path, title):
        """显示热力图图像"""
        try:
            self._current_image_path = image_path
            self._current_title = title

            self.original_pixmap = QPixmap(image_path)
            if self.original_pixmap.isNull():
                self.status_text.append("错误：无法加载图像")
                return

            self.is_zoomed = False
            self._zoom_history.clear()
            self.restore_btn.hide()

            self.display_image_scaled(self.original_pixmap)
            self.image_label.setText("")

            self.status_text.append(f"热力图已加载: {os.path.basename(image_path)}")
            self.status_text.append("提示：双击图片可在全功能查看器中打开")
            self.status_text.append("提示：点击「🔍 放大模式」可在图上框选区域局部放大")

        except Exception as e:
            self.status_text.append(f"显示图像时出错: {str(e)}")
            
    def generation_finished(self, success, message):
        """生成完成"""
        # 启用控制按钮
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 显示完成消息
        if success:
            QMessageBox.information(self, "生成完成", message)
        else:
            QMessageBox.warning(self, "生成失败", message)