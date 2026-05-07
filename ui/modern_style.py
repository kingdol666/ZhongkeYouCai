#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级毛玻璃质感 UI 样式表 — Premium Glassmorphism Design System
浅色琥珀金主题 | 多层次半透明 | 高对比度 | 卡片式布局
"""

MODERN_STYLE = """
/* ============================================================
   GLOBAL — 全局基础
   ============================================================ */
QWidget {
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    font-size: 12px;
    color: #111827;
    background-color: transparent;
    font-weight: 500;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #f8f9fc, stop:0.25 #f3f5fb, stop:0.5 #f0f3f9,
        stop:0.75 #eef1f7, stop:1 #eceff5);
}

QMainWindow::separator {
    width: 0px;
    height: 0px;
}

/* ============================================================
   SIDEBAR — 高级毛玻璃侧边栏
   ============================================================ */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.82),
        stop:0.2 rgba(252,252,255,0.85),
        stop:0.5 rgba(250,250,254,0.82),
        stop:0.8 rgba(248,248,252,0.78),
        stop:1 rgba(245,245,250,0.75));
    border-right: 1px solid rgba(0,0,0,0.05);
    border-image: none;
}

QFrame#logoFrame {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.0),
        stop:1 rgba(245,158,11,0.03));
    border-bottom: 1px solid rgba(0,0,0,0.04);
    padding: 4px 0;
}

QLabel#logoTitle {
    color: #0f172a;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.6px;
    background: transparent;
}

QLabel#logoSubtitle {
    color: rgba(107,114,128,0.75);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.8px;
    background: transparent;
    margin-top: 3px;
}

QFrame#sidebarSeparator {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(0,0,0,0.0), stop:0.3 rgba(0,0,0,0.04),
        stop:0.7 rgba(0,0,0,0.04), stop:1 rgba(0,0,0,0.0));
    max-height: 1px;
    margin: 6px 16px;
}

QPushButton#navButton {
    background: transparent;
    color: #4b5563;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 13px 18px;
    margin: 2px 10px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 10px;
}

QPushButton#navButton:hover {
    background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
        stop:0 rgba(245,158,11,0.04),
        stop:1 rgba(245,158,11,0.01));
    color: #1e293b;
    border-left: 3px solid rgba(245,158,11,0.4);
}

QPushButton#navButton:checked {
    background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
        stop:0 rgba(245,158,11,0.1),
        stop:0.6 rgba(245,158,11,0.04),
        stop:1 rgba(245,158,11,0.0));
    color: #0f172a;
    border-left: 3px solid #f59e0b;
    font-weight: 700;
}

QPushButton#collapseButton {
    background: transparent;
    color: rgba(107,114,128,0.45);
    border: none;
    border-top: 1px solid rgba(0,0,0,0.04);
    text-align: center;
    padding: 14px;
    font-size: 12px;
    font-weight: 600;
    min-width: 0;
}

QPushButton#collapseButton:hover {
    background: rgba(245,158,11,0.04);
    color: #4b5563;
}

QFrame#contentFrame {
    background: transparent;
}

/* ============================================================
   GROUP BOX — 高级毛玻璃卡片
   ============================================================ */
QGroupBox {
    font-weight: 700;
    font-size: 13px;
    color: #111827;
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 18px;
    margin-top: 20px;
    padding: 24px 18px 18px 18px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.7),
        stop:0.5 rgba(255,255,255,0.5),
        stop:1 rgba(255,255,255,0.4));
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 22px;
    padding: 2px 14px;
    color: #b45309;
    font-size: 13px;
    font-weight: 800;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.9),
        stop:1 rgba(255,255,255,0.6));
    border: 1px solid rgba(245,158,11,0.12);
    border-radius: 8px;
}

/* ============================================================
   BUTTONS — 精致按钮系统
   ============================================================ */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f59e0b, stop:0.5 #e88d08, stop:1 #d97706);
    color: #ffffff;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 12px;
    min-width: 80px;
    letter-spacing: 0.2px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e88d08, stop:0.5 #d97706, stop:1 #b45309);
    border-color: rgba(255,255,255,0.25);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #b45309, stop:1 #92400e);
}

