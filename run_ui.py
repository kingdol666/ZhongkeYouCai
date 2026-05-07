#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV数据批处理工具启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主窗口
from ui.main_window import MainWindow
from ui.modern_style import MODERN_STYLE
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 应用全局现代风格样式
    app.setStyleSheet(MODERN_STYLE)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())