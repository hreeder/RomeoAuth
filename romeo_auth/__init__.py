import json
import os
from flask import Flask
from flask.ext.login import LoginManager
from ts3tools import ts3manager
from announce import pingbot
from ldaptools import LDAPTools
from emailtools import EmailTools

app = Flask(__name__)

# Load configuration
with open("config.json") as fh:
	config=json.loads(fh.read())
assert(config)
app.config.update(config)
app.secret_key = os.urandom(24)

# Set up all classes
login_manager = LoginManager()
login_manager.init_app(app)
pingbot = pingbot(app.config)
ts3manager = ts3manager(app.config)
ldaptools = LDAPTools(app.config)
emailtools = EmailTools(app.config, app.jinja_loader)

@login_manager.user_loader
def load_user(userid):
	return ldaptools.getuser(userid)

login_manager.login_view = "/login"

@app.teardown_appcontext
def shutdown_session(exception=None):
	pass

from romeo_auth.views import admin, api, core, groups, ping, registration, users
