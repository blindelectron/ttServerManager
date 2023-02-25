"""
The configuration functions for serverManager.
author: blindelectron
"""
import configparser
import json
config=configparser.ConfigParser()

def read():
	config.read("config.ini")

def getServerParams(serverName: str):
	server=""
	if config.has_section("server "+serverName): server="server "+serverName
	else: raise RuntimeError(f'Server {serverName} not found.')
	neededOptions=['host','tcpport','username','password','jailchannel']
	for n in neededOptions:
		if not config.has_option(server,n): raise RuntimeError(f'missing needed configuration option: {n}')
	username=config.get(server,"username")
	password=config.get(server,"password")
	host=config.get(server,"host")
	port=config.get(server,"tcpport")
	jailchan=config.get(server,"jailchannel")
	nickname="serverManager"
	jailed={}
	autoSub=True
	autoAway=False
	channel="/"
	if config.has_option(server,"nickname"): nickname=config.get(server,"nickname")
	if config.has_option(server,"initialchannel"): channel=config.get(server,"initialchannel")
	if config.has_option(server,"autosubscribe"): autoSub=config.getboolean(server,"autosubscribe")
	if config.has_option(server,"autoaway"): autoAway=config.getboolean(server,"autoaway")
	awayChannel=""
	if autoAway==True:
		if not config.has_option(server,"awaychannel"): raise RuntimeError("if the awto away option is enabled, an away channel must be spesified eg:\n awaychannel=/away/")
		awayChannel=config.get(server,"awaychannel")
	if config.has_option(server,"jailed"): jailed=json.loads(config.get(server,"jailed"))
	params=(host,port,autoSub,jailchan,nickname,username,password,jailed,channel,autoAway,awayChannel)
	return params

def getServers():
	servers=config.sections()
	servers=[s for s in servers if s.lower().startswith("server ")]
	sers=[]
	for s in servers:
		s=s.lstrip("server ")
		sers.append(s)
	return sers

def updateJailed(serverName: str,jailed: dict):
	server=""
	if config.has_section("server "+serverName): server="server "+serverName
	else: raise RuntimeError(f'Server {serverName} not found.')
	config.set(server,"jailed",json.dumps(jailed))

def  set(serverName,option: str,value):
	server=""
	if config.has_section("server "+serverName): server="server "+serverName
	else: raise RuntimeError(f'Server {serverName} not found.')
	config.set(server,option,str(value))

def getopt(section: str,option: str):
	opt=None
	try:
		opt=config.getboolean(section,option)
		return opt
	except:
		pass
	try:
		opt=config.getint(section,option)
		return opt
	except:
		pass
	try:
		opt=config.get(section,option)
		return opt
	except:
		pass
	raise RuntimeError(f'error geting configuration option {option}: the option {option} is not a valid configuration data type.')

def getJailed(serverName):
	if not config.has_option("server "+serverName,"jailed"): return {}
	return json.loads(config.get("server "+serverName,"jailed"))

def write():
	with open("config.ini","w") as c:
		config.write(c,False)