QPushButton:disabled {
    background: #e5e7eb;
    color: #9ca3af;
    border-color: transparent;
}

QPushButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f43f5e, stop:0.5 #e11d48, stop:1 #be123c);
    border: 1px solid rgba(255,255,255,0.15);
}

QPushButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e11d48, stop:0.5 #be123c, stop:1 #9f1239);
}

QPushButton#browseButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.6),
        stop:1 rgba(245,158,11,0.06));
    color: #4b5563;
    border: 1px solid rgba(245,158,11,0.18);
    font-weight: 600;
    border-radius: 10px;
    padding: 9px 18px;
}

QPushButton#browseButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.85),
        stop:1 rgba(245,158,11,0.12));
    color: #1e293b;
    border-color: rgba(245,158,11,0.4);
}

QPushButton#histDeleteButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f43f5e, stop:0.5 #e11d48, stop:1 #be123c);
}

/* ============================================================
   INPUTS — 毛玻璃输入框
   ============================================================ */
QLineEdit, QTextEdit {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 11px;
    padding: 10px 15px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.75),
        stop:1 rgba(255,255,255,0.5));
    selection-background-color: #fde68a;
    color: #111827;
    font-weight: 500;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1.5px solid #f59e0b;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.97),
        stop:1 rgba(255,255,255,0.85));
}

QLineEdit:read-only {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(250,250,252,0.55),
        stop:1 rgba(248,248,250,0.4));
    color: #4b5563;
}

QLineEdit:read-only:focus {
    border-color: rgba(0,0,0,0.08);
}

/* ============================================================
   LABELS
   ============================================================ */
QLabel {
    color: #111827;
    font-weight: 600;
    background: transparent;
}

/* ============================================================
   SCROLL AREA — 毛玻璃滚动区
   ============================================================ */
QScrollArea {
    border: 1px solid rgba(255,255,255,0.5);
    border-radius: 16px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.3),
        stop:1 rgba(255,255,255,0.15));
}

/* ---- 精致滚动条 ---- */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 6px 2px;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(156,163,175,0.3),
        stop:0.5 rgba(156,163,175,0.4),
        stop:1 rgba(156,163,175,0.3));
    border-radius: 3px;
    min-height: 32px;
}

QScrollBar::handle:vertical:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 rgba(245,158,11,0.35),
        stop:0.5 rgba(245,158,11,0.45),
        stop:1 rgba(245,158,11,0.35));
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 6px;
    margin: 2px 6px;
}

QScrollBar::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(156,163,175,0.3),
        stop:0.5 rgba(156,163,175,0.4),
        stop:1 rgba(156,163,175,0.3));
    border-radius: 3px;
    min-width: 32px;
}

QScrollBar::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(245,158,11,0.35),
        stop:0.5 rgba(245,158,11,0.45),
        stop:1 rgba(245,158,11,0.35));
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============================================================
   PROGRESS BAR — 渐变进度条
   ============================================================ */
QProgressBar {
    border: none;
    border-radius: 10px;
    text-align: center;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(229,231,235,0.6),
        stop:1 rgba(243,244,246,0.4));
    color: #4b5563;
    font-weight: 700;
    font-size: 10px;
    height: 14px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f59e0b, stop:0.3 #fbbf24, stop:0.7 #f59e0b, stop:1 #d97706);
    border-radius: 10px;
    margin: 1px;
}

/* ============================================================
   CHECKBOX
   ============================================================ */
QCheckBox {
    color: #111827;
    font-weight: 600;
    spacing: 9px;
}

QCheckBox::indicator {
    width: 19px;
    height: 19px;
    border-radius: 5px;
    border: 1.5px solid rgba(156,163,175,0.5);
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.85),
        stop:1 rgba(255,255,255,0.55));
}

QCheckBox::indicator:checked {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #fbbf24, stop:1 #f59e0b);
    border-color: #d97706;
}

/* ============================================================
   COMBOBOX — 毛玻璃下拉框
   ============================================================ */
