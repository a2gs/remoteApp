#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

from sys import argv, exit
from os import getcwd, path, mkdir, walk
from ftplib import FTP, error_reply, error_temp, error_perm, error_proto, all_errors
from remoteAppClientCfg import racCfg

'''
remoteAppClient run appName
remoteAppClient install appName
remoteAppClient uninstall appName
remoteAppClient checkUpdates appName
remoteAppclient listInstalledApps
remoteAppclient listServerApps
remoteAppClient update appName

/remoteAppClient/remoteAppClient.py
/remoteAppClient/installed/<apps>
/remoteAppClient/appDatas/<apps>
/remoteAppClient/appBackups/apps.zip
'''

def runApp(appName : str) -> [bool, str]:
	import importlib

	app = importlib.import_module(f"installed.{appName}")
	app.run()
	app.version()

	return [True, "Ok"]

def installApp(appName : str) -> [bool, str]:
	print('install...')
	return [True, 'Ok']

def uninstallApp(appName : str) -> [bool, str]:
	print('uninstall...')
	return [True, 'Ok']

def listInstalledAppsApp() -> [bool, str]:
	import importlib

	global remoteAppClient_Install_FullPath

	instapp = [x for x in walk(remoteAppClient_Install_FullPath)]

	if len(instapp) == 1:
		print('No one application installed')

	else:
		print(f"{'Application':30} | Version")
		for i in instapp[0][1:]:

			if len(i) == 0: continue

			appVersion = importlib.import_module(f"installed.{i[0]}")
			print(f"{i[0]:30} | {appVersion.version()}")

	return [True, 'Ok']

class appList():
	applist = []

	def __init__(self):
		pass

	def add(self, appdesc : str):
		app = appdesc.split('\t')
		self.applist.append(app)

	def get(self) -> []:
		return self.applist

def listServerAppsApp() -> [bool, str]:
	global remoteAppClient_server, remoteAppClient_server_user, remoteAppClient_server_passwd

	try:
		ftpapp = FTP(host    = remoteAppClient_server,
		             user    = remoteAppClient_server_user,
		             passwd  = remoteAppClient_server_passwd,
		             timeout = 20)

	except error_reply as e: return [False, f'{e}']
	except error_temp  as e: return [False, f'{e}']
	except error_perm  as e: return [False, f'{e}']
	except error_proto as e: return [False, f'{e}']
	except all_errors  as e: return [False, f'{e}']
	except Exception   as e: return [False, f'{e}']

	srvapps = appList()

	try:
		ftpapp.retrlines('RETR apps.txt', srvapps.add)

	except error_reply as e: return [False, f'{e}']
	except error_temp  as e: return [False, f'{e}']
	except error_perm  as e: return [False, f'{e}']
	except error_proto as e: return [False, f'{e}']
	except all_errors  as e: return [False, f'{e}']
	except Exception   as e: return [False, f'{e}']

	ftpapp.quit()

	print(f"{'Application':30} | {'Version':10} | Package")
	[print(f'{i[0]:30} | {i[1]:10} | {i[2]}') for i in srvapps.get()]

	return [True, 'Ok']

def updateApp(appName : str) -> [bool, str]:
	pass

def printRemoteAppClient_help():
	print("remoteAppClient run appName")
	print("remoteAppClient install appName")
	print("remoteAppClient checkUpdates appName")
	print("remoteAppclient listInstalledApps")
	print("remoteAppclient listServerApps")
	print("remoteAppClient update appName")
	print("")
	print("Default configuration:")
	print(f"Server.............: [{remoteAppClient_server_user}@{remoteAppClient_server}]")
	print(f"Password...........: [{remoteAppClient_server_passwd}]")
	print(f"Path...............: [{remoteAppClient_path}]")
	print(f"Installed Apps path: [{remoteAppClient_Install_FullPath}]")
	print(f"Apps data path.....: [{remoteAppClient_Data_FullPath}]")
	print(f"Backups............: [{remoteAppClient_Bkps_FullPath}]")

def createPaths() -> [bool, str]:
	global remoteAppClient_Install_FullPath, remoteAppClient_Data_FullPath, remoteAppClient_Bkps_FullPath

	if path.isdir(remoteAppClient_Install_FullPath) == False:
		try:
			mkdir(remoteAppClient_Install_FullPath)
		except:
			return [False, remoteAppClient_Install_FullPath]

	if path.isdir(remoteAppClient_Data_FullPath) == False:
		try:
			mkdir(remoteAppClient_Data_FullPath)
		except:
			return [False, remoteAppClient_Data_FullPath]

	if path.isdir(remoteAppClient_Bkps_FullPath) == False:
		try:
			mkdir(remoteAppClient_Bkps_FullPath)
		except:
			return [False, remoteAppClient_Bkps_FullPath]

	return [True, "Ok"]

# ---------------------------------------------------------------------

cfgFile = 'rac.cfg'
cfg = racCfg(cfgFile)

def checkCfg(ret : bool, section : str, key : str):
	global cfgFile

	ret, value = cfg.get(section, key)

	if ret == False:
		print('There is no [{key}] configuration in [{section}] section into file [{cfgFile}].')
		exit(-1)

	return value

remoteAppClient_server        = checkCfg(cfg, 'SERVER', 'address')
remoteAppClient_server_user   = checkCfg(cfg, 'SERVER', 'user')
remoteAppClient_server_passwd = checkCfg(cfg, 'SERVER', 'passwd')
remoteAppClient_Install_Path  = checkCfg(cfg, 'DIRECTORIES', 'install')
remoteAppClient_Data_Path     = checkCfg(cfg, 'DIRECTORIES', 'data')
remoteAppClient_Bkps_Path     = checkCfg(cfg, 'DIRECTORIES', 'backups')
remoteAppClient_path             = getcwd()
remoteAppClient_Install_FullPath = path.join(remoteAppClient_path, remoteAppClient_Install_Path)
remoteAppClient_Data_FullPath    = path.join(remoteAppClient_path, remoteAppClient_Data_Path)
remoteAppClient_Bkps_FullPath    = path.join(remoteAppClient_path, remoteAppClient_Bkps_Path)

del cfg
del cfgFile

if __name__ == '__main__':

	if len(argv) == 1:
		printRemoteAppClient_help()
		exit(0)

	ret = 0
	msgRet = ''
	appName = ''

	ret, msgRet = createPaths()
	if ret == False:
		print(f'ERROR: creating working paths [{msgRet}].')
		exit(-1)

	if argv[1] == 'run':
		try:
			appName = argv[2]
		except:
			ret, msgRet = False, "run command error!"
		else:
			[ret, msgRet] = runApp(appName)

	elif argv[1] == 'install':
		try:
			appName = argv[2]
		except:
			ret, msgRet = False, "install command error!"
		else:
			ret, msgRet = installApp(appName)

	elif argv[1] == 'uninstallApp':
		try:
			appName = argv[2]
		except:
			ret, msgRet = False, "uninstallApp command error!"
		else:
			ret, msgRet = uninstallAppApp(appName)

	elif argv[1] == 'listInstalledApps':
		ret, msgRet = listInstalledAppsApp()

	elif argv[1] == 'listServerApps':
		ret, msgRet = listServerAppsApp()

	elif argv[1] == 'update':
		try:
			appName = argv[2]
		except:
			ret, msgRet = False, "update command error!"
		else:
			ret, msgRet = updateApp(appName)

	else:
		print(f'Unknow option: [{argv[1]}]')
		exit(-1)

	if ret == False:
		print(f'ERROR: [{msgRet}]')
		exit(-1)

	exit(0)