from romeo_auth import app, ldaptools
from romeo_auth.authutils import group_required
from flask import render_template, request, redirect, flash
from flask.ext.login import login_required
from ldap import MOD_ADD, MOD_DELETE, MOD_REPLACE

@app.route("/admin")
@login_required
@group_required("admin")
def admin():
	return render_template("adminhome.html")

@app.route("/admin/lookup", methods=["POST",])
@login_required
@group_required("admin")
def userlookup():
	user = None
	if "userid" in request.form:
		user = ldaptools.getuser(request.form["userid"])
		if not user:
			flash("Unable to find '%s' as a username." % request.form['userid'], "danger")
			return redirect("/admin")
		else:
			user = user.__dict__
	return redirect("/admin/user/%s" % request.form['userid'])

@app.route("/admin/user/<uid>")
@login_required
@group_required('admin')
def viewuser(uid):
	user = ldaptools.getuser(uid)
	if not user:
		flash("'%s' is not a valid username" % uid, "danger")
		return redirect("/admin")
	user = user.__dict__
	return render_template("admin_viewuser.html", user=user)

@app.route("/admin/user/<uid>/<action>")
@app.route("/admin/user/<uid>/<action>/<value>")
@login_required
@group_required("admin")
def admin_user(uid, action, value=None):
	user = ldaptools.getuser(uid)
	validActions = ['activate', 'disable', 'delete', 'addgroup', 'delgroup']
	if not user:
                flash("'%s' is not a valid username" % uid, "danger")
                return redirect("/admin")
	if action not in validActions:
		flash("'%s' is not a valid action to perform to %s" % (action, uid), "danger")
		return redirect("/admin/user/%s" % uid)

	currentStatus = user.accountStatus[0]

	if action == "activate" and currentStatus == "inactive":
		result = ldaptools.modattr(uid, MOD_REPLACE, "accountStatus", "romeo")
		assert(result)
		flash("Successfully re-activated %s" % uid, "success")
		return redirect("/admin/user/%s" % uid)
	elif action == "disable" and currentStatus == "romeo":
                result = ldaptools.modattr(uid, MOD_REPLACE, "accountStatus", "inactive")
                assert(result)
                flash("Successfully disabled %s" % uid, "success")
                return redirect("/admin/user/%s" % uid)
	elif action == "delete":
		if ldaptools.deleteuser(uid):
			flash("Deleted %s" % uid, "success")
			return redirect("/admin")
		else:
			flash("SOMETHING BAD HAPPENED OH GOD PANIC", "danger")
			return redirect("/admin")
	elif action == "addgroup" and value and value not in user.get_authgroups():
		ldaptools.modgroup(uid, MOD_ADD, str(value))
		flash("%s added to %s" % (uid, value), "success")
		return redirect("/admin/user/%s" % uid)
	elif action == "delgroup" and value and value in user.get_authgroups():
		ldaptools.modgroup(uid, MOD_DELETE, str(value))
		flash("%s removed from %s" % (uid, value), "success")
		return redirect("/admin/user/%s" % uid)
	flash("Unable to perform that action, maybe it's an invalid action due to the user's current state", "danger")
	return redirect("/admin/user/%s" % uid)

@app.route("/admin/listusers")
@app.route("/admin/listusers/<status>")
@login_required
@group_required("admin")
def listusers(status=None):
	if status and status == "active":
		users = ldaptools.getusers("accountStatus=romeo")
	elif status and status == "inactive":
		users = ldaptools.getusers("accountStatus=inactive")
	else:
		status = "all"
		users = ldaptools.getusers("uid=*")
	return render_template("admin_listusers.html", users=users, group=status)

@app.route("/dumper")
@login_required
@group_required("admin")
def dumpheaders():
	return "%s" % (str(request.headers),)