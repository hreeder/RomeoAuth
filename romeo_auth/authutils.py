from flask import current_app, redirect, flash, request, abort
from flask.ext.login import current_user
from functools import wraps
from random import randint
from hashlib import md5
from urllib import urlopen


def groups_required(filter_function):
	def real_decorator(func):
		"Decorates a function to require a certain auth group to continue"
		@wraps(func)
		def decorated_view(*args, **kwargs):
			if len(filter(filter_function, current_user.authGroup))==0:
				flash("You must be in one of the correct groups to access that.", "danger")
				return redirect("/")
			else:
				return func(*args, **kwargs)
		return decorated_view
	return real_decorator

def group_required(group):
	def real_decorator(func):
		"Decorates a function to require a certain auth group to continue"
		@wraps(func)
		def decorated_view(*args, **kwargs):
			if group not in current_user.authGroup:
				flash("You must be in the %s group to access that." % group, "danger")
				return redirect("/")
			else:
				return func(*args, **kwargs)
		return decorated_view
	return real_decorator

def api_key_required(func):
	@wraps(func)
	def decorated_view(*args, **kwargs):
		key = request.args.get('key','')
		if key not in current_app.config["apikeys"]:
			abort(401)
		else:
			return func(*args, **kwargs)
	return decorated_view

KeyCAPTCHA_Template = '''<!-- KeyCAPTCHA code (www.keycaptcha.com)-->
<input id="capcode" type="hidden" name="capcode" value="123" />
<script language="JavaScript">
    var s_s_c_user_id = '#kc_user_id#';
    var s_s_c_session_id = '#kc_session_id#';
    var s_s_c_captcha_field_id = 'capcode';
    var s_s_c_submit_button_id = 'postbut';
    var s_s_c_web_server_sign = '#kc_s1#';
    var s_s_c_web_server_sign2 = '#kc_s2#';
</script>
<script language=JavaScript src="https://backs.keycaptcha.com/swfs/cap.js"></script>
<!-- end of KeyCAPTCHA code-->
'''

def show_keycaptcha(remote_ip='127.0.0.1') :
  KeyCAPTCHA_PrivateKey = current_app.config['keycaptcha']['secret']
  KeyCAPTCHA_UserID = current_app.config['keycaptcha']['userid']
  session_id = str(randint(100000000,999999999999))
  s1 = md5( session_id + remote_ip + KeyCAPTCHA_PrivateKey ).hexdigest()
  s2 = md5( session_id + KeyCAPTCHA_PrivateKey ).hexdigest()
  rd = { 'kc_user_id':KeyCAPTCHA_UserID, 'kc_s1':s1, 'kc_s2':s2, 'kc_session_id':session_id }
  st = KeyCAPTCHA_Template
  for k in rd.keys() :
    st = st.replace( '#' + k + '#', rd[k] )
  return st


def validate_keycaptcha( capcode ) :  
  KeyCAPTCHA_PrivateKey = current_app.config['keycaptcha']['secret']
  KeyCAPTCHA_UserID = current_app.config['keycaptcha']['userid']
  cap = capcode.split('|')
  if len( cap ) < 3 : return False
  valid_cap_sign = md5( 'accept' + cap[1] + KeyCAPTCHA_PrivateKey + cap[2] ).hexdigest()
  if valid_cap_sign <> cap[0] : return False
  if cap[2].find( 'http://' ) == 0 : 
    try :
      f = urlopen( cap[2] + cap[1] )
      st = f.read()
      f.close()
    except :
      return False
    if st <> '1' : return False
  else : return False
  return True
