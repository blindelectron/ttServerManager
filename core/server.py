"""
The custom teamtalk server class used by server manager.
author: blindelectron
"""
from teamtalk import teamtalk
from serverManager import version
from . import commands
import threading
import secrets
import inspect

class server:
	def __init__(self,host: str,port: int,autoSub: bool,jailChannel: str,nickname: str,username: str,password: str,jailed: dict,initialChannel: str):
		self.host=host
		self.port=port
		self.autoSub=autoSub
		self.jailChannel=jailChannel
		self.jailed=jailed
		self.announcers=[]
		self.initialChannel=initialChannel
		if not self.initialChannel.startswith("/"):
			self.initialChannel="/"+self.initialChannel
		if not self.initialChannel.endswith("/"):
			self.initialChannel+="/"
		self.username=username
		self.password=password
		self.nickname=nickname
		self.tcls=teamtalk.TeamTalkServer(self.host,self.port)
		self.commandHandeler=commands.commandHandeler(self)
		self.running=True
		if self.autoSub==True: self.autoSubThread=""
		self.jailThread=""

	def connect(self):
		self.tcls.connect()
		self.tcls.login(self.nickname,self.username,self.password,"server Manager "+version)
		self.tcls.join(self.initialChannel)

	def handleEvents(self):
		@self.tcls.subscribe("messagedeliver")
		def ms(server,params):
			threading.Thread(target=message,args=(self,server,params)).start()
		def message(self,server,params):
			user = server.get_user(params["srcuserid"])
			if params["type"] == teamtalk.USER_MSG:
				nickname = user["nickname"]
				content = params["content"]
				ch=self.handleCommand(content,user,server)
				if ch is not None: self.tcls.user_message(user,ch)
			elif params["type"]==teamtalk.CHANNEL_MSG:
				content = params["content"]
				if user in self.announcers and not content.startswith("/"): self.commandHandeler.cbroadcast(content);return
				elif not content.startswith("/"): return
				elif user["userid"]==server.me["userid"]: return
				ch=self.handleCommand(content,user,server)
				if ch is not None: self.tcls.channel_message(ch,user["chanid"])


	def handleCommand(self,msg,user,server):
		if not user["usertype"]==2: return f'sorry {user["nickname"]}, your not an admin of this server.'
		if msg.startswith("/"): msg=msg.lstrip("/")
		for c in self.commandHandeler.commands:
			if msg.startswith(c) and len(msg.split(" ")[0])==len(c):
				func=c
				break
			else: 
				if self.commandHandeler.commands.index(c)>=len(self.commandHandeler.commands)-1: return f'invalid command, the available commands are {", ".join(self.commandHandeler.commands)}'
				else: continue
		c=func
		func=getattr(commands.commandHandeler,func)
		numArgs=len(inspect.signature(func).parameters)
		if numArgs==1: func=func(self.commandHandeler)
		elif numArgs==2: func=func(self.commandHandeler,msg.lstrip(c).lstrip(" "))
		elif numArgs==3: func=func(self.commandHandeler,msg.lstrip(c).lstrip(" "),user)
		if func is not None:
			return func

	def jail(self,data):
		u=None
		for us in self.jailed.values():
			if data[0] in us["users"]: return 1
			if len(data)>1 and hasattr(u,"ipaddresses") and data[1] in u["ipaddresses"]: return 1
		t=secrets.token_hex(16)
		u=data
		if len(data)>1: self.jailed.update({t:{"users":[u[0]],"ipaddresses":[u[1]]}});return 0
		else: self.jailed.update({t:{"users":[u[0]],"ipaddresses":[]}});return 0

	def unjail(self,data):
		for k,v in self.jailed.items():
			if data==v["users"]: self.jailed.pop(k);return 0
		return 1

	def handleJail(self):
		while self.running:
			self.tcls._sleep(0.2)
			for u in self.tcls.users:
				if u["userid"]==self.tcls.me["userid"]: continue
				for t,d in self.jailed.items():
					if u["username"] in d["users"] and hasattr(d,"ipaddresses") and u["ipaddr"] not in d["ipaddresses"]: d["ipaddresses"].append(u["ipaddr"])
					elif u["username"] in d["users"] and not hasattr(d,"ipaddresses"): d.update({"ipaddresses":[u["ipaddr"]]})
					elif u["ipaddr"] in d["ipaddresses"] and u["username"] not in d["users"]: d["users"].append(u["username"])
					try:
						if u["username"] in d["users"] and not u["chanid"]==self.tcls.get_channel(self.jailChannel)["chanid"]: u.update({"lastid":u["chanid"]});self.tcls.move(u,self.jailChannel)
					except Exception:
						continue

	def handleAutoSub(self):
		for u in self.tcls.users:
			if u["usertype"]==2: self.tcls.subscribe_to(u,teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG)
			lastAddition=self.tcls.users[-1]
		while self.running:
			if self.tcls.users[-1]!=lastAddition and self.tcls.users[-1]["usertype"]==2: self.tcls.subscribe_to(self.tcls.users[-1],teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG);lastAddition=self.tcls.users[-1]

	def startThreads(self):
		self.jailThread=threading.Thread(target=self.handleJail)
		self.jailThread.start()
		if self.autoSub==True:
			self.autoSubThread=threading.Thread(target=self.handleAutoSub)
			self.autoSubThread.start()