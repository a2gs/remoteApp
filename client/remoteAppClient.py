#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

from sys import argv, exit
from os import getcwd, path, mkdir, walk, remove
from shutil import rmtree
from ftplib import FTP, error_reply, error_temp, error_perm, error_proto, all_errors
from remoteAppClientCfg import racCfg
import zipfile

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

def connectFTP(server : str, user : str, passwd : str, timeout : int, debugLevel : int) -> [bool, str, object]:
	try:
		ftpapp = FTP(host    = server,
		             user    = user,
		             passwd  = passwd,
		             timeout = timeout)

	except error_reply as e: return [False, f'{e}', None]
	except error_temp  as e: return [False, f'{e}', None]
	except error_perm  as e: return [False, f'{e}', None]
	except error_proto as e: return [False, f'{e}', None]
	except all_errors  as e: return [False, f'{e}', None]
	except Exception   as e: return [False, f'{e}', None]

	ftpapp.set_debuglevel(debugLevel)

	return [True, 'Ok', ftpapp]

def execRetrFTP(conn : FTP, binascii : str, file : str, callback) -> [bool, str]:
	try:
		if binascii == 'BIN':
			conn.retrbinary(f'RETR {file}', callback, blocksize = 8192)
		elif binascii == 'ASCII':
			conn.retrlines(f'RETR {file}', callback)
		else:
			return [False, f"Unknown mode [{binascii}]. Only 'BIN' or 'ASCII' allowed"]

	except error_reply as e: return [False, f'{e}']
	except error_temp  as e: return [False, f'{e}']
	except error_perm  as e: return [False, f'{e}']
	except error_proto as e: return [False, f'{e}']
	except all_errors  as e: return [False, f'{e}']
	except Exception   as e: return [False, f'{e}']

	return [True, 'Ok']

def getAppVersion(app : str) -> [bool, str, object]:
	import importlib

	global remoteAppClient_Install_Path

	try:
		appVersion = importlib.import_module(f"{remoteAppClient_Install_Path}.{app}")
	except:
		return [False, f'Unable to import [{app}] to get version', None]

	ver = ''
	try:
		ver = appVersion.version()
	except:
		return [False, f'Unable to get version of application [{app}]', None]

	return [True, 'Ok', ver]

def runApp(appName : str) -> [bool, str]:
	import importlib

	global remoteAppClient_Install_Path

	try:
		app = importlib.import_module(f"{remoteAppClient_Install_Path}.{appName}")
	except ImportError as e:
		return [False, f"Erro: Unable to import [{appName}]: [{e}]"]
	except Exception as e:
		return [False, f"Erro: Generic error importing [{appName}]: [{e}]"]

	try:
		app.run()
	except AttributeError as e:
		return [False, f"Erro: There is no 'run' method in [{appName}]: [{e}]"]
	except Exception as e:
		return [False, f"Erro: Unable to call 'run' method in [{appName}]: [{e}]"]

	return [True, "Ok"]

def installDependence(dep : str) -> [bool, str]:
	import subprocess

	print(f'Installing [{dep}]')

	try:
		#subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
		subprocess.run([sys.executable, "-m", "pip", "install", dep])
	except:
		return [False, 'Fail']

	return [True, 'Ok']

