from flask import Blueprint, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField

from HandleFile.AiType import CommonAI
from HandleFile.ai_Project_tools import load_keys, update_key_time

ai_project_blueprint = Blueprint('ai_project', __name__)


class ChatForm(FlaskForm):
    message = StringField('请输入您的问题：')


@ai_project_blueprint.route('/ai', methods=['GET', 'POST'])
def ai_page():
    api = load_keys()
    talk = CommonAI(api_key=api)
    form = ChatForm()
    if form.validate_on_submit():
        message = form.message.data
        print("message：", message)
        talk.send_message({"role": "user", "content": message})
        update_key_time(api)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 这是一个Ajax请求，返回JSON响应
            print(talk.content)
            return talk.content
        else:
            # 这不是一个Ajax请求，返回正常的HTML响应
            return render_template('aiTalk.html', form=form, response=talk.content)
    return render_template('aiTalk.html', form=form)
