#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

import configparser
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def getCfg(section: str, key: str) -> [bool, None]:
	global cfg

	try:
		value = cfg[section][key]
	except:
		return [False, None]

	return [True, value]

cfg = configparser.ConfigParser()
cfg.read('ras.cfg')

authorizer = DummyAuthorizer()

for sect in cfg.sections():
	ret, username = getCfg(sect, 'user')
	if ret == False: continue

	ret, passwd = getCfg(sect, 'passwd')
	if ret == False: continue

	ret, path = getCfg(sect, 'path')
	if ret == False: continue

	ret, permission = getCfg(sect, 'permissions')
	if ret == False: continue

	print(f'User: [{username}] | Path: [{path}] | Permission: [{permission}]')

	authorizer.add_user(username, passwd, path, perm = permission)

del cfg

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 21), handler)
server.serve_forever()