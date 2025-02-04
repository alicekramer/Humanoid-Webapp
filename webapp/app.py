# -*- coding: utf-8 -*-
# from crypt import methods
from flask import request, Flask, render_template, redirect, send_file
import flask
import qi
from os import environ
from copy import deepcopy
import logging
from typing import Optional
from human_greeter import HumanGreeter
from util import get_statements_ui as get_statements
from raven.contrib.flask import Sentry

human_greeter = None
logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.config.from_pyfile('appconfig.py')
def url_for_self(**args):
    return flask.url_for(flask.request.endpoint, **dict(flask.request.view_args, **args))

app.jinja_env.globals['url_for_self'] = url_for_self

IP = environ.get("NAO_IP", "127.0.0.1")

ALL_BUTTONS = {"home": "HOME", "showcases": "WELCOME", "movement": "MOVE", "chat": "CHAT"}

SUPPORTED_LANGS = ('de', 'en')
NAO_PORT = "9559"


@app.route('/')
def redir():
    return redirect('/home', 307)


@app.route('/home')
def home():
    return render_template('home.html', default_lang=app.config['DEFAULT_LANG'])


@app.route('/<lang>/chat')
def chat(lang):
    # type: (str) -> str|tuple[str, int]
    if lang not in SUPPORTED_LANGS:
        return '', 404
    buttons = deepcopy(ALL_BUTTONS)
    try:
        del buttons['chat']
    except KeyError:
        pass
    statements = get_statements('chat', lang)
    return render_template('listview.html', statements=statements, lang=lang, section="CHAT", buttons=buttons)


@app.route('/<lang>/showcases')
def showcases(lang):
    # type: (str) -> str|tuple[str, int]
    if lang not in SUPPORTED_LANGS:
        return '', 404
    statements = get_statements('showcase', lang)
    return render_template('showcases.html', statements=statements, lang=lang)


@app.route('/<lang>/movement')
def movement(lang):
    # type: (str) -> str|tuple[str, int]
    if lang not in SUPPORTED_LANGS:
        return '', 404
    statements = get_statements('movement', lang)
    return render_template('movement.html', statements=statements, lang=lang)


@app.route('/test', methods=["POST"])
def action():
    rq_data = request.get_json(force=True)
    classes = rq_data["class"].split(" ")
    if "lang--de" in classes:
        language = "de"
        print("Language: de")
    elif "lang--en" in classes:
        language = "en"
        print("Language: en")

    if "speech" in classes:
        action = "speech"
        prompt = rq_data["id"]
    elif "NaoChat" in classes:
        action = "NaoChat"
        prompt = rq_data["id"]
    elif "move" in classes:
        action = "move"
        prompt = rq_data["id"]
        # if prompt=="Stand/Waiting/TakePicture_1":
        #     activate_qi().showNaoImage()
    else:
        pass
    qi = activate_qi()
    if qi:
        if action == "move":
            res = qi.move(prompt)
            if res:
                res[1].seek(0)
                return send_file(res[1], mimetype=res[0])
        elif action in ("NaoChat", "speech"):
            qi.speak(language, prompt, action)
    return "", 200


def activate_qi():
    # type: () -> HumanGreeter|None
    global human_greeter
    if human_greeter is not None:
        return human_greeter
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + IP + ":" + str(NAO_PORT)
        logging.debug("initialising Qi app...")
        qi_app = qi.Application(["HumanGreeter", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(NAO_PORT) + ".\n"
              "Please check your script arguments. Run with -h option for help.")
        return None
    human_greeter = HumanGreeter(qi_app)
    return human_greeter


if __name__ == "__main__":
    raven = Sentry(app, dsn='https://9872015619a46ca56a5b7298d4a3ed15@sentry.technologyinnovation.cloud/12',
                   logging=True, level=logging.ERROR)
    try:
        human_greeter = activate_qi()
    except RuntimeError as e:
        logging.error("Can't connect to NaoQi", exc_info=e)

    app.run(debug=False, host='0.0.0.0')