QComboBox {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 11px;
    padding: 10px 15px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.75),
        stop:1 rgba(255,255,255,0.5));
    min-width: 100px;
    color: #111827;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #f59e0b;
}

QComboBox::drop-down {
    border: none;
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M3 5l3 3 3-3' fill='none' stroke='%23374151' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>");
}

QComboBox QAbstractItemView {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px;
    background-color: rgba(255,255,255,0.98);
    selection-background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(245,158,11,0.12),
        stop:1 rgba(245,158,11,0.08));
    selection-color: #78350f;
    padding: 6px;
    outline: none;
}

/* ============================================================
   TABLE — 毛玻璃数据表格
   ============================================================ */
QTableWidget {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.55),
        stop:1 rgba(255,255,255,0.35));
    border: 1px solid rgba(255,255,255,0.6);
    border-radius: 16px;
    gridline-color: rgba(0,0,0,0.03);
    selection-background-color: rgba(245,158,11,0.1);
    selection-color: #111827;
}

QTableWidget::item {
    padding: 10px 15px;
    border-bottom: 1px solid rgba(0,0,0,0.03);
    font-weight: 500;
}

QTableWidget::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(245,158,11,0.12),
        stop:1 rgba(245,158,11,0.06));
    color: #111827;
    font-weight: 600;
}

QHeaderView::section {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(252,253,255,0.8),
        stop:1 rgba(248,249,252,0.6));
    color: #4b5563;
    padding: 12px 15px;
    border: none;
    border-bottom: 2px solid rgba(245,158,11,0.25);
    font-weight: 800;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

QHeaderView::section:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(252,253,255,0.95),
        stop:1 rgba(250,251,254,0.8));
}

/* ============================================================
   DATE EDIT & CALENDAR — 毛玻璃日历
   ============================================================ */
QDateEdit, QDateTimeEdit {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 11px;
    padding: 10px 15px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.75),
        stop:1 rgba(255,255,255,0.5));
    color: #111827;
    font-weight: 500;
}

QDateEdit:focus, QDateTimeEdit:focus {
    border-color: #f59e0b;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.97),
        stop:1 rgba(255,255,255,0.85));
}

QDateEdit::drop-down, QDateTimeEdit::drop-down {
    border: none;
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
    image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M3 5l3 3 3-3' fill='none' stroke='%23374151' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>");
}

QCalendarWidget {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 14px;
}

QCalendarWidget QToolButton {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 700;
    font-size: 12px;
}

QCalendarWidget QToolButton:hover {
    background-color: rgba(245,158,11,0.08);
    border-color: #f59e0b;
}

QCalendarWidget QToolButton:pressed {
    background-color: rgba(245,158,11,0.14);
}

QCalendarWidget QToolButton::menu-indicator {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    left: 2px;
    image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M3 5l3 3 3-3' fill='none' stroke='%23374151' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    width: 14px;
    height: 14px;
}

QCalendarWidget QToolButton::menu-button {
    background-color: transparent;
    border: none;
}

QCalendarWidget QMenu {
    background-color: #ffffff;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 4px;
}

QCalendarWidget QMenu::item {
    padding: 7px 20px;
    color: #111827;
    border-radius: 7px;
    font-weight: 500;
}

QCalendarWidget QMenu::item:selected {
    background-color: rgba(245,158,11,0.12);
    color: #78350f;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #ffffff;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding: 8px;
}

QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid rgba(0,0,0,0.12);
    border-radius: 7px;
    padding: 4px 10px;
    font-weight: 600;
}

QCalendarWidget QSpinBox:hover {
    border-color: #f59e0b;
}

QCalendarWidget QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    border: none;
    border-left: 1px solid rgba(0,0,0,0.08);
    border-bottom: 1px solid rgba(0,0,0,0.05);
    image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'><path d='M2 7l3-3 3 3' fill='none' stroke='%23374151' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    width: 22px;
    border-top-right-radius: 7px;
}

QCalendarWidget QSpinBox::up-button:hover {
    background-color: rgba(245,158,11,0.1);
}

QCalendarWidget QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    border: none;
    border-left: 1px solid rgba(0,0,0,0.08);
    image: url("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 10 10'><path d='M2 4l3 3 3-3' fill='none' stroke='%23374151' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    width: 22px;
    border-bottom-right-radius: 7px;
}

