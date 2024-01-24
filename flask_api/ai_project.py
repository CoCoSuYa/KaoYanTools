from flask import Blueprint, redirect, url_for, render_template
from flask_wtf import FlaskForm
from wtforms import StringField
from HandleFile.AiType import CommonAI

ai_project_blueprint = Blueprint('ai_project', __name__)
talk = CommonAI(api_key="ddf5a2904f615d2039e77590bdc9006b.JkoaJ4q33a6rRy2h")


class ChatForm(FlaskForm):
    message = StringField('请输入您的问题：')


@ai_project_blueprint.route('/ai', methods=['GET', 'POST'])
def ai_page():
    form = ChatForm()
    if form.validate_on_submit():
        message = form.message.data
        talk.send_message({"role": "user", "content": message})
        return render_template('aiTalk.html', form=form, response=talk.content)
    return render_template('aiTalk.html', form=form)
