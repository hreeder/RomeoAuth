from romeo_auth import app, login_manager, ldaptools
from flask import flash, render_template, redirect, request
from flask.ext.login import login_user, logout_user, login_required, current_user

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method=="GET":
		return render_template("login.html", next_page=request.args.get("next"))
	username = request.form["username"]
	password = request.form["password"]
	next_page = request.form["next_page"]
	if ldaptools.check_credentials(username, password):
		user = ldaptools.getuser(username)
		login_user(user)
		flash("Logged in as %s" % username, "success")
		if next_page and next_page!="None":
			return redirect(next_page)
		else:
			return redirect("/")
	else:
		flash("Invalid Credentials. ", "danger")
		return redirect("/login")

@app.route("/forgot_password", methods=["POST", "GET"])
def forgot_password():
	if request.method=="GET":
		return render_template("forgot_password.html")
	username = request.form["username"]
	email = request.form["email"]
	try:
		user = ldaptools.getuser(username)
		assert(user)
		assert(email == user.email[0])
		token = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(24))
		url = request.host_url+"recovery/"+token
		recoverymap[token] = username
		emailtools.render_email(email, "Password Recovery", "forgot_password.txt", url=url, config=app.config)
		flash("Email sent to "+email, "success")
	except Exception as e:
		flash("Username/Email mismatch", "danger")
	return redirect("/login")

@app.route("/recovery/<token>")
def recovery(token):
	if token not in recoverymap:
		flash("Recovery Token Expired", "danger")
		return redirect("/login")
	else:
		user = ldaptools.getuser(recoverymap[token])
		login_user(user)
		del recoverymap[token]
		flash("Logged in as %s using recovery token." % user.get_id(), "success")
		return render_template("account_reset.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")

@app.route("/account")
@login_required
def account():
	return render_template("account.html")

@app.route("/account/update", methods=['POST'])
@login_required
def update_account():
	email = request.form["email"]
	characterName = request.form["characterName"]
	oldpassword = request.form["oldpassword"]
	if not ldaptools.check_credentials(current_user.get_id(), oldpassword):
		flash("You must confirm your old password to update your account.", "danger")
		return redirect("/account")
	try:
		if all(x in request.form for x in ["password", "password_confirm", "oldpassword"]):
			if request.form["password"] != request.form["password_confirm"]:
				flash("Password confirmation mismatch.", "danger")
				return redirect("/account")
			result = ldaptools.modattr(current_user.get_id(), MOD_REPLACE, "userPassword", ldaptools.makeSecret(request.form["password"]))
			assert(result)
		result = ldaptools.modattr(current_user.get_id(), MOD_REPLACE, "email", email)
		assert(result)
		result = ldaptools.modattr(current_user.get_id(), MOD_REPLACE, "characterName", characterName)
		assert(result)
		flash("Account updated", "success")
	except Exception:
		flash("Update failed", "danger")
	app.logger.info('User account {0} infos changed'.format(current_user.get_id()))
	return redirect("/account")