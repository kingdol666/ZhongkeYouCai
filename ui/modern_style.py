#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级毛玻璃质感 UI 样式表 — Glassmorphism Design System
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
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #e8ecf1, stop:0.5 #f0f2f5, stop:1 #e8ecf1);
}

/* ============================================================
   SIDEBAR
   ============================================================ */
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0f172a, stop:0.5 #111827, stop:1 #0f172a);
    border-right: 1px solid rgba(255,255,255,0.06);
}

QFrame#logoFrame {
    background: transparent;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

QLabel#logoTitle {
    color: #f1f5f9;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
    background: transparent;
}

QLabel#logoSubtitle {
    color: rgba(148,163,184,0.8);
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 1px;
    background: transparent;
    margin-top: 2px;
}

QFrame#sidebarSeparator {
    background: rgba(255,255,255,0.04);
    max-height: 1px;
    margin: 4px 16px;
}

QPushButton#navButton {
    background: transparent;
    color: rgba(203,213,225,0.85);
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
    background: rgba(255,255,255,0.06);
    color: #e2e8f0;
    border-left: 3px solid rgba(99,102,241,0.5);
}

QPushButton#navButton:checked {
    background: rgba(99,102,241,0.15);
    color: #ffffff;
    border-left: 3px solid #818cf8;
    font-weight: 600;
}

QPushButton#collapseButton {
    background: transparent;
    color: rgba(148,163,184,0.6);
    border: none;
    border-top: 1px solid rgba(255,255,255,0.04);
    text-align: center;
    padding: 14px;
    font-size: 12px;
    min-width: 0;
}

QPushButton#collapseButton:hover {
    background: rgba(255,255,255,0.04);
    color: #cbd5e1;
}

QFrame#contentFrame {
    background: transparent;
}

/* ============================================================
   GROUP BOX — Glass Card
   ============================================================ */
QGroupBox {
    font-weight: 600;
    font-size: 13px;
    color: #334155;
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 14px;
    margin-top: 16px;
    padding: 20px 16px 14px 16px;
    background-color: rgba(255,255,255,0.55);
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
    background: rgba(100,116,139,0.12);
    color: #475569;
    border: 1px solid rgba(100,116,139,0.2);
    font-weight: 500;
}

QPushButton#browseButton:hover {
    background: rgba(100,116,139,0.2);
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
    border: 1px solid rgba(203,213,225,0.8);
    border-radius: 8px;
    padding: 8px 14px;
    background-color: rgba(255,255,255,0.7);
    selection-background-color: #818cf8;
    color: #1e293b;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1.5px solid #818cf8;
    background-color: rgba(255,255,255,0.95);
}

QLineEdit:read-only {
    background-color: rgba(241,245,249,0.7);
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
    border: 1px solid rgba(255,255,255,0.6);
    border-radius: 12px;
    background-color: rgba(255,255,255,0.35);
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
    background-color: rgba(226,232,240,0.8);
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
    border: 1.5px solid rgba(148,163,184,0.6);
    background-color: rgba(255,255,255,0.7);
}

QCheckBox::indicator:checked {
    background-color: #6366f1;
    border-color: #6366f1;
}

/* ============================================================
   COMBOBOX
   ============================================================ */
QComboBox {
    border: 1px solid rgba(203,213,225,0.8);
    border-radius: 8px;
    padding: 8px 14px;
    background-color: rgba(255,255,255,0.7);
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
    border: 1px solid rgba(203,213,225,0.9);
    border-radius: 8px;
    background-color: rgba(255,255,255,0.95);
    selection-background-color: rgba(99,102,241,0.12);
    selection-color: #4338ca;
    padding: 4px;
}

/* ============================================================
   TABLE
   ============================================================ */
QTableWidget {
    background-color: rgba(255,255,255,0.5);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 12px;
    gridline-color: rgba(226,232,240,0.5);
    selection-background-color: rgba(99,102,241,0.12);
    selection-color: #1e293b;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(241,245,249,0.8);
}

QTableWidget::item:selected {
    background-color: rgba(99,102,241,0.1);
    color: #312e81;
}

QHeaderView::section {
    background-color: rgba(248,250,252,0.8);
    color: #475569;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid rgba(226,232,240,0.8);
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QHeaderView::section:hover {
    background-color: rgba(241,245,249,0.9);
}

/* ============================================================
   SPINBOX
   ============================================================ */
QSpinBox, QDoubleSpinBox {
    border: 1px solid rgba(203,213,225,0.8);
    border-radius: 8px;
    padding: 8px 14px;
    background-color: rgba(255,255,255,0.7);
    color: #1e293b;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #818cf8;
}

/* ============================================================
   TOOLTIP
   ============================================================ */
QToolTip {
    background: rgba(15,23,42,0.92);
    color: #f1f5f9;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
}

/* ============================================================
   TEXT BROWSER (Usage Tab)
   ============================================================ */
QTextBrowser {
    background-color: rgba(255,255,255,0.55);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 14px;
    padding: 20px;
    font-size: 13px;
    line-height: 1.7;
}

/* ============================================================
   IMAGE LABEL (Heatmap Preview)
   ============================================================ */
QLabel#imagePreview {
    background-color: rgba(255,255,255,0.6);
    border: 1px solid rgba(226,232,240,0.8);
    border-radius: 12px;
}
"""