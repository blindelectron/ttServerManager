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
from .offlinePm import offlinePM,unJsonafy
import json

class server:
	def __init__(self,host: str,port: int,autoSub: bool,jailChannel: str,nickname: str,username: str,password: str,jailed: dict,initialChannel: str,autoAway: bool,awayChannel: str,name: str,offlinePms: list,configObj):
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
		if self.autoAway==True: self.awayThread=""
		self.jailThread=""
		self.configObj=configObj
		self.name=name
		self.restarting=False
		self.offlinePms=self.__unjsonoffpms__(offlinePms)
		for o in self.offlinePms:
			if o.received==True: self.offlinePms.remove(o)
			self.updateOffLinePms()
		self.awayUsers=[]

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
		@self.tcls.subscribe("loggedin")
		def user(server,params):
			params=self.tcls.get_user(params["userid"])
			for p in self.offlinePms:
				if p.username==params["username"] and p.received==False: self.tcls.user_message(params,f'Offline pm from {p.sender}: {p.message}, reply received to confirm that you have received this message.')
			if self.autoSub==True and params["usertype"]==2: self.tcls.subscribe_to(params,teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG)
			self.handleJail(params)
		@self.tcls.subscribe("updateuser")
		def userup(server,params):
			params=self.tcls.get_user(params["userid"])
			ustat=params["statusmode"]
			if ustat==1 or ustat==4097 or ustat==257 and params not in self.getJailedUsers():
				params.update({"lastid":params["chanid"]})
				self.tcls.move(params,self.awayChannel)
			elif ustat!=1 or ustat!=4097 or ustat!=257 and params not in self.getJailedUsers():
				if params["lastid"] is not None: self.tcls.move(params["userid"],params["lastid"])
		@self.tcls.subscribe("adduser")
		def userad(server,params):
			params=self.tcls.get_user(params["userid"])
			self.handleJail(params)
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
					print(tstr)
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
					print(tstr)

	def checkChannelSlashes(self,channelName: str):
		channelName=channelName
		if not channelName.startswith("/"):
			channelName="/"+channelName
		if not channelName.endswith("/"):
			channelName+="/"
		return channelName

	def handleCommand(self,msg,user,server):
		nonAdminCmds=['offpm','received']

		if msg.startswith("/"): msg=msg.lstrip("/")
		for c in self.commandHandeler.commands:
			if msg.lower().startswith(c) and len(msg.split(" ")[0])==len(c):
				if not user["usertype"]==2 and c not in nonAdminCmds: return f'sorry {user["nickname"]}, your not an admin of this server.'
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
		if len(data)>1: 
			self.jailed.update({t:{"users":[u[0]],"ipaddresses":[u[1]]}})
		else:
			self.jailed.update({t:{"users":[u[0]],"ipaddresses":[]}})
			for user in self.tcls.users: 
				if user["username"]==data[0]: 
					user.update({"lastid":user["chanid"]})
					self.tcls.move(user["userid"],self.jailChannel)
		return 0

	def offLinePm(self,user,message,sender):
		self.offlinePms.append(offlinePM(message,user,sender,False))
		self.updateOffLinePms()

	def updateOffLinePms(self):
		self.configObj.set(self.name,"offlinepms",json.dumps(self.__jsonoffpms__()))
		self.configObj.write()

	def unjail(self,data):
		for k,v in self.jailed.items():
			if data==v["users"]: 
				self.jailed.pop(k)
				user=None
				for u in self.tcls.users:
					if u["username"] in data and "lastid" in u: self.tcls.move(u["userid"],u["lastid"])

				return 0
		return 1 

	def getJailedUsers(self):
		users=[]
		for t,d in self.jailed.items():
			for u in self.tcls.users:
				if u["username"] in d["users"] or u["ipaddr"] in d["ipaddresses"]: users.append(u)
		return users

	def handleJail(self,user):
		for t,d in self.jailed.items():
			done=False
			if user["ipaddr"] in d["ipaddresses"] and user["username"] not in d["users"]: d["users"].append(user["username"]);done=True
			if user["username"] in d["users"] and user["ipaddr"] not in d["ipaddresses"]: d["ipaddresses"].append(user["ipaddr"]);done=True
			if done==True: 
				self.configObj.set(self.name,"jailed",json.dumps(self.jailed))
				self.configObj.write()
		if user in self.getJailedUsers() and not hasattr(user,"chanid"): self.tcls.move(user["userid"],self.jailChannel)
		elif user in self.getJailedUsers() and user["chanid"]!=self.tcls.get_channel(self.jailChannel)["chanid"]: self.tcls.move(user["userid"],self.jailChannel)

	def __jsonoffpms__(self):
		pms=[]
		for o in self.offlinePms:
			pms.append(o.jsonify())
		return pms

	def __unjsonoffpms__(self,pmlist: list):
		pms=[]
		for o in pmlist:
			pms.append(unJsonafy(o))
		return pms