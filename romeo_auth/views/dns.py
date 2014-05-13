from romeo_auth import app, cloudflare
from romeo_auth.authutils import group_required
from flask import render_template
from flask.ext.login import login_required

@app.route('/dns')
@login_required
@group_required('admin')
def dns():
	records = []
	for record in cloudflare.rec_load_all(app.config['auth']['domain']):
		records.append(record)
	return render_template('dns.html', dnsrecords=records)