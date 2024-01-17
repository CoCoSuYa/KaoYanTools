import json
import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_path_url = os.getcwd() + "/backup/file_path.json"
with open(file_path_url) as file_path_json:
    file_path = json.load(file_path_json)
data_dir = file_path["datas_dir"]


def cmt_data_analysis(path):
    df = pd.read_csv(path)
    df = df.replace('未知', np.nan)
    df = df.dropna(subset=['view_duration'])
    df['view_duration'] = pd.to_numeric(df['view_duration'])
    df = df[df['view_duration'] <= 1200]
    df['view_duration'] = df['view_duration'].round().astype(int)

    cumulative_users = df['view_duration'].value_counts().sort_index(ascending=False).cumsum()

    plt.figure(figsize=(10, 5))
    plt.plot(cumulative_users.index, cumulative_users.values, marker='o', linestyle='-', color='blue')

    # 计算斜率并找到最小斜率的位置
    slopes = np.diff(cumulative_users.values) / np.diff(cumulative_users.index)
    min_slope_idx = np.argmin(slopes)
    min_slope_value = slopes[min_slope_idx]

    # 在图上标记最小斜率的位置
    plt.plot(cumulative_users.index[min_slope_idx], cumulative_users.values[min_slope_idx], 'ro')

    # 在图上标记最小斜率的值
    plt.text(cumulative_users.index[min_slope_idx], cumulative_users.values[min_slope_idx], f'slope: {min_slope_value:.2f}', color='red')

    plt.title('Cumulative User Departure over View Duration (Up to 1200 Seconds)')
    plt.xlabel('View Duration (seconds)')
    plt.ylabel('Cumulative Number of Users Left')

    plt.xticks(np.arange(0, 1201, 100))
    max_users = cumulative_users.max()
    digits = int(math.log10(max_users)) + 1 if max_users != 0 else 1
    y_ticks = 10 ** (digits - 1)
    plt.yticks(np.arange(0, max_users + 1, y_ticks))
    plt.xlim(1, 1200)

    filename_without_ext = os.path.splitext(os.path.basename(path))[0]
    new_filename = filename_without_ext + "_data_analysis.png"
    new_file_url = os.path.join(data_dir, new_filename)
    absolute_path = os.path.abspath(new_file_url)
    if not os.path.exists(os.path.dirname(absolute_path)):
        os.makedirs(os.path.dirname(absolute_path))
    plt.savefig(absolute_path, bbox_inches='tight')
    plt.show()
