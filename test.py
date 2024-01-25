import os
import pickle

from HandleFile.AiType import TestAI


def serialize(instance, filename):
    with open(filename, 'wb') as file:
        pickle.dump(instance, file)

def deserialize(filename):
    with open(filename, 'rb') as file:
        instance = pickle.load(file)
    os.remove(filename)  # 反序列化后删除文件
    return instance

# 测试序列化和反序列化
if __name__ == "__main__":
    # 创建TestAI的一个实例
    test_ai = TestAI(1, 2, 3, 4)

    # 将实例序列化到文件
    serialize(test_ai, 'test_ai.pkl')

    # 更新实例
    test_ai.add()

    # 从文件反序列化实例
    deserialized_test_ai = deserialize('test_ai.pkl')

    # 测试以确保反序列化的实例具有原始值
    assert deserialized_test_ai.a == 1
    assert deserialized_test_ai.b == 2
    assert deserialized_test_ai.c == 3
    assert deserialized_test_ai.d == 4

    print("序列化和反序列化测试通过。")