from romeo_auth import app, ldaptools
from flask import flash, render_template, redirect
from flask.ext.login import login_required, current_user
from ldap import MOD_ADD, MOD_DELETE, MOD_REPLACE

@app.route("/groups")
@login_required
def groups():
	yourgroups = current_user.get_authgroups() + current_user.get_pending_authgroups()
	notyours = lambda x: x not in yourgroups
	return render_template("groups.html", closed_groups=filter(notyours, app.config["groups"]["closedgroups"]), open_groups=filter(notyours, app.config["groups"]["opengroups"]))

@app.route("/groups/admin")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupadmin():
	if "admin" in current_user.authGroup:
		groups = groups=app.config["groups"]["closedgroups"]+app.config["groups"]["opengroups"]
	else:
		groups = map(lambda x:x[6:], filter(lambda x:x.startswith("admin-"), current_user.authGroup))	p
endingusers = ldaptools.getusers("authGroup=*-pending")
	applications = []
	for user in pendingusers:
		for group in user.get_pending_authgroups():
			if group in groups:
				applications.append((user.get_id(), group))
	return render_template("groupsadmin.html", applications=applications, groups=groups)

@app.route("/groups/list/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def grouplist(group):
	users = ldaptools.getusers("authGroup="+group)
	return render_template("groupmembers.html", group=group, members=users)


@app.route("/groups/admin/approve/<id>/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupapprove(id, group):
	if ("admin" not in current_user.get_authgroups()) and ("admin-%s" % group not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/groups/admin")
	try:
		id = str(id)
		group = str(group)
		ldaptools.modgroup(id, MOD_DELETE, group+"-pending")
		ldaptools.modgroup(id, MOD_ADD, group)
		flash("Membership of %s approved for %s" % (group, id), "success")
		return redirect("/groups/admin")
	except:
		flash("Membership application not found", "danger")
		return redirect("/groups/admin")

@app.route("/groups/admin/deny/<id>/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupdeny(id, group):
	if ("admin" not in current_user.get_authgroups()) and ("admin-%s" % group not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/groups/admin")
	try:
		id = str(id)
		group = str(group)
		ldaptools.modgroup(id, MOD_DELETE, group+"-pending")
		flash("Membership of %s denied for %s" % (group, id), "success")
		return redirect("/groups/admin")
	except:
		flash("Membership application not found", "danger")
		return redirect("/groups/admin")

@app.route("/groups/admin/remove/<id>/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupremove(id, group):
	if ("admin" not in current_user.get_authgroups()) and ("admin-%s" % group not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/groups/admin")
	id = str(id)
	group = str(group)
	ldaptools.modgroup(id, MOD_DELETE, group)
	flash("Membership of %s removed for %s" % (group, id), "success")
	return redirect("/groups/list/"+group)


@app.route("/groups/admin/admin/<id>/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupmkadmin(id, group):
	if ("admin" not in current_user.get_authgroups()) and ("admin-%s" % group not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/groups/admin")
	id = str(id)
	group = str(group)
	try:
		ldaptools.modgroup(id, MOD_ADD, "admin-%s" % group)
		flash("Membership of admin-%s added for %s" % (group, id), "success")
	except:
		flash("That user is already in that group.", "danger")
	return redirect("/groups/list/"+group)

@app.route("/groups/admin/ping/<id>/<group>")
@login_required
@groups_required(lambda x:x.startswith("admin"))
def groupmkping(id, group):
	if ("admin" not in current_user.get_authgroups()) and ("admin-%s" % group not in current_user.get_authgroups()):
		flash("You do not have the right to do that.", "danger")
		return redirect("/groups/admin")
	id = str(id)
	group = str(group)
	try:
		ldaptools.modgroup(id, MOD_ADD, "ping-%s" % group)
		flash("Membership of ping-%s added for %s" % (group, id), "success")
	except:
		flash("That user is already in that group.", "danger")
	return redirect("/groups/list/"+group)

@app.route("/groups/apply/<group>")
@login_required
def group_apply(group):
	originalgroup = group
	group = str(group)
	assert(group in app.config["groups"]["closedgroups"]+app.config["groups"]["opengroups"])
	join = True
	if group in app.config["groups"]["closedgroups"]:
		group = group+"-pending"
		join = False
	if current_user.accountStatus[0]=="Ineligible":
		if group not in app.config["groups"]["publicgroups"]:
			flash("You cannot join that group.", "danger")
			return redirect("/groups")
	ldaptools.modgroup(current_user.get_id() , MOD_ADD, group)
	if join:
		flash("Joined %s group" % group, "success")
	else:
		flash("Applied for %s group" % originalgroup, "success")
	return redirect("/groups")

@app.route("/groups/remove/<group>")
@login_required
def group_remove(group):
	group = str(group)
	ldaptools.modgroup(current_user.get_id() , MOD_DELETE, group)
	flash("Removed %s group" % group, "success")
	return redirect("/groups")
