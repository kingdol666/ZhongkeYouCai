import os
import csv
import pandas as pd
import numpy as np
from datetime import datetime

def parse_time_from_filename(filename):
    """
    从文件名解析时间信息
    文件名格式: 21_51_29_1 (21时51分29秒)
    """
    # 去掉.CSV扩展名
    basename = os.path.basename(filename)
    name_without_ext = os.path.splitext(basename)[0]
    
    # 分割文件名
    parts = name_without_ext.split('_')
    
    if len(parts) >= 3:
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2])
        # 返回格式化的时间字符串
        return f"{hour:02d}:{minute:02d}:{second:02d}"
    return "Unknown"

def calculate_position_columns(num_points=183):
    """
    计算位置列名，从2.5到14.39平均分配184个点
    
    Args:
        num_points: 位置点的数量，默认为184
        
    Returns:
        位置列名列表
    """
    start_pos = 2.50
    end_pos = 14.39
    step = (end_pos - start_pos) / (num_points - 1)
    positions = [round(start_pos + i * step, 2) for i in range(num_points)]
    return positions

def process_csv_files():
    """
    处理所有CSV文件的主函数
    """
    # 数据文件夹路径
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Data')
    
    # 输出文件夹路径
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ProcessedData')
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历所有子文件夹
    for subdir in os.listdir(data_dir):
        subdir_path = os.path.join(data_dir, subdir)
        
        # 确保是目录
        if os.path.isdir(subdir_path):
            print(f"处理子文件夹: {subdir}")
            
            # 获取所有CSV文件
            csv_files = [f for f in os.listdir(subdir_path) if f.endswith('.CSV')]
            csv_files.sort()  # 按文件名排序
            
            if not csv_files:
                print(f"  子文件夹 {subdir} 中没有CSV文件")
                continue
                
            # 读取第一个CSV文件确定数据点数量
            first_csv_path = os.path.join(subdir_path, csv_files[0])
            with open(first_csv_path, 'r') as f:
                lines = f.readlines()
                # 设置固定数据点数量为184个点（从第7行到第190行）
                num_data_points = 183
            
            # 计算位置列名
            position_columns = calculate_position_columns(num_data_points)
            
            # 创建DataFrame来存储合并后的数据
            # 行为时间，列为位置
            merged_data = pd.DataFrame(columns=position_columns)
            
            # 处理每个CSV文件
            for csv_file in csv_files:
                csv_path = os.path.join(subdir_path, csv_file)
                
                # 从文件名解析时间
                time_str = parse_time_from_filename(csv_file)
                
                # 读取CSV文件，跳过前7行，只读取183行数据（从第7行到第190行）
                df = pd.read_csv(csv_path, skiprows=7, header=None, names=['pos', 'bw'], nrows=183)
                
                # 确保数据点数量匹配
                if len(df) != num_data_points:
                    print(f"  跳过: 文件 {csv_file} 的数据点数量 ({len(df)}) 与预期 ({num_data_points}) 不匹配")
                    continue
                
                # 将厚度数据添加到合并的DataFrame中，作为一行
                # 使用时间作为行索引
                merged_data.loc[time_str] = df['bw'].values
            
            # 保存合并后的数据到新的CSV文件
            output_file = os.path.join(output_dir, f"merged_{subdir}.csv")
            merged_data.to_csv(output_file)
            print(f"  已保存合并数据到: {output_file}")

if __name__ == "__main__":
    process_csv_files()
    print("所有CSV文件处理完成!")