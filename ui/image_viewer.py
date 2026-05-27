#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全功能图片查看器窗口 — 支持缩放、平移、旋转
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QGraphicsView, QGraphicsScene,
                              QGraphicsPixmapItem, QToolBar, QStatusBar)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QAction, QKeySequence, QShortcut


class ImageViewerWindow(QMainWindow):
    """全功能图片查看器，支持缩放、平移、旋转"""

    def __init__(self, image_path: str, title: str = "", parent=None):
        super().__init__(parent)
        self._image_path = image_path
        self._zoom_factor = 1.0

        fname = os.path.basename(image_path)
        self.setWindowTitle(f"图片查看器 - {fname}")
        self.resize(1100, 780)

        # ---- 场景 & 视图 ----
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._view.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self._view.setBackgroundBrush(Qt.GlobalColor.transparent)

        # 加载图像
        self._pixmap = QPixmap(image_path)
        if self._pixmap.isNull():
            raise ValueError(f"无法加载图像: {image_path}")
        self._pixmap_item = QGraphicsPixmapItem(self._pixmap)
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(QRectF(self._pixmap.rect()))

        self.setCentralWidget(self._view)

        # ---- 工具栏 ----
        self._toolbar = QToolBar("工具")
        self._toolbar.setMovable(False)
        self.addToolBar(self._toolbar)

        self._act_zoom_in = QAction("🔍 放大")
        self._act_zoom_in.triggered.connect(lambda: self._zoom(1.25))
        self._toolbar.addAction(self._act_zoom_in)

        self._act_zoom_out = QAction("🔎 缩小")
        self._act_zoom_out.triggered.connect(lambda: self._zoom(0.8))
        self._toolbar.addAction(self._act_zoom_out)

        self._toolbar.addSeparator()

        self._act_rot_left = QAction("↺ 左转90°")
        self._act_rot_left.triggered.connect(lambda: self._view.rotate(-90))
        self._toolbar.addAction(self._act_rot_left)

        self._act_rot_right = QAction("↻ 右转90°")
        self._act_rot_right.triggered.connect(lambda: self._view.rotate(90))
        self._toolbar.addAction(self._act_rot_right)

        self._toolbar.addSeparator()

        self._act_fit = QAction("📐 适应窗口")
        self._act_fit.triggered.connect(self._fit_to_window)
        self._toolbar.addAction(self._act_fit)

        self._act_reset = QAction("🔁 原始大小")
        self._act_reset.triggered.connect(self._reset)
        self._toolbar.addAction(self._act_reset)

        # ---- 快捷键 ----
        QShortcut(QKeySequence.StandardKey.ZoomIn, self, lambda: self._zoom(1.25))
        QShortcut(QKeySequence.StandardKey.ZoomOut, self, lambda: self._zoom(0.8))
        QShortcut(QKeySequence("Ctrl+0"), self, self._fit_to_window)
        QShortcut(QKeySequence("Ctrl+1"), self, self._reset)

        # ---- 状态栏 ----
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._update_status()

        # 初始适应窗口
        self._fit_to_window()

    # ==================== 核心操作 ====================

    def _zoom(self, factor: float):
        self._view.scale(factor, factor)
        self._zoom_factor = self._view.transform().m11()
        self._update_status()

    def _fit_to_window(self):
        self._view.fitInView(self._scene.sceneRect(),
                             Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_factor = self._view.transform().m11()
        self._update_status()

    def _reset(self):
        self._view.resetTransform()
        self._zoom_factor = 1.0
        self._update_status()

    def _update_status(self):
        pct = int(self._zoom_factor * 100)
        w, h = self._pixmap.width(), self._pixmap.height()
        self._status.showMessage(
            f"缩放: {pct}%  |  尺寸: {w} × {h} px  |  "
            f"滚轮缩放  |  拖拽平移  |  Ctrl+/- 缩放  |  Ctrl+0 适应  |  Ctrl+1 原始"
        )

    # ==================== 滚轮缩放 ====================

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._zoom(1.15)
        else:
            self._zoom(0.87)