def installApp(appName : str) -> [bool, str]:
	import importlib

	global remoteAppClient_server, remoteAppClient_server_user, remoteAppClient_server_passwd
	global remoteAppClient_Install_FullPath, remoteAppClient_Install_Path

	ret, retMsg, ftpapp = connectFTP(remoteAppClient_server,
	                                 remoteAppClient_server_user,
	                                 remoteAppClient_server_passwd,
	                                 20, 0)
	if ret == False:
		return [False, retMsg]

	# Get package name (application full name)
	srvapps = appList()

	ret, retMsg = execRetrFTP(ftpapp, 'ASCII', 'apps.txt', srvapps.add)
	if ret == False:
		return [False, retMsg]

	packNameLst = [i[2] for i in srvapps.get() if i[0] == appName]

	if len(packNameLst) == 0:
		return [False, f'Application [{appName}] does not exist']

	packName = packNameLst[0]
	fullPathPackName = path.join(remoteAppClient_Install_FullPath, packName)

	# Get the package

	with open(fullPathPackName, 'wb') as fp:
		ret, retMsg = execRetrFTP(ftpapp, 'BIN', packName, fp.write)
		if ret == False:
			return [False, retMsg]

	ftpapp.quit()

	try:
		with zipfile.ZipFile(fullPathPackName, 'r') as zip_ref:
			zip_ref.extractall(path.join(remoteAppClient_Install_FullPath, appName))
	except:
		return [False, f'Erro unzipping file {fullPathPackName}']

	try:
		remove(fullPathPackName)
	except:
		return [False, f'Erro deleting file {fullPathPackName}']

	# Installing dependences

	try:
		appDeps = importlib.import_module(f"{remoteAppClient_Install_Path}.{appName}")
	except ImportError as e:
		return [False, f"Erro: Unable to import [{appName}] to install dependences: [{e}]"]
	except Exception as e:
		return [False, f"Erro: Generic error importing [{appName}] to install dependences: [{e}]"]

	print(f'Dependencias {appDeps.dependences()}')

	try:
		for i in appDeps.dependences():
			ret, retMsg = installDependence(i)

			if ret == False:
				print(f'Error [{retMsg}]')

	except AttributeError as e:
		return [False, f"Erro: There is no 'dependences' method in [{appName}]: [{e}]"]
	except Exception as e:
		return [False, f"Erro: Unable to call 'dependences' method in [{appName}]: [{e}]"]

	return [True, 'Ok']

def uninstallApp(appName : str) -> [bool, str]:
	import datetime

	global remoteAppClient_Install_Path, remoteAppClient_Bkps_Path

	now = datetime.datetime.now()
	nowtag = now.strftime('%Y%m%d%H%M%S')

	ret, retMsg, ver = getAppVersion(appName)
	if ret == False:
		return [False, retMsg]

	appFullPath = path.join(remoteAppClient_Install_Path, appName)
	appFullPathBackup = path.join(remoteAppClient_Bkps_Path, appName)

	if path.isdir(appFullPath) == False:
		return [False, f'There is no {appFullPath} installed']

	walkdir = walk(appFullPath)
	appFullPathZip = appFullPathBackup + '_' + ver + '_' + nowtag + '.zip'

	trimInstalledPAth = len(f'{remoteAppClient_Install_Path}\\')

	ziphandle = zipfile.ZipFile(appFullPathZip, 'w')

	for i in walkdir:
		if i[0].find('__pycache__') != -1: continue

		for i1 in i[1]: # Directories
			if i1.find('__pycache__') != -1: continue

			fs = path.join(i[0], i1)
			fszip = path.join(i[0][trimInstalledPAth:], i1)

			ziphandle.write(fs, fszip, compress_type = zipfile.ZIP_DEFLATED)

		for i2 in i[2]: # Files
			fs = path.join(i[0], i2)
			fszip = path.join(i[0][trimInstalledPAth:], i2)

			ziphandle.write(fs, fszip, compress_type = zipfile.ZIP_DEFLATED)

	ziphandle.close()

	rmtree(appFullPath)

	###
	### TODO
	### To do the same to Data/appName directory
	###

	return [True, 'Ok']

def listInstalledAppsApp() -> [bool, str]:
	import importlib

	global remoteAppClient_Install_FullPath

	instapp = [x for x in next(walk(remoteAppClient_Install_FullPath))][1]

	if len(instapp) == 0:
		print('No one application installed')

	else:
		print(f"{'Application':30} | Version")

		for i in instapp:

			if path.isdir(path.join(remoteAppClient_Install_FullPath, i)) == False: continue

			ret, retMsg, ver = getAppVersion(i)
			if ret == False:
				continue

			print(f"{i:30} | {ver}")

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

	ret, retMsg, ftpapp = connectFTP(remoteAppClient_server,
	                                 remoteAppClient_server_user,
	                                 remoteAppClient_server_passwd,
	                                 20, 0)
	if ret == False:
		return [False, retMsg]

	srvapps = appList()

	ret, retMsg = execRetrFTP(ftpapp, 'ASCII', 'apps.txt', srvapps.add)
	if ret == False:
		return [False, retMsg]

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

	elif argv[1] == 'uninstall':
		try:
			appName = argv[2]
		except:
			ret, msgRet = False, "uninstall command error!"
		else:
			ret, msgRet = uninstallApp(appName)

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