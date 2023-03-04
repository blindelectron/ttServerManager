import teamtalk
import threading
import sys
import os
from core import server,config
import json
import traceback

version="1.0"

def main():
	servers={}
	config.read()
	for s in config.getServers():
		servers.update({s:server.server(*config.getServerParams(s))})
	serverThreads=[]
	for sn,s in servers.items():
		t=threading.Thread(target=handleServerSetUp,args=(s,sn),name=sn)
		t.start()
		serverThreads.append(t)

def handleServerSetUp(serverobj,serverName: str):
	serverobj.connect()
	serverobj.handleEvents()
	serverobj.startThreads()
	threading.Thread(target=handleJailUpDates,args=(serverobj,serverName),name=serverName+"_jailUpdater").start()
	while serverobj.running:
		try:
			serverobj.tcls.handle_messages()
		except Exception:
			pass
	if serverobj.restarting:
		serverobj.__init__(*config.getServerParams(serverName))
		return handleServerSetUp(serverobj,serverName)



def handleJailUpDates(serverobj,serverName):
	while serverobj.running:
		j=serverobj.jailed
		if j!=config.getJailed(serverName): config.updateJailed(serverName,serverobj.jailed);config.write()

if __name__=="__main__": main()