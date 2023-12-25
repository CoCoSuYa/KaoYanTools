import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_path_url = os.getcwd() + "/backup/file_path.json"
with open(file_path_url) as file_path_json:
    file_path = json.load(file_path_json)
data_dir = file_path["datas_dir"]


def cmt_data_analysis(path):
    # 假设 'data.csv' 是你的数据文件名
    # 确保在相同目录下存在这样的文件，或提供完整路径
    # 如果 df 已经是您的DataFrame, 那么跳过这个读取文件的步骤
    df = pd.read_csv(path)

    # 假设‘view_duration’列有可能含有字符串类型的"未知"数据
    # 先将 "未知" 替换为 NaN, 然后删除这些行
    df = df.replace('未知', np.nan)  # 若为其他标识未知的字符串，需相应替换
    df = df.dropna(subset=['view_duration'])

    # 确保 'view_duration' 列是数值类型
    df['view_duration'] = pd.to_numeric(df['view_duration'])

    # 过滤掉超过 1200s 的数据
    df = df[df['view_duration'] <= 1200]

    # 对 view_duration 进行四舍五入取整
    df['view_duration'] = df['view_duration'].round().astype(int)

    # 分组统计，对每一秒钟都计算累计离开的用户数
    cumulative_users = df['view_duration'].value_counts().sort_index(ascending=False).cumsum()

    # 绘制图表，横坐标是取整后的 view_duration，纵坐标是每个时间点的累计用户数
    plt.figure(figsize=(10, 5))
    plt.plot(cumulative_users.index, cumulative_users.values, marker='o', linestyle='-', color='blue')

    # 添加图表标题和坐标轴标签
    plt.title('Cumulative User Departure over View Duration (Up to 1200 Seconds)')
    plt.xlabel('View Duration (seconds)')
    plt.ylabel('Cumulative Number of Users Left')

    # 设置 X 轴和 Y 轴的刻度
    plt.xticks(np.arange(0, 1201, 100))  # X 轴: range 从 0 到 1201，step 为 100
    plt.yticks(np.arange(0, cumulative_users.max() + 1, 1000))  # Y 轴: range 从 0 到 最大累计用户数+1，step 为 1000

    # 限制 X 轴的显示范围从 1 到 1200 (根据您的数据调节上限)
    plt.xlim(1, 1200)

    filename_without_ext = os.path.splitext(os.path.basename(path))[0]
    # 构造新文件名（可以自行修改格式）
    new_filename = filename_without_ext + "_data_analysis.png"
    # 得到新文件的完整路径
    new_file_url = os.path.join(data_dir, new_filename)
    # 使用os.path.abspath确保路径是绝对的
    absolute_path = os.path.abspath(new_file_url)
    # 创建保存图像的路径文件夹（如果不存在）
    if not os.path.exists(os.path.dirname(absolute_path)):
        os.makedirs(os.path.dirname(absolute_path))
    # 保存图表到指定路径
    plt.savefig(absolute_path, bbox_inches='tight')
    # 显示图表
    plt.show()
