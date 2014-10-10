from romeo_auth import app, ldaptools
from romeo_auth.authutils import show_keycaptcha, validate_keycaptcha
from flask import render_template, request, flash, redirect
from flask.ext.login import login_user
from ldap import ALREADY_EXISTS

@app.route('/signup')
def signup():
	captcha = show_keycaptcha(request.remote_addr)
	return render_template("signup.html", captcha=captcha)

@app.route('/create_account', methods=['POST'])
def create_account():
	capcode = request.form.get("capcode")
	if not validate_keycaptcha(capcode):
		flash("Captcha Incorrect, Please Try Again")
		return redirect("/signup")

	attrs = {}
	attrs["uid"] = request.form.get("username")
	attrs["email"] = request.form.get("email")
	attrs["userPassword"] = request.form.get("password")

	attrs["characterName"] = request.form.get("characterName")
	attrs["accountStatus"] = "romeo"

	for key in attrs:
		attrs[key] = str(attrs[key])

	import re
	def special_match(strg, search=re.compile(r'[^-_\.a-zA-Z0-9]+').search):
		return bool(search(strg))

	if special_match(attrs["uid"]):
		flash("Usernames can only contain Numbers, Letters and - _ . characters.", "danger")
		return redirect("/signup")

	try:
		ldaptools.adduser(attrs)
	except ALREADY_EXISTS:
		flash("User already exists", "danger")
		return redirect("/")

	user = ldaptools.getuser(attrs["uid"])
	login_user(user)
	flash("Created and logged in as %s" % attrs["uid"], "success")

	return redirect("/")
