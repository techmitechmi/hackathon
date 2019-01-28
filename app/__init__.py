import os
from flask import Flask, request, render_template, flash, redirect, url_for, session, Blueprint
from tempfile import mkdtemp
from flask_mysqldb import MySQL
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from flask_recaptcha import ReCaptcha
import requests
import json

app = Flask(__name__, instance_path=os.path.join(os.path.abspath(os.curdir), 'instance'), instance_relative_config=True, static_url_path="", static_folder="static")
app.config.from_pyfile('config.cfg')
app.config['SESSION_FILE_DIR'] = mkdtemp()
mysql=MySQL(app)
Session(app)

recaptcha = ReCaptcha(app=app)

def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = "6Le8-XUUAAAAAD3eT4zYW_i2pWEsJw_szKQwlyZc"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


def execute_db(query,args=()):
    cur=mysql.connection.cursor()
    cur.execute(query,args)
    mysql.connection.commit()
    cur.close()
def query_db(query,args=(),one=False):
    cur=mysql.connection.cursor()
    result=cur.execute(query,args)
    if result>0:
        values=cur.fetchall()
        return values

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("adminid") is None:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin")==False:
            return redirect(url_for("main.index", next=request.url))
        return f(*args, **kwargs)
    return decorated_function
    
# Importing Blueprints
from app.views.main import main
# Registering Blueprints
app.register_blueprint(main)