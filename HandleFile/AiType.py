import json

from zhipuai import ZhipuAI


class CommonAI:
    def __init__(self, api_key):
        self.spent_tokens = None
        self.finish_reason = None
        self.content = None
        self.model = None
        self.client = ZhipuAI(api_key=api_key)
        self.histories = []

    def edit_history(self, message):
        # 如果列表长度大于或等于9，保留最后9个元素
        if len(self.histories) >= 9:
            histories = self.histories[-9:]  # 保留最后9个元素
        # 将新消息添加到列表末尾
        self.histories.append(message)

    def send_message(self, message):
        messages = []
        self.edit_history(message)
        for history in self.histories:
            messages.append(history)
        res = self.client.chat.completions.create(
            model="glm-4",  # 填写需要调用的模型名称
            messages=messages,
            max_tokens=4096,
        )
        self.analyze_response(res)
        self.export_message()
        return res

    def analyze_response(self, response):
        data = json.loads(response.model_dump_json())
        self.model = data["model"]
        self.content = data["choices"][0]["message"]["content"]
        self.finish_reason = data["choices"][0]["finish_reason"]
        self.spent_tokens = data["usage"]["total_tokens"]
        self.edit_history({"role": "assistant", "content": self.content})

    def export_message(self):
        print("模型:", self.model)
        print("回答:", self.content)
        if self.finish_reason == "stop":
            print("请求正常完成", end=",")
        elif self.finish_reason == "length":
            print("回答长度超过限制被截断", end=",")
        elif self.finish_reason == "tool_calls":
            print("模型命中函数", end=",")
        print("此次请求消耗tokens：", self.spent_tokens, "个")