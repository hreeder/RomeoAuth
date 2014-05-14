from romeo_auth import app, cloudflare
from romeo_auth.authutils import group_required
from flask import render_template, request, redirect
from flask.ext.login import login_required

valid_record_types = ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'SRV', 'LOC']

@app.route('/dns')
@login_required
@group_required('admin')
def dns():
    records = []
    for record in cloudflare.rec_load_all(app.config['auth']['domain']):
        records.append(record)
    return render_template('dns.html', dnsrecords=records)


@app.route('/dns/new', methods=['POST', ])
@login_required
@group_required('admin')
def new_dns():
    type = request.form['type']
    if type not in valid_record_types:
        flash('That record type was invalid', 'danger')
        return redirect('/dns')

    name = request.form['name']
    ttl = request.form['ttl']
    value = request.form['value']
    if 'cloudflare' in request.form:
        cf = True
    else:
        cf = False

    result = cloudflare.rec_new(app.config['auth']['domain'],
                                type,
                                name,
                                value,
                                ttl)

    if result['result'] != "success":
        flash('Something bad happened. You may want to check if that record was created', 'danger')

    return redirect("/dns")


@app.route('/dns/edit', methods=['POST', ])
@login_required
@group_required('admin')
def edit_dns():
    type = request.form['type']
    if type not in ['A', 'CNAME', 'MX', 'TXT', 'SPF', 'AAAA', 'NS', 'SRV', 'LOC']:
        flash('That record type was invalid', 'danger')
        return redirect('/dns')

    name = request.form['name']
    ttl = request.form['ttl']
    value = request.form['value']
    if 'cloudflare' in request.form:
        cf = True
    else:
        cf = False


@app.route('/dns/delete/<id>')
@login_required
@group_required('admin')
def delete_dns(id):
    result = cloudflare.rec_delete(app.config['auth']['domain'],
                                   id)

    if result['result'] != "success":
        flash('Something bad happened. You may want to check if that record was created', 'danger')

    return redirect("/dns")
