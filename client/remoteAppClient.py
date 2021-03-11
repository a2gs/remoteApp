#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

from sys import argv, exit
from os import getcwd, path

'''
remoteAppClient run appName
remoteAppClient install appName
remoteAppClient checkUpdates appName
remoteAppclient listInstalledApps
remoteAppclient listServerApps
remoteAppClient update appName

/remoteAppClient/remoteAppClient.py
/remoteAppClient/installed/<apps>
/remoteAppClient/appDatas/<apps>
/remoteAppClient/appBackups/apps.zip
'''

server = "localhost"
remoteAppClient_path = getcwd()
remoteAppClient_Install_Path = 'installed'
remoteAppClient_Data_Path = 'data'
remoteAppClient_Bkps_Path = 'backup'
remoteAppClient_Install_FullPath = path.join(remoteAppClient_path, remoteAppClient_Install_Path)
remoteAppClient_Data_FullPath = path.join(remoteAppClient_path, remoteAppClient_Data_Path)
remoteAppClient_Bkps_FullPath = path.join(remoteAppClient_path, remoteAppClient_Bkps_Path)

def runApp(appName : str) -> [bool, str]:
	import importlib

	app = importlib.import_module(f"installed.{appName}")
	app.run()

	return [True, "Ok!"]

def installApp(appName : str) -> [bool, str]:
	from ftplib import FTP
	print('install...')

def checkUpdatesApp(appName : str) -> [bool, str]:
	pass

def listInstalledAppsApp() -> [bool, str]:
	pass

def listServerAppsApp() -> [bool, str]:
	pass

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
	print(f"App server.........: [{server}]")
	print(f"Path...............: [{remoteAppClient_path}]")
	print(f"Installed Apps path: [{remoteAppClient_Install_FullPath}]")
	print(f"Apps data path.....: [{remoteAppClient_Data_FullPath}]")
	print(f"Backups............: [{remoteAppClient_Bkps_FullPath}]")

if __name__ == '__main__':

	if len(argv) == 1:
		printRemoteAppClient_help()
		exit(0)

	ret = 0
	msgRet = ''
	appName = ''

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

	elif argv[1] == 'checkUpdates':
		ret, msgRet = checkUpdatesApp()

	elif argv[1] == 'listInstalledApps':
		ret, msgRet = listInstalledAppsApp()

	elif arg[1] == 'listServerApps':
		try:
			server = argv[2]
		except:
			ret, msgRet = False, "list server apps command error!"
		else:
			ret, msgRet = listServerAppsApp(server)

	elif argv[1] == 'update':
		try:
			appName = argv[2]
			server = argv[3]
		except:
			ret, msgRet = False, "update command error!"
		else:
			ret, msgRet = updateApp(appName, server)

	else:
		print(f'Unknow option: [{argv[1]}]')
		exit(-1)

	if(ret == False):
		print(f'ERROR: [{msgRet}]')
		exit(-1)

	exit(0)