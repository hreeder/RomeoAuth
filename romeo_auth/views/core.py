from romeo_auth import app, ldaptools, ts3manager
from flask import render_template, request, flash, redirect
from flask.ext.login import current_user, login_required
from ldap import MOD_ADD, MOD_DELETE, MOD_REPLACE

@app.route('/')
def index():
	if current_user.is_anonymous():
		return render_template("index.html")
	else:
		return render_template("index_user.html")

@app.route("/services")
@login_required
def services():
	return render_template("services.html")

@app.route("/services/ts3id", methods=['POST'])
@login_required
def add_tss3id():
	ts3id = str(request.form["ts3id"])
	ts3group = {
			"romeo": app.config["ts3"]["servergroups"]["full"]
			}
	ldaptools.modts3id(current_user.get_id() , MOD_ADD, ts3id)
	result = ts3manager.modpermissions(ts3id, groupid=ts3group[current_user.accountStatus[0]])
	if result:
		flash("TS3 ID added and auth requested.", "success")
	else:
		flash("Something blew up.", "error")
	return redirect("/services")


@app.route("/services/ts3id/reload", methods=['GET'])
@login_required
def refresh_ts3id():
	ts3ids = current_user.ts3uid
	ts3group = {
			"romeo": app.config["ts3"]["servergroups"]["full"]
			}
	results = []
	for ts3id in ts3ids:
		results.append(ts3manager.modpermissions(ts3id, groupid=ts3group[current_user.accountStatus[0]]))
	flash("Results:"+str(results), "info")
	return redirect("/services")



@app.route("/services/ts3id/delete/<path:id>")
@login_required
def delete_ts3id(id):
	id = str(id)
	ts3manager.modpermissions(id, remove=True, groupid=app.config["ts3"]["servergroups"]["full"])
	ts3manager.modpermissions(id, remove=True, groupid=app.config["ts3"]["servergroups"]["ally"])
	ldaptools.modts3id(current_user.get_id() , MOD_DELETE, id)
	return redirect("/services")
