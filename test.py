import requests as requests

# 在这里配置您在本站的API_KEY
api_key = "your API_KEY"

headers = {
    "Authorization": 'Bearer ' + 'sk-c2W2DFWC7B5D19247e19T3BLBkFJcFcb14b504E842299535',
}

question = input("输入您的问题\n")

params = {
    "messages": [

        {
            "role": 'user',
            "content": question
        }
    ],
    # 如果需要切换模型，在这里修改
    "model": 'gpt-3.5-turbo-16k-0613'
}
response = requests.post(
    "https://cfwus02.opapi.win/v1/chat/completions",
    headers=headers,
    json=params,
    stream=False
)
res = response.json()
print(res)
res_content = res['choices'][0]['message']['content']
print(res_content)
