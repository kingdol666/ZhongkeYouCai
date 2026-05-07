#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级浅色 UI 样式表 — Light Design System
"""

MODERN_STYLE = """
/* ============================================================
   GLOBAL
   ============================================================ */
QWidget {
    font-family: 'Segoe UI', 'Microsoft YaHei', 'PingFang SC', sans-serif;
    font-size: 12px;
    color: #1e293b;
    background-color: transparent;
}

QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f8fafc, stop:1 #f1f5f9);
}

/* ============================================================
   SIDEBAR — Light Theme
   ============================================================ */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #f8fafc);
    border-right: 1px solid #e2e8f0;
}

QFrame#logoFrame {
    background: transparent;
    border-bottom: 1px solid #e2e8f0;
}

QLabel#logoTitle {
    color: #1e293b;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: transparent;
}

QLabel#logoSubtitle {
    color: #64748b;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 1px;
    background: transparent;
    margin-top: 2px;
}

QFrame#sidebarSeparator {
    background: #e2e8f0;
    max-height: 1px;
    margin: 4px 16px;
}

QPushButton#navButton {
    background: transparent;
    color: #475569;
    border: none;
    border-left: 3px solid transparent;
    text-align: left;
    padding: 13px 18px;
    margin: 2px 8px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
}

QPushButton#navButton:hover {
    background: rgba(99,102,241,0.06);
    color: #1e293b;
    border-left: 3px solid rgba(99,102,241,0.4);
}

QPushButton#navButton:checked {
    background: rgba(99,102,241,0.1);
    color: #4338ca;
    border-left: 3px solid #6366f1;
    font-weight: 600;
}

QPushButton#collapseButton {
    background: transparent;
    color: #94a3b8;
    border: none;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    padding: 14px;
    font-size: 12px;
    min-width: 0;
}

QPushButton#collapseButton:hover {
    background: rgba(99,102,241,0.06);
    color: #475569;
}

QFrame#contentFrame {
    background: transparent;
}

/* ============================================================
   GROUP BOX — Light Card
   ============================================================ */
QGroupBox {
    font-weight: 600;
    font-size: 13px;
    color: #334155;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    margin-top: 16px;
    padding: 20px 16px 14px 16px;
    background-color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 18px;
    padding: 0 10px;
    color: #6366f1;
    font-size: 13px;
    font-weight: 700;
}

/* ============================================================
   BUTTONS
   ============================================================ */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #6366f1, stop:1 #4f46e5);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    font-weight: 600;
    font-size: 12px;
    min-width: 80px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #5558e6, stop:1 #4338ca);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #4f46e5, stop:1 #3730a3);
}

QPushButton:disabled {
    background: #cbd5e1;
    color: #94a3b8;
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
    background: #f1f5f9;
    color: #475569;
    border: 1px solid #e2e8f0;
    font-weight: 500;
}

QPushButton#browseButton:hover {
    background: #e2e8f0;
    color: #1e293b;
}

QPushButton#histDeleteButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f43f5e, stop:1 #e11d48);
}

/* ============================================================
   INPUTS
   ============================================================ */
QLineEdit, QTextEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    background-color: #ffffff;
    selection-background-color: #818cf8;
    color: #1e293b;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1.5px solid #818cf8;
    background-color: #ffffff;
}

QLineEdit:read-only {
    background-color: #f8fafc;
    color: #64748b;
}

/* ============================================================
   LABELS
   ============================================================ */
QLabel {
    color: #334155;
    font-weight: 500;
    background: transparent;
}

/* ============================================================
   SCROLL AREA & BARS
   ============================================================ */
QScrollArea {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    background-color: #ffffff;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background: rgba(148,163,184,0.4);
    border-radius: 4px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(100,116,139,0.6);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
    margin: 2px 4px;
}

QScrollBar::handle:horizontal {
    background: rgba(148,163,184,0.4);
    border-radius: 4px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(100,116,139,0.6);
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
QProgressBar {
    border: none;
    border-radius: 8px;
    text-align: center;
    background-color: #e2e8f0;
    color: #475569;
    font-weight: 600;
    height: 10px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6366f1, stop:1 #818cf8);
    border-radius: 8px;
}

/* ============================================================
   CHECKBOX
   ============================================================ */
QCheckBox {
    color: #334155;
    font-weight: 500;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1.5px solid #cbd5e1;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

/* ============================================================
   COMBOBOX
   ============================================================ */
QComboBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    background-color: #ffffff;
    min-width: 100px;
    color: #1e293b;
}

QComboBox:hover {
    border-color: #818cf8;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    background-color: #ffffff;
    selection-background-color: rgba(99,102,241,0.12);
    selection-color: #4338ca;
    padding: 4px;
}

/* ============================================================
   TABLE
   ============================================================ */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    gridline-color: #f1f5f9;
    selection-background-color: rgba(99,102,241,0.12);
    selection-color: #1e293b;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background-color: rgba(99,102,241,0.1);
    color: #312e81;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:hover {
    background-color: #f1f5f9;
}

/* ============================================================
   DATE EDIT & CALENDAR POPUP — White Background
   ============================================================ */
QDateEdit, QDateTimeEdit {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    background-color: #ffffff;
    color: #1e293b;
}

QDateEdit:focus, QDateTimeEdit:focus {
    border-color: #818cf8;
}

QDateEdit::drop-down, QDateTimeEdit::drop-down {
    border: none;
    width: 28px;
}

QCalendarWidget {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}

QCalendarWidget QToolButton {
    background-color: #ffffff;
    color: #1e293b;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 600;
    font-size: 12px;
}

QCalendarWidget QToolButton:hover {
    background-color: #f1f5f9;
}

QCalendarWidget QToolButton::menu-indicator {
    subcontrol-origin: padding;
    subcontrol-position: center;
}

QCalendarWidget QMenu {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 4px;
}

QCalendarWidget QMenu::item {
    padding: 6px 16px;
    color: #1e293b;
    border-radius: 4px;
}

QCalendarWidget QMenu::item:selected {
    background-color: rgba(99,102,241,0.12);
    color: #4338ca;
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    padding: 4px;
}

QCalendarWidget QSpinBox {
    background-color: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 2px 6px;
}

QCalendarWidget QSpinBox::up-button,
QCalendarWidget QSpinBox::down-button {
    background-color: transparent;
    border: none;
}

QCalendarWidget QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    selection-background-color: rgba(99,102,241,0.15);
    selection-color: #4338ca;
    border: none;
    outline: none;
}

QCalendarWidget QAbstractItemView:disabled {
    color: #cbd5e1;
}

/* ============================================================
   SPINBOX
   ============================================================ */
QSpinBox, QDoubleSpinBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    background-color: #ffffff;
    color: #1e293b;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #818cf8;
}

/* ============================================================
   TOOLTIP
   ============================================================ */
QToolTip {
    background: #ffffff;
    color: #1e293b;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ============================================================
   TEXT BROWSER (Usage Tab)
   ============================================================ */
QTextBrowser {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 20px;
    font-size: 13px;
    line-height: 1.7;
}

/* ============================================================
   IMAGE LABEL (Heatmap Preview)
   ============================================================ */
QLabel#imagePreview {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
"""
