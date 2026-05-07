#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热力云图绘制线程类
"""

import os
import numpy as np
import pandas as pd
import matplotlib
# 使用非交互式后端，避免在非主线程中使用GUI
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import AutoMinorLocator
from datetime import datetime, timedelta
from PyQt6.QtCore import QThread, pyqtSignal

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class HeatmapThread(QThread):
    """热力云图绘制线程"""
    progress_updated = pyqtSignal(int)  # 进度更新信号
    status_updated = pyqtSignal(str)   # 状态更新信号
    image_ready = pyqtSignal(str, str)  # 图像准备就绪信号 (图像路径, 标题)
    finished = pyqtSignal(bool, str)   # 完成信号 (成功, 消息)
    
    def __init__(self, csv_file_path, output_dir=None):
        super().__init__()
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir or os.path.dirname(csv_file_path)
        self.is_running = False
        
    def run(self):
        """执行热力云图绘制"""
        self.is_running = True
        
        try:
            self.status_updated.emit(f"开始处理文件: {os.path.basename(self.csv_file_path)}")
            
            # 读取CSV文件
            try:
                # 尝试使用UTF-8编码读取，如果失败则尝试GBK编码
                try:
                    df = pd.read_csv(self.csv_file_path, index_col=0, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(self.csv_file_path, index_col=0, encoding='gbk')
                    except UnicodeDecodeError:
                        # 如果都失败，尝试自动检测编码
                        import chardet
                        with open(self.csv_file_path, 'rb') as f:
                            result = chardet.detect(f.read())
                        df = pd.read_csv(self.csv_file_path, index_col=0, encoding=result['encoding'])
                
                self.status_updated.emit(f"成功读取CSV文件，数据形状: {df.shape}")
            except Exception as e:
                self.finished.emit(False, f"读取CSV文件失败: {str(e)}")
                return
                
            # 检查数据格式
            if df.empty:
                self.finished.emit(False, "CSV文件为空")
                return
                
            # 确保输出目录存在
            os.makedirs(self.output_dir, exist_ok=True)
            
            # 解析时间索引
            try:
                # 尝试解析时间索引
                time_index = []
                for time_str in df.index:
                    # 假设时间格式为 HH_MM_SS 或类似格式
                    if '_' in time_str:
                        parts = time_str.split('_')
                        if len(parts) >= 3:
                            hour, minute, second = int(parts[0]), int(parts[1]), int(parts[2])
                            time_index.append(datetime(2023, 1, 1, hour, minute, second))
                        else:
                            # 如果格式不符合预期，使用序号
                            time_index.append(datetime(2023, 1, 1) + timedelta(minutes=len(time_index)))
                    else:
                        # 如果没有下划线，尝试直接解析
                        try:
                            time_index.append(pd.to_datetime(time_str))
                        except:
                            time_index.append(datetime(2023, 1, 1) + timedelta(minutes=len(time_index)))
                            
                # 使用解析后的时间索引
                df.index = time_index
                self.status_updated.emit(f"成功解析时间索引")
            except Exception as e:
                self.status_updated.emit(f"时间索引解析失败，使用原始索引: {str(e)}")
                
            # 获取位置数据（列名）
            try:
                # 尝试将列名转换为浮点数
                positions = []
                for col in df.columns:
                    try:
                        pos = float(col)
                        positions.append(pos)
                    except:
                        # 如果转换失败，使用列索引
                        positions.append(df.columns.get_loc(col))
                        
                # 使用位置数据作为x轴
                x_data = positions
                self.status_updated.emit(f"成功解析位置数据，范围: {min(x_data):.2f} - {max(x_data):.2f}")
            except Exception as e:
                self.status_updated.emit(f"位置数据解析失败，使用列索引: {str(e)}")
                x_data = list(range(len(df.columns)))
                
            # 创建热力图
            try:
                self.progress_updated.emit(30)
                self.status_updated.emit("正在创建热力图...")
                
                # 设置图形大小
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # 创建自定义颜色映射
                colors = ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
                n_bins = 100
                cmap = LinearSegmentedColormap.from_list('heat_map', colors, N=n_bins)
                
                # 绘制热力图
                im = ax.imshow(df.values, aspect='auto', cmap=cmap, origin='lower',
                              extent=[min(x_data), max(x_data), 0, max(1, len(df) - 1)])
                
                # 设置Origin风格的坐标轴样式
                ax.set_xlabel('模头位置 (mm)', fontsize=12, fontweight='bold')
                ax.set_ylabel('时间点', fontsize=12, fontweight='bold')
                
                # 设置坐标轴线条样式
                ax.spines['top'].set_linewidth(1.5)
                ax.spines['bottom'].set_linewidth(1.5)
                ax.spines['left'].set_linewidth(1.5)
                ax.spines['right'].set_linewidth(1.5)
                ax.spines['top'].set_color('black')
                ax.spines['bottom'].set_color('black')
                ax.spines['left'].set_color('black')
                ax.spines['right'].set_color('black')
                
                # 添加次要刻度（Origin风格的重要特征）
                ax.xaxis.set_minor_locator(AutoMinorLocator())
                ax.yaxis.set_minor_locator(AutoMinorLocator())
                
                # 设置刻度样式
                ax.tick_params(axis='both', which='major', labelsize=10, width=1.2, length=6, 
                              direction='inout', color='black')
                ax.tick_params(axis='both', which='minor', width=1, length=3, 
                              direction='in', color='black')
                
                # 添加网格线（Origin风格通常有清晰的网格）
                ax.grid(True, linestyle='--', alpha=0.7, color='gray', linewidth=0.5)
                ax.grid(which='minor', linestyle=':', alpha=0.5, color='gray', linewidth=0.3)
                
                # 设置x轴刻度
                if len(x_data) > 10:
                    step = len(x_data) // 10
                    x_ticks = [x_data[i] for i in range(0, len(x_data), step)]
                    ax.set_xticks(x_ticks)
                    # 优化x轴标签显示
                    ax.set_xticklabels([f'{tick:.1f}' for tick in x_ticks], rotation=45, ha='right')
                
                # 设置y轴为时间格式
                if all(isinstance(t, datetime) for t in df.index):
                    # 格式化时间显示
                    time_fmt = mdates.DateFormatter('%H:%M:%S')
                    ax.yaxis.set_major_formatter(time_fmt)
                    
                    # 设置y轴刻度
                    if len(df.index) > 10:
                        step = len(df.index) // 10
                        y_ticks = list(range(0, len(df.index), step))
                        ax.set_yticks(y_ticks)
                        ax.set_yticklabels([df.index[i].strftime('%H:%M:%S') for i in y_ticks])
                else:
                    # 如果不是datetime对象，使用原始索引
                    if len(df.index) > 10:
                        step = len(df.index) // 10
                        y_ticks = list(range(0, len(df.index), step))
                        ax.set_yticks(y_ticks)
                        ax.set_yticklabels([str(df.index[i]) for i in y_ticks])
                
                # 添加颜色条，优化样式
                cbar = plt.colorbar(im, ax=ax, shrink=0.85, aspect=20)
                cbar.set_label('厚度值', fontsize=11, fontweight='bold')
                cbar.ax.tick_params(labelsize=10, width=1, length=5, direction='in')
                
                # 设置标题，优化样式
                file_name = os.path.basename(self.csv_file_path)
                title = f"热力云图 - {file_name}"
                ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
                
                # 调整布局，确保所有元素清晰可见
                plt.tight_layout(pad=2.0)
                
                self.progress_updated.emit(70)
                self.status_updated.emit("正在保存图像...")
                
                # 保存图像
                output_image_path = os.path.join(self.output_dir, f"heatmap_{os.path.splitext(file_name)[0]}.png")
                plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
                plt.close()  # 关闭图形，释放内存
                
                self.progress_updated.emit(100)
                self.status_updated.emit(f"热力图已保存到: {output_image_path}")
                
                # 发出图像准备就绪信号
                self.image_ready.emit(output_image_path, title)
                
                self.finished.emit(True, f"热力图绘制完成: {output_image_path}")
                
            except Exception as e:
                self.finished.emit(False, f"创建热力图失败: {str(e)}")
                
        except Exception as e:
            self.finished.emit(False, f"处理过程中发生错误: {str(e)}")
            
    def stop(self):
        """停止处理"""
        self.is_running = False