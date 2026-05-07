#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理线程模块
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import AutoMinorLocator
from mpl_toolkits.axes_grid1 import make_axes_locatable
from datetime import datetime, timedelta
from PyQt6.QtCore import QThread, pyqtSignal

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def parse_time_from_filename(filename):
    """
    从文件名中解析时间
    
    Args:
        filename: 文件名，格式为 "时_分_秒_序号.CSV"
        
    Returns:
        时间字符串，格式为 "时:分:秒"
    """
    # 使用正则表达式提取时间部分
    match = re.match(r'(\d+)_(\d+)_(\d+)_(\d+)\.CSV', filename)
    if match:
        hour, minute, second, _ = match.groups()
        return f"{hour}:{minute}:{second}"
    return "00:00:00"


class DataProcessorThread(QThread):
    """数据处理线程"""
    progress_updated = pyqtSignal(int)  # 进度更新信号
    status_updated = pyqtSignal(str)   # 状态更新信号
    finished = pyqtSignal(bool, str)   # 完成信号 (成功, 消息)
    
    def __init__(self, input_folder, output_folder, start_row, end_row, start_pos, end_pos):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.start_row = start_row
        self.end_row = end_row
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_running = False
        
    def calculate_position_columns(self, num_points):
        """
        计算位置列名，从start_pos到end_pos平均分配
        
        Args:
            num_points: 位置点的数量
            
        Returns:
            位置列名列表
        """
        step = (self.end_pos - self.start_pos) / (num_points - 1)
        positions = [round(self.start_pos + i * step, 2) for i in range(num_points)]
        return positions
        
    def run(self):
        """执行数据处理"""
        self.is_running = True
        
        try:
            # 确保输出目录存在
            os.makedirs(self.output_folder, exist_ok=True)
            
            # 获取所有子文件夹
            subdirs = [d for d in os.listdir(self.input_folder) if os.path.isdir(os.path.join(self.input_folder, d))]
            total_subdirs = len(subdirs)
            
            if total_subdirs == 0:
                self.finished.emit(False, "输入文件夹中没有子文件夹")
                return
                
            # 计算数据点数量
            num_data_points = self.end_row - self.start_row + 1
            
            # 计算位置列名
            position_columns = self.calculate_position_columns(num_data_points)
            
            processed_count = 0
            
            # 处理每个子文件夹
            for i, subdir in enumerate(subdirs):
                if not self.is_running:
                    break
                    
                subdir_path = os.path.join(self.input_folder, subdir)
                self.status_updated.emit(f"处理子文件夹: {subdir}")
                
                # 获取所有CSV文件
                csv_files = [f for f in os.listdir(subdir_path) if f.endswith('.CSV')]
                csv_files.sort()  # 按文件名排序
                
                if not csv_files:
                    self.status_updated.emit(f"  子文件夹 {subdir} 中没有CSV文件")
                    continue
                    
                # 创建DataFrame来存储合并后的数据
                # 行为时间，列为位置
                merged_data = pd.DataFrame(columns=position_columns)
                valid_files = 0
                
                # 处理每个CSV文件
                for csv_file in csv_files:
                    if not self.is_running:
                        break
                        
                    csv_path = os.path.join(subdir_path, csv_file)
                    
                    # 从文件名解析时间
                    time_str = parse_time_from_filename(csv_file)
                    
                    # 读取CSV文件，跳过前start_row-1行，只读取num_data_points行数据
                    # 尝试使用UTF-8编码读取，如果失败则尝试GBK编码
                    try:
                        df = pd.read_csv(csv_path, skiprows=self.start_row-1, header=None, names=['pos', 'bw'], nrows=num_data_points, encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            df = pd.read_csv(csv_path, skiprows=self.start_row-1, header=None, names=['pos', 'bw'], nrows=num_data_points, encoding='gbk')
                        except UnicodeDecodeError:
                            # 如果都失败，尝试自动检测编码
                            import chardet
                            with open(csv_path, 'rb') as f:
                                result = chardet.detect(f.read())
                            df = pd.read_csv(csv_path, skiprows=self.start_row-1, header=None, names=['pos', 'bw'], nrows=num_data_points, encoding=result['encoding'])
                    
                    # 确保数据点数量匹配
                    if len(df) != num_data_points:
                        self.status_updated.emit(f"  跳过: 文件 {csv_file} 的数据点数量 ({len(df)}) 与预期 ({num_data_points}) 不匹配")
                        continue
                    
                    # 将厚度数据添加到合并的DataFrame中，作为一行
                    # 使用时间作为行索引
                    merged_data.loc[time_str] = df['bw'].values
                    valid_files += 1
                
                # 保存合并后的数据到新的CSV文件
                if valid_files > 0:
                    output_file = os.path.join(self.output_folder, f"merged_{subdir}.csv")
                    # 使用UTF-8编码保存，并添加BOM以支持Excel正确显示中文
                    merged_data.to_csv(output_file, encoding='utf-8-sig')
                    self.status_updated.emit(f"  已保存合并数据到: {output_file} (处理了 {valid_files} 个文件)")
                else:
                    self.status_updated.emit(f"  子文件夹 {subdir} 中没有有效文件")
                
                processed_count += 1
                progress = int((i + 1) / total_subdirs * 100)
                self.progress_updated.emit(progress)
                
            if self.is_running:
                self.finished.emit(True, f"处理完成! 共处理了 {processed_count} 个子文件夹")
            else:
                self.finished.emit(False, "处理已取消")
                
        except Exception as e:
            self.finished.emit(False, f"处理过程中发生错误: {str(e)}")
            
    def stop(self):
        """停止处理"""
        self.is_running = False


class SingleFolderProcessorThread(QThread):
    """单文件夹处理线程：合并CSV + 自动生成热力云图"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    image_ready = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, folder_path, output_folder, start_row, end_row, start_pos, end_pos):
        super().__init__()
        self.folder_path = folder_path
        self.output_folder = output_folder
        self.start_row = start_row
        self.end_row = end_row
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.is_running = False

    def _calculate_position_columns(self, num_points):
        step = (self.end_pos - self.start_pos) / (num_points - 1)
        return [round(self.start_pos + i * step, 2) for i in range(num_points)]

    def _read_csv_with_encoding(self, csv_path, num_data_points):
        for enc in ('utf-8', 'gbk'):
            try:
                return pd.read_csv(csv_path, skiprows=self.start_row - 1,
                                   header=None, names=['pos', 'bw'],
                                   nrows=num_data_points, encoding=enc)
            except UnicodeDecodeError:
                continue
        import chardet
        with open(csv_path, 'rb') as f:
            result = chardet.detect(f.read())
        return pd.read_csv(csv_path, skiprows=self.start_row - 1,
                           header=None, names=['pos', 'bw'],
                           nrows=num_data_points, encoding=result['encoding'])

    def _merge_csv_files(self):
        """合并文件夹下所有CSV，返回 (merged_csv_path, valid_files_count)"""
        csv_files = sorted(f for f in os.listdir(self.folder_path) if f.upper().endswith('.CSV'))
        if not csv_files:
            return None, 0

        num_data_points = self.end_row - self.start_row + 1
        position_columns = self._calculate_position_columns(num_data_points)
        merged_data = pd.DataFrame(columns=position_columns)
        valid_files = 0

        for i, csv_file in enumerate(csv_files):
            if not self.is_running:
                return None, 0
            csv_path = os.path.join(self.folder_path, csv_file)
            time_str = parse_time_from_filename(csv_file)

            try:
                df = self._read_csv_with_encoding(csv_path, num_data_points)
            except Exception as e:
                self.status_updated.emit(f"  跳过: {csv_file} 读取失败 ({e})")
                continue

            if len(df) != num_data_points:
                self.status_updated.emit(
                    f"  跳过: {csv_file} 数据点 ({len(df)}) 与预期 ({num_data_points}) 不匹配")
                continue

            merged_data.loc[time_str] = df['bw'].values
            valid_files += 1

            progress = int((i + 1) / len(csv_files) * 50)
            self.progress_updated.emit(progress)

        if valid_files == 0:
            return None, 0

        folder_name = os.path.basename(self.folder_path) or "output"
        output_file = os.path.join(self.output_folder, f"merged_{folder_name}.csv")
        merged_data.to_csv(output_file, encoding='utf-8-sig')
        self.status_updated.emit(f"已保存合并数据: {output_file} ({valid_files} 个文件)")
        return output_file, valid_files

    def _generate_heatmap(self, csv_path):
        """根据合并后的CSV生成热力云图"""
        try:
            df = pd.read_csv(csv_path, index_col=0, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, index_col=0, encoding='gbk')

        if df.empty:
            return None

        # 解析时间索引
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
        df.index = time_index

        # 解析位置列
        positions = []
        for col in df.columns:
            try:
                positions.append(float(col))
            except ValueError:
                positions.append(df.columns.get_loc(col))

        self.progress_updated.emit(70)
        self.status_updated.emit("正在生成热力云图...")

        fig, ax = plt.subplots(figsize=(12, 8))
        colors = ['#0000FF', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000']
        cmap = LinearSegmentedColormap.from_list('heat_map', colors, N=100)

        im = ax.imshow(df.values, aspect='auto', cmap=cmap, origin='lower',
                       extent=[min(positions), max(positions), 0, max(1, len(df) - 1)])

        ax.set_xlabel('模头位置 (mm)', fontsize=12, fontweight='bold')
        ax.set_ylabel('时间', fontsize=12, fontweight='bold')
        for spine in ax.spines.values():
            spine.set_linewidth(1.5)
            spine.set_color('black')
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(axis='both', which='major', labelsize=10, width=1.2, length=6,
                       direction='inout', color='black')
        ax.tick_params(axis='both', which='minor', width=1, length=3,
                       direction='in', color='black')
        ax.grid(True, linestyle='--', alpha=0.7, color='gray', linewidth=0.5)
        ax.grid(which='minor', linestyle=':', alpha=0.5, color='gray', linewidth=0.3)

        if len(positions) > 10:
            step = len(positions) // 10
            x_ticks = [positions[i] for i in range(0, len(positions), step)]
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([f'{t:.1f}' for t in x_ticks], rotation=45, ha='right')

        # 左轴：真实时间
        n_rows = len(df)
        if n_rows > 10:
            step = max(1, n_rows // 10)
            y_ticks = list(range(0, n_rows, step))
            time_labels = []
            for i in y_ticks:
                try:
                    time_labels.append(df.index[i].strftime('%H:%M:%S'))
                except Exception:
                    time_labels.append(str(df.index[i]))
            ax.set_yticks(y_ticks)
            ax.set_yticklabels(time_labels)

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="3%", pad=0.8)
        cbar = plt.colorbar(im, cax=cax)
        cbar.set_label('厚度值', fontsize=11, fontweight='bold')
        cbar.ax.tick_params(labelsize=10, width=1, length=5, direction='in')

        folder_name = os.path.basename(self.folder_path) or "output"
        title = f"热力云图 - {folder_name}"
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout(pad=2.0)

        output_image_path = os.path.join(self.output_folder, f"heatmap_{folder_name}.png")
        plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
        plt.close()

        return output_image_path, title

    def run(self):
        self.is_running = True
        try:
            os.makedirs(self.output_folder, exist_ok=True)

            if not os.path.isdir(self.folder_path):
                self.finished.emit(False, f"文件夹不存在: {self.folder_path}")
                return

            self.status_updated.emit(f"开始处理文件夹: {self.folder_path}")
            self.progress_updated.emit(5)

            # Step 1: 合并CSV
            csv_path, valid_count = self._merge_csv_files()
            if not csv_path:
                self.finished.emit(False, "没有有效的CSV文件可处理")
                return

            if not self.is_running:
                self.finished.emit(False, "处理已取消")
                return

            self.progress_updated.emit(60)

            # Step 2: 生成热力云图
            result = self._generate_heatmap(csv_path)
            if result:
                image_path, title = result
                self.progress_updated.emit(100)
                self.status_updated.emit(f"热力云图已保存: {image_path}")
                self.image_ready.emit(image_path, title)
                self.finished.emit(True, f"处理完成! 合并 {valid_count} 个文件，热力云图已生成")
            else:
                self.finished.emit(True, f"数据合并完成 ({valid_count} 个文件)，但热力云图生成失败")

        except Exception as e:
            self.finished.emit(False, f"处理错误: {str(e)}")

    def stop(self):
        self.is_running = False