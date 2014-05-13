from romeo_auth import app, pingbot
from romeo_auth.authutils import group_required, groups_required
from flask import flash, request, session, redirect, render_template
from flask.ext.login import login_required, current_user

@app.route("/ping")
@login_required
@groups_required(lambda x:x.startswith("ping"))
def ping():
	return render_template("ping.html")

@app.route("/ping/send", methods=["POST"])
@login_required
@group_required("ping")
def ping_send():
	servers = map(lambda x:x + config["auth"]["domain"], ["allies.", "", "public."])
	servers = filter(lambda x:x in request.form, servers)
	pingbot.broadcast(current_user.get_name(),"All Online", request.form["message"], servers)
	flash("Broadcast sent to All Online", "success")
	return redirect("/ping")

@app.route("/ping/group", methods=["POST"])
@login_required
@groups_required(lambda x:x.startswith("ping"))
def ping_send_group():
	if ("ping" not in current_user.get_authgroups()) and ("ping-%s" % request.form["group"] not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/ping")
	count = pingbot.groupbroadcast(current_user.get_name(), "(|(authGroup={0}))".format(request.form["group"]), request.form["message"], request.form["group"])
	flash("Broadcast sent to %d members in %s" % (count, request.form["group"]), "success")
	return redirect("/ping")

@app.route("/ping/advgroup", methods=["POST"])
@login_required
@group_required("ping")
def ping_send_advgroup():
	ldap_filter = "("+request.form["filter"]+")"
	message = request.form["message"]
	count = pingbot.groupbroadcast(current_user.get_name(), ldap_filter, message, ldap_filter)
	flash("Broadcast sent to %d members in %s" % (count, ldap_filter), "success")
	return redirect("/ping")

@app.route("/ping/complete")
def pingcomplete():
	allusers = ldaptools.getusers("objectClass=xxPilot")
	entities = []
	for user in allusers:
		if user.corporation[0] not in entities:
			entities.append(user.corporation[0])
		if hasattr(user, "alliance"):
			if user.alliance[0] not in entities:
				entities.append(user.alliance[0])
	term = request.args.get('term')
	results = filter(lambda x:x.lower().startswith(term.lower()), entities+app.config["groups"]["closedgroups"]+app.config["groups"]["opengroups"])
	return json.dumps(results)