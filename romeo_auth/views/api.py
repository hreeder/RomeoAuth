from romeo_auth import app, ldaptools
from romeo_auth.authutils import api_key_required

import json

@app.route("/apiv1/group/<string:group>")
@api_key_required
def groupdump(group):
	allusers = ldaptools.getusers("authGroup=%s" % group)
	results = map(lambda x:x.characterName[0], allusers)
	return json.dumps(results)