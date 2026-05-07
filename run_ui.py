#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中科优材 · 膜厚云图分析系统 — 启动脚本
"""

import sys
import os

# ============================================================
# !! 必须在任何 PyQt6 导入之前设置 Windows AppUserModelID !!
# 否则任务栏会一直显示 "Python"
# ============================================================
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ZhongkeYouCai.ThicknessAnalysis")
    except Exception:
        pass

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from ui.main_window import MainWindow
from ui.modern_style import MODERN_STYLE

if __name__ == "__main__":
    QCoreApplication.setApplicationName("厚度分析")
    QCoreApplication.setOrganizationName("ZhongkeYouCai")
    QCoreApplication.setOrganizationDomain("zhongkeyoucai.com")

    app = QApplication(sys.argv)
    app.setStyleSheet(MODERN_STYLE)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
