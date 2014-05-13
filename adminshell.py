#!/usr/bin/env python 
"""
Auth shell
"""
import sys
from romeo_auth.ldaptools import LDAPTools
import json
from blessings import Terminal

term = Terminal()
# Load config
fh=open("config.json", "r")
config = json.loads(fh.read())
fh.close()
# Set up tools
ldaptools = LDAPTools(config)
# Enter prompt
print("Entering interactive Romeo Auth admin shell")
sys.ps1 = "{t.magenta}auth > {t.normal}".format(t=term)
import code
code.InteractiveConsole(locals=globals()).interact()
