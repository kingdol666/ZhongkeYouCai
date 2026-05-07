#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热力云图显示界面
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QTextEdit, QGroupBox, 
                            QMessageBox, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QFont

# 导入处理逻辑
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'logic'))
from logic.heatmap_thread import HeatmapThread
# 导入现代风格样式
from ui.modern_style import MODERN_STYLE


class HeatmapWidget(QWidget):
    """热力云图显示界面"""
    
    def __init__(self):
        super().__init__()
        self.heatmap_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 应用现代风格样式
        self.setStyleSheet(MODERN_STYLE)
        
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
        self.file_path_edit.setStyleSheet("QLabel { background-color: #f8f9fa; border: 2px solid #e0e0e0; padding: 8px 12px; border-radius: 6px; }")
        file_layout.addWidget(self.file_path_edit, 1)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.setObjectName("browseButton")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
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
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("请选择CSV文件并生成热力图")
        self.image_label.setStyleSheet("QLabel { background-color: white; border: 2px solid #e0e0e0; border-radius: 6px; }")
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setMinimumSize(1, 1)  # 确保标签可以调整大小
        # 启用鼠标跟踪以支持双击事件
        self.image_label.mouseDoubleClickEvent = self.on_image_double_click
        self.scroll_area.setWidget(self.image_label)
        
        # 添加状态变量跟踪图片缩放状态
        self.is_zoomed = False
        self.original_pixmap = None
        
        image_layout.addWidget(self.scroll_area)
        image_group.setLayout(image_layout)
        image_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # 让组也扩展
        main_layout.addWidget(image_group, 1)  # 使用拉伸因子，让图像区域占据更多空间
        
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
            
        # 禁用控制按钮
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_text.clear()
        
        # 创建并启动热力图生成线程
        self.heatmap_thread = HeatmapThread(file_path, self.output_dir)
        
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
        """处理图像双击事件，在原始大小和适应大小之间切换"""
        if not self.original_pixmap:
            return
            
        # 切换缩放状态
        self.is_zoomed = not self.is_zoomed
        
        if self.is_zoomed:
            # 显示原始大小
            self.image_label.setPixmap(self.original_pixmap)
            self.image_label.setMinimumSize(self.original_pixmap.size())
            self.status_text.append("已切换到原始大小显示")
        else:
            # 显示适应大小
            self.display_image_scaled(self.original_pixmap)
            self.status_text.append("已切换到适应窗口大小显示")
    
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
            # 保存原始图像
            self.original_pixmap = QPixmap(image_path)
            if self.original_pixmap.isNull():
                self.status_text.append("错误：无法加载图像")
                return
                
            # 重置缩放状态
            self.is_zoomed = False
            
            # 使用缩放后的图像显示
            self.display_image_scaled(self.original_pixmap)
            self.image_label.setText("")
            
            # 更新状态文本
            self.status_text.append(f"热力图已加载: {os.path.basename(image_path)}")
            self.status_text.append("提示：双击图片可以切换原始大小/适应大小")
            
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