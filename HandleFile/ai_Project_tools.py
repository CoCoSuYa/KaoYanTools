import json
import datetime
import os
import pickle
import time

from zhipuai import ZhipuAI

keys_url = os.getcwd() + "/api_key.json"
pickle_url = os.getcwd() + "/pickle_files/"


def load_keys():
    with open(keys_url) as f:
        data = json.load(f)
    api_key = ""
    # 获取当前时间，精确到分钟
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    # 初始化标志位，表示是否已经选择了API密钥
    flag = False
    # 找到第一个status为"empty"或"using"但超过10分钟没有使用的key，并将status修改为"using"
    for test, info in data.items():
        if info['status'] == 'empty' or (info['status'] == 'using' and (
                datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M') - datetime.datetime.strptime(info['last_time'],
                                                                                                    '%Y-%m-%d %H:%M')).total_seconds() > 600):
            if not flag:
                api_key = info['key']
                info['status'] = 'using'
                info['last_time'] = now_time
                flag = True
            else:
                info['status'] = 'empty'

    # 如果没有找到可用的API密钥，返回默认的api
    if not flag:
        return "ddf5a2904f615d2039e77590bdc9006b.JkoaJ4q33a6rRy2h"

    # 将修改后的数据写回json文件
    with open(keys_url, 'w') as f:
        json.dump(data, f, indent=4)

    return api_key


def update_key_time(api_key):
    # 读取json文件
    with open(keys_url) as f:
        data = json.load(f)
    # 获取当前时间，精确到分钟
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    # 遍历json数据，找到匹配的key，然后更新last_time
    for test, info in data.items():
        if info['key'] == api_key:
            info['last_time'] = now_time
            break
    # 将修改后的数据写回json文件
    with open(keys_url, 'w') as f:
        json.dump(data, f, indent=4)


def serialize(instance, session_id):
    url = os.path.join(pickle_url, 'talk_' + session_id + '.pkl')
    with open(url, 'wb') as file:
        pickle.dump(instance, file)
    cleanup_serialized_files(pickle_url, 2 * 60 * 60)  # 2小时的秒数


def deserialize(session_id):
    url = os.path.join(pickle_url, 'talk_' + session_id + '.pkl')
    with open(url, 'rb') as file:
        instance = pickle.load(file)
    cleanup_serialized_files(pickle_url, 2 * 60 * 60)  # 2小时的秒数
    # 在反序列化之后，确保重新创建client
    instance.client = ZhipuAI(api_key=instance.api_key)
    return instance


def cleanup_serialized_files(directory, max_age_seconds):
    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = now - os.path.getmtime(file_path)  # 检查文件的最后修改时间
            if file_age > max_age_seconds:
                os.remove(file_path)
                print("Deleted old serialized file: %s" % filename)
