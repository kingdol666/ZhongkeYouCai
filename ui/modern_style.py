#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级毛玻璃质感 UI 样式表 — 浅色黄主题 Glassmorphism Design System
"""

MODERN_STYLE = """
/* ============================================================
   GLOBAL
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
        stop:0 #fdfdfd, stop:0.3 #fafbfd, stop:0.7 #f6f8fb, stop:1 #f2f5f9);
}

QMainWindow::separator {
    width: 0px;
    height: 0px;
}

/* ============================================================
   SIDEBAR — Light Frosted Glass
   ============================================================ */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255,255,255,0.88), stop:0.3 rgba(252,252,254,0.9),
        stop:0.7 rgba(250,251,254,0.88), stop:1 rgba(248,249,252,0.85));
    border-right: 1px solid rgba(0,0,0,0.06);
}

QFrame#logoFrame {
    background: transparent;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

QLabel#logoTitle {
    color: #111827;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.5px;
    background: transparent;
}

QLabel#logoSubtitle {
    color: rgba(107,114,128,0.8);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.5px;
    background: transparent;
    margin-top: 2px;
}

QFrame#sidebarSeparator {
    background: rgba(0,0,0,0.05);
    max-height: 1px;
    margin: 4px 16px;
}

QPushButton#navButton {
    background: transparent;
    color: #374151;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 12px 18px;
    margin: 2px 10px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 10px;
}

QPushButton#navButton:hover {
    background: rgba(245,158,11,0.06);
    color: #111827;
    border-left: 3px solid rgba(245,158,11,0.5);
}

QPushButton#navButton:checked {
    background: rgba(245,158,11,0.1);
    color: #111827;
    border-left: 3px solid #f59e0b;
    font-weight: 700;
}

QPushButton#collapseButton {
    background: transparent;
    color: rgba(107,114,128,0.5);
    border: none;
    border-top: 1px solid rgba(0,0,0,0.05);
    text-align: center;
    padding: 14px;
    font-size: 12px;
    font-weight: 600;
    min-width: 0;
}

QPushButton#collapseButton:hover {
    background: rgba(0,0,0,0.03);
    color: #374151;
}

QFrame#contentFrame {
    background: transparent;
}

/* ============================================================
   GROUP BOX — Frosted Glass Card
   ============================================================ */
QGroupBox {
    font-weight: 700;
    font-size: 13px;
    color: #111827;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 16px;
    margin-top: 18px;
    padding: 22px 16px 16px 16px;
    background-color: rgba(255,255,255,0.55);
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 20px;
    padding: 0 12px;
    color: #d97706;
    font-size: 13px;
    font-weight: 800;
}

/* ============================================================
   BUTTONS
   ============================================================ */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f59e0b, stop:1 #d97706);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 700;
    font-size: 12px;
    min-width: 80px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #d97706, stop:1 #b45309);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #b45309, stop:1 #92400e);
}

QPushButton:disabled {
    background: #d1d5db;
    color: #9ca3af;
}

QPushButton#stopButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f43f5e, stop:1 #e11d48);
}

QPushButton#stopButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #e11d48, stop:1 #be123c);
}

QPushButton#browseButton {
    background: rgba(245,158,11,0.06);
    color: #374151;
    border: 1px solid rgba(245,158,11,0.2);
    font-weight: 600;
    border-radius: 10px;
}

QPushButton#browseButton:hover {
    background: rgba(245,158,11,0.12);
    color: #111827;
    border-color: rgba(245,158,11,0.4);
}

QPushButton#histDeleteButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f43f5e, stop:1 #e11d48);
}

/* ============================================================
   INPUTS — Glass Feel
   ============================================================ */
QLineEdit, QTextEdit {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 9px 14px;
    background-color: rgba(255,255,255,0.7);
    selection-background-color: #fde68a;
    color: #111827;
    font-weight: 500;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1.5px solid #f59e0b;
    background-color: rgba(255,255,255,0.95);
}

QLineEdit:read-only {
    background-color: rgba(250,250,252,0.6);
    color: #374151;
}