QCalendarWidget QSpinBox::down-button:hover {
    background-color: rgba(245,158,11,0.1);
}

QCalendarWidget QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    selection-background-color: rgba(245,158,11,0.15);
    selection-color: #78350f;
    border: none;
    outline: none;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #d1d5db;
}

/* ============================================================
   SPINBOX
   ============================================================ */
QSpinBox, QDoubleSpinBox {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 11px;
    padding: 10px 15px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.75),
        stop:1 rgba(255,255,255,0.5));
    color: #111827;
    font-weight: 500;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #f59e0b;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.97),
        stop:1 rgba(255,255,255,0.85));
}

/* ============================================================
   TOOLTIP — 毛玻璃提示
   ============================================================ */
QToolTip {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.97),
        stop:1 rgba(248,249,252,0.92));
    color: #111827;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 12px;
    padding: 10px 16px;
    font-size: 12px;
    font-weight: 500;
}

/* ============================================================
   DIALOG & MESSAGE BOX
   ============================================================ */
QDialog {
    background-color: #ffffff;
    color: #111827;
}

QMessageBox {
    background-color: #ffffff;
    color: #111827;
}

QMessageBox QLabel {
    color: #111827;
    background: transparent;
}

QMessageBox QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f59e0b, stop:1 #d97706);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 28px;
    font-weight: 700;
    font-size: 12px;
    min-width: 80px;
}

QMessageBox QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d97706, stop:1 #b45309);
}

QMessageBox QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #b45309, stop:1 #92400e);
}

/* ============================================================
   TEXT BROWSER (Usage Tab)
   ============================================================ */
QTextBrowser {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.6),
        stop:1 rgba(255,255,255,0.35));
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: 18px;
    padding: 24px;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.7;
}

/* ============================================================
   IMAGE LABEL — 毛玻璃图片预览
   ============================================================ */
QLabel#imagePreview {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.55),
        stop:1 rgba(255,255,255,0.3));
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: 16px;
}

/* ============================================================
   TOOL BAR (ImageViewer)
   ============================================================ */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.8),
        stop:1 rgba(248,249,252,0.7));
    border-bottom: 1px solid rgba(0,0,0,0.05);
    padding: 4px;
    spacing: 6px;
}

QToolBar QToolButton {
    background: transparent;
    color: #4b5563;
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    font-weight: 600;
    font-size: 12px;
}

QToolBar QToolButton:hover {
    background: rgba(245,158,11,0.08);
    color: #1e293b;
}

QToolBar QToolButton:pressed {
    background: rgba(245,158,11,0.14);
}

/* ============================================================
   STATUS BAR
   ============================================================ */
QStatusBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(248,249,252,0.7),
        stop:1 rgba(255,255,255,0.6));
    border-top: 1px solid rgba(0,0,0,0.04);
    color: #6b7280;
    font-weight: 500;
    font-size: 11px;
    padding: 4px 12px;
}

/* ============================================================
   GRAPHICS VIEW (ImageViewer canvas)
   ============================================================ */
QGraphicsView {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(248,249,252,0.6),
        stop:1 rgba(240,242,247,0.4));
    border: none;
    border-radius: 12px;
}

/* ============================================================
   SPLITTER
   ============================================================ */
QSplitter::handle {
    background: rgba(0,0,0,0.04);
}

QSplitter::handle:hover {
    background: rgba(245,158,11,0.15);
}

/* ============================================================
   TAB WIDGET (备用)
   ============================================================ */
QTabWidget::pane {
    border: 1px solid rgba(255,255,255,0.7);
    border-radius: 16px;
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.5),
        stop:1 rgba(255,255,255,0.3));
}

QTabBar::tab {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.6),
        stop:1 rgba(248,249,252,0.4));
    color: #6b7280;
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 10px 10px 0 0;
    padding: 10px 22px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.85),
        stop:1 rgba(255,255,255,0.6));
    color: #1e293b;
    border-bottom: 2px solid #f59e0b;
}
"""
