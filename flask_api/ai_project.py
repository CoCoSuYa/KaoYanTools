import os

from flask import Blueprint, render_template, request, session
from flask_wtf import FlaskForm
from wtforms import StringField

from HandleFile.AiType import CommonAI
from HandleFile.ai_Project_tools import load_keys, update_key_time, serialize, deserialize

ai_project_blueprint = Blueprint('ai_project', __name__)


class ChatForm(FlaskForm):
    message = StringField('请输入您的问题：')


# 处理初次访问页面的GET请求
@ai_project_blueprint.route('/ai', methods=['GET'])
def ai_page():
    form = ChatForm()
    api = load_keys()
    talk = CommonAI(api_key=api)
    session.pop('session_id', None)  # 删除旧的会话ID
    session_id = session.get('session_id')
    if not session_id:
        session_id = os.urandom(24).hex()  # 生成一个新的会话ID
        session['session_id'] = session_id
    print("serialize_session_id:", session_id)
    print("talk.api_key:", talk.api_key)
    serialize(talk, session_id)
    return render_template('aiTalk.html', form=form)


# 处理发送消息的POST请求
@ai_project_blueprint.route('/ai', methods=['POST'])
def ai_message():
    session_id = session.get('session_id')
    print("deserialize_session_id:", session_id)
    if not session_id:
        return "Session not found.", 404  # 没有找到会话ID，返回错误
    talk = deserialize(session_id)
    form = ChatForm()
    if form.validate_on_submit():
        message = form.message.data
        print("message：", message)
        print("talk.api_key:", talk.api_key)
        talk.send_message({"role": "user", "content": message})
        update_key_time(talk.api_key)
        serialize(talk, session_id)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 这是一个Ajax请求，返回JSON响应
            return talk.content
        else:
            # 这不是一个Ajax请求，返回正常的HTML响应
            return render_template('aiTalk.html', form=form, response=talk.content)
    return render_template('aiTalk.html', form=form)