QLineEdit:read-only:focus {
    border-color: rgba(0,0,0,0.1);
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
   SCROLL AREA & BARS
   ============================================================ */
QScrollArea {
    border: 1px solid rgba(0,0,0,0.05);
    border-radius: 14px;
    background-color: rgba(255,255,255,0.35);
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 7px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: rgba(156,163,175,0.35);
    border-radius: 4px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(107,114,128,0.55);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 7px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background: rgba(156,163,175,0.35);
    border-radius: 4px;
    min-width: 28px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(107,114,128,0.55);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
QProgressBar {
    border: none;
    border-radius: 10px;
    text-align: center;
    background-color: rgba(229,231,235,0.7);
    color: #374151;
    font-weight: 700;
    font-size: 10px;
    height: 12px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #f59e0b, stop:0.5 #fbbf24, stop:1 #fcd34d);
    border-radius: 10px;
}

/* ============================================================
   CHECKBOX
   ============================================================ */
QCheckBox {
    color: #111827;
    font-weight: 600;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid rgba(156,163,175,0.5);
    background-color: rgba(255,255,255,0.7);
}

QCheckBox::indicator:checked {
    background-color: #f59e0b;
    border-color: #d97706;
}

/* ============================================================
   COMBOBOX
   ============================================================ */
QComboBox {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 9px 14px;
    background-color: rgba(255,255,255,0.7);
    min-width: 100px;
    color: #111827;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #f59e0b;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    background-color: rgba(255,255,255,0.98);
    selection-background-color: rgba(245,158,11,0.12);
    selection-color: #92400e;
    padding: 6px;
    outline: none;
}

/* ============================================================
   TABLE — Glass Card Table
   ============================================================ */
QTableWidget {
    background-color: rgba(255,255,255,0.5);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 14px;
    gridline-color: rgba(0,0,0,0.04);
    selection-background-color: rgba(245,158,11,0.1);
    selection-color: #111827;
}

QTableWidget::item {
    padding: 9px 14px;
    border-bottom: 1px solid rgba(0,0,0,0.04);
    font-weight: 500;
}

QTableWidget::item:selected {
    background-color: rgba(245,158,11,0.1);
    color: #111827;
    font-weight: 600;
}

QHeaderView::section {
    background-color: rgba(252,252,254,0.75);
    color: #374151;
    padding: 11px 14px;
    border: none;
    border-bottom: 2px solid rgba(245,158,11,0.3);
    font-weight: 800;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:hover {
    background-color: rgba(250,250,252,0.9);
}

/* ============================================================
   DATE EDIT & CALENDAR — Glass Style
   ============================================================ */
QDateEdit, QDateTimeEdit {
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 9px 14px;
    background-color: rgba(255,255,255,0.7);
    color: #111827;
    font-weight: 500;
}

QDateEdit:focus, QDateTimeEdit:focus {
    border-color: #f59e0b;
    background-color: rgba(255,255,255,0.95);
}

QDateEdit::drop-down, QDateTimeEdit::drop-down {
    border: none;
    width: 28px;
}

QCalendarWidget {
    background-color: rgba(255,255,255,0.99);
    color: #111827;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 12px;
}

QCalendarWidget QToolButton {
    background-color: transparent;
    color: #111827;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 700;
    font-size: 12px;
}

QCalendarWidget QToolButton:hover {
    background-color: rgba(245,158,11,0.08);
}

QCalendarWidget QToolButton::menu-indicator {
    subcontrol-origin: padding;
    subcontrol-position: center;
}

QCalendarWidget QMenu {
    background-color: rgba(255,255,255,0.99);
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 8px;
    padding: 4px;
}

QCalendarWidget QMenu::item {
    padding: 6px 18px;
    color: #111827;
    border-radius: 6px;
    font-weight: 500;
}

QCalendarWidget QMenu::item:selected {
    background-color: rgba(245,158,11,0.12);
    color: #92400e;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: transparent;
    border-bottom: 1px solid rgba(0,0,0,0.08);
    padding: 6px;
}

QCalendarWidget QSpinBox {
    background-color: rgba(255,255,255,0.85);
    color: #111827;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 6px;
    padding: 3px 8px;
    font-weight: 500;
}

QCalendarWidget QSpinBox::up-button,
QCalendarWidget QSpinBox::down-button {
    background-color: transparent;
    border: none;
}

QCalendarWidget QAbstractItemView {
    background-color: transparent;
    color: #111827;
    selection-background-color: rgba(245,158,11,0.15);
    selection-color: #92400e;
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
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    padding: 9px 14px;
    background-color: rgba(255,255,255,0.7);
    color: #111827;
    font-weight: 500;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #f59e0b;
    background-color: rgba(255,255,255,0.95);
}

/* ============================================================
   TOOLTIP
   ============================================================ */
QToolTip {
    background: rgba(255,255,255,0.96);
    color: #111827;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 500;
}

/* ============================================================
   DIALOG & MESSAGE BOX — Light Theme
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
    background-color: rgba(255,255,255,0.55);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 16px;
    padding: 22px;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.7;
}

/* ============================================================
   IMAGE LABEL (Heatmap Preview)
   ============================================================ */
QLabel#imagePreview {
    background-color: rgba(255,255,255,0.55);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 14px;
}
"""
