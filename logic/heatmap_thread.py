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
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime, timedelta
from PyQt5.QtCore import QThread, pyqtSignal

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


class HeatmapThread(QThread):
    """热力云图绘制线程"""
    progress_updated = pyqtSignal(int)  # 进度更新信号
    status_updated = pyqtSignal(str)   # 状态更新信号
    image_ready = pyqtSignal(str, str)  # 图像准备就绪信号 (图像路径, 标题)
    finished = pyqtSignal(bool, str)   # 完成信号 (成功, 消息)
    
    def __init__(self, csv_file_path, output_dir=None, target=None, upper=None, lower=None):
        super().__init__()
        self.csv_file_path = csv_file_path
        self.output_dir = output_dir or os.path.dirname(csv_file_path)
        self.is_running = False
        self.target = target
        self.upper = upper
        self.lower = lower
        
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
                        import chardet
                        with open(self.csv_file_path, 'rb') as f:
                            raw = f.read()
                        detected = chardet.detect(raw)
                        enc = detected.get('encoding', 'utf-8') or 'utf-8'
                        try:
                            df = pd.read_csv(self.csv_file_path, index_col=0, encoding=enc)
                        except Exception:
                            df = pd.read_csv(self.csv_file_path, index_col=0, encoding='latin-1')
                
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
                # 尝试解析时间索引（支持 HH:MM:SS 和 HH_MM_SS 两种格式）
                time_index = []
                for time_str in df.index:
                    if ':' in str(time_str):
                        try:
                            parts = str(time_str).split(':')
                            time_index.append(datetime(2023, 1, 1, int(parts[0]), int(parts[1]), int(parts[2])))
                        except (ValueError, IndexError):
                            time_index.append(datetime(2023, 1, 1) + timedelta(minutes=len(time_index)))
                    elif '_' in str(time_str):
                        parts = str(time_str).split('_')
                        try:
                            time_index.append(datetime(2023, 1, 1, int(parts[0]), int(parts[1]), int(parts[2])))
                        except (ValueError, IndexError):
                            time_index.append(datetime(2023, 1, 1) + timedelta(minutes=len(time_index)))
                    else:
                        try:
                            time_index.append(pd.to_datetime(time_str))
                        except Exception:
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
                
                # 计算颜色映射范围
                data_mean = df.values.mean()
                
                use_custom_range = (self.target is not None and 
                                   self.upper is not None and 
                                   self.lower is not None)
                
                if use_custom_range:
                    vmin = self.lower
                    vmax = self.upper
                    target_val = self.target
                    self.status_updated.emit(f"使用自定义参数: Target={target_val}, 上限={vmax}, 下限={vmin}")
                else:
                    vmin = data_mean * 0.98
                    vmax = data_mean * 1.02
                    target_val = data_mean
                    self.status_updated.emit(f"使用默认参数: Target={target_val:.4f}, 上限={vmax:.4f}, 下限={vmin:.4f}")
                
                # 创建自定义颜色映射：下限=最蓝，target=绿色，上限=最红
                blue_pos = (target_val - vmin) / (vmax - vmin) if vmax != vmin else 0.5
                red_pos = 1.0
                
                if blue_pos <= 0 or blue_pos >= 1:
                    blue_pos = 0.3
                
                colors = [
                    (0.0, (0, 0, 1)),
                    (blue_pos, (0, 1, 0)),
                    (red_pos, (1, 0, 0))
                ]
                n_bins = 256
                cmap = LinearSegmentedColormap.from_list('heat_map', colors, N=n_bins)
                
                # 设置图形大小
                fig, ax = plt.subplots(figsize=(12, 8))
                
                # 绘制热力图
                im = ax.imshow(df.values, aspect='auto', cmap=cmap, origin='lower',
                              extent=[min(x_data), max(x_data), 0, max(1, len(df) - 1)],
                              vmin=vmin, vmax=vmax)
                
                # 设置Origin风格的坐标轴样式
                ax.set_xlabel('模头位置 (mm)', fontsize=12, fontweight='bold')
                ax.set_ylabel('时间', fontsize=12, fontweight='bold')

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
                    ax.set_xticklabels([f'{tick:.1f}' for tick in x_ticks], rotation=45, ha='right')

                # 左轴：真实时间（HH:MM:SS）
                n_rows = len(df)
                if n_rows > 1:
                    if n_rows <= 10:
                        step = 1
                    elif n_rows <= 30:
                        step = max(1, n_rows // 6)
                    else:
                        step = max(1, n_rows // 10)
                    y_ticks = list(range(0, n_rows, step))
                    if y_ticks[-1] != n_rows - 1 and n_rows - 1 - y_ticks[-1] >= step // 2:
                        y_ticks.append(n_rows - 1)
                    time_labels = []
                    for i in y_ticks:
                        try:
                            time_labels.append(df.index[i].strftime('%H:%M:%S'))
                        except Exception:
                            time_labels.append(str(df.index[i]))
                    ax.set_yticks(y_ticks)
                    ax.set_yticklabels(time_labels)

                # 添加颜色条，放在图外部右侧
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="3%", pad=0.8)
                cbar = plt.colorbar(im, cax=cax)
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