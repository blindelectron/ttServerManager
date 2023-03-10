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
import traceback

class server:
	def __init__(self,host: str,port: int,autoSub: bool,jailChannel: str,nickname: str,username: str,password: str,jailed: dict,initialChannel: str,autoAway: bool,awayChannel: str,configObj,name: str):
		self.host=host
		self.port=port
		self.autoSub=autoSub
		self.autoAway=autoAway
		self.jailChannel=self.checkChannelSlashes(jailChannel)
		self.jailed=jailed
		self.announcers=[]
		self.initialChannel=self.checkChannelSlashes(initialChannel)
		self.awayChannel=self.checkChannelSlashes(awayChannel)
		self.username=username
		self.password=password
		self.nickname=nickname
		self.tcls=teamtalk.TeamTalkServer(self.host,self.port)
		self.commandHandeler=commands.commandHandeler(self)
		self.running=True
		if self.autoSub==True: self.autoSubThread=""
		if self.autoAway==True: self.awayThread=""
		self.jailThread=""
		self.configObj=configObj
		self.name=name
		self.restarting=False

	def connect(self):
		try:
			self.tcls.connect()
		except ConnectionRefusedError:
			print(f'connection was refused by the server {self.name}, retrying in 5 seconds')
			self.tcls._sleep(5)
			self.connect()
		self.tcls.login(self.nickname,self.username,self.password,"server Manager "+version)
		self.tcls.join(self.initialChannel)

	def disconnect(self):
		self.tcls.leave()
		self.tcls.disconnect()
		self.running=False

	def handleEvents(self):
		@self.tcls.subscribe("messagedeliver")
		def ms(server,params):
			threading.Thread(target=message,args=(self,server,params)).start()
		def message(self,server,params):
			user = server.get_user(params["srcuserid"])
			if params["type"] == teamtalk.USER_MSG:
				nickname = user["nickname"]
				content = params["content"]
				try:
					ch=self.handleCommand(content,user,server)
					if ch is not None: self.tcls.user_message(user,ch)
				except Exception:
					tstr=traceback.format_exc()
					self.tcls.user_message(user,tstr)
			elif params["type"]==teamtalk.CHANNEL_MSG:
				content = params["content"]
				if user in self.announcers and not content.startswith("/"): self.commandHandeler.cbroadcast(content);return
				elif not content.startswith("/"): return
				elif user["userid"]==server.me["userid"]: return
				try:
					ch=self.handleCommand(content,user,server)
					if ch is not None: self.tcls.channel_message(ch,user["chanid"])
				except Exception:
					tstr=traceback.format_exc()
					self.tcls.channel_message(tstr,user["chanid"])

	def checkChannelSlashes(self,channelName: str):
		if not channelName.startswith("/"):
			channelName="/"+channelName
		if not channelName.endswith("/"):
			channelName+="/"
		return channelName

	def handleCommand(self,msg,user,server):
		if not user["usertype"]==2: return f'sorry {user["nickname"]}, your not an admin of this server.'
		if msg.startswith("/"): msg=msg.lstrip("/")
		for c in self.commandHandeler.commands:
			if msg.lower().startswith(c) and len(msg.split(" ")[0])==len(c):
				func=c
				break
			else: 
				if self.commandHandeler.commands.index(c)>=len(self.commandHandeler.commands)-1: return f'invalid command, the available commands are {", ".join(self.commandHandeler.commands)}'
				else: continue
		c=func
		func=getattr(commands.commandHandeler,func)
		numArgs=len(inspect.signature(func).parameters)
		if numArgs==1: func=func(self.commandHandeler)
		elif numArgs==2: func=func(self.commandHandeler,msg[len(c):].lstrip(" "))
		elif numArgs==3: func=func(self.commandHandeler,msg[len(c):].lstrip(" "),user)
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

	def getJailedUsers(self):
		users=[]
		for t,d in self.jailed.items():
			for u in self.tcls.users:
				if u["username"] in d["users"]: users.append(u)
		return users

	def handleAutoSub(self):
		for u in self.tcls.users:
			if u["usertype"]==2: self.tcls.subscribe_to(u,teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG)
			lastAddition=self.tcls.users[-1]
		while self.running:
			if self.tcls.users[-1]!=lastAddition and self.tcls.users[-1]["usertype"]==2: self.tcls.subscribe_to(self.tcls.users[-1],teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG);lastAddition=self.tcls.users[-1]

	def handleAutoAway(self):
		awayUsers=[]
		while True:
			self.tcls._sleep(0.2)
			for user in self.tcls.users:
				if user in awayUsers: continue
				ustat=user["statusmode"]
				if ustat==1 or ustat==4097 or ustat==257:
					if user in self.getJailedUsers(): continue
					user.update({"lastid":user["chanid"]})
					self.tcls.move(user,self.awayChannel)
					awayUsers.append(user)
			for user in awayUsers:
				if user in self.getJailedUsers(): continue
				try:
					if user["chanid"]==self.tcls.get_channel(self.awayChannel)["chanid"]:
						ustat=user["statusmode"]
						if ustat!=1 and ustat!=257 and ustat!=4097: awayUsers.remove(user);self.tcls.move(user,user["lastid"]);user.pop("lastid")
				except:
					continue


	def startThreads(self):
		self.jailThread=threading.Thread(target=self.handleJail,name=self.name+": jail")
		self.jailThread.start()
		if self.autoSub==True:
			self.autoSubThread=threading.Thread(target=self.handleAutoSub,name=self.name+": auto subscribe")
			self.autoSubThread.start()
		if self.autoAway==True:
			self.awayThread=threading.Thread(target=self.handleAutoAway,name=self.name+": auto away")
			self.awayThread.start()