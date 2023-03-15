"""
command Handeler for server manager.
author: blindelectron
"""
from teamtalk import teamtalk
import shlex
import re
import secrets

def getDictFromMessage(msg):
	pattern = r'\b(\w+)\s*=\s*(.+?)\s*(?=\b\w+\s*=|\b$)'
	matches = re.findall(pattern, msg)
	data=dict(matches)
	return data

def getListFromMessage(msg):
	data=msg.split("::")
	return data

class commandHandeler:
	def __init__(self,server):
		self.commands = [i for i in dir(self) if not i.startswith("_") if callable(getattr(self,i))]
		self.server=server
  
	def cbroadcast(self,message):
		for c in self.server.tcls.channels:
			self.server.tcls.channel_message(message,c)

	def pbroadcast(self,msg):
		msg=msg
		for u in self.server.tcls.users:
			if u["userid"]==self.server.tcls.me["userid"]: continue
			self.server.tcls.user_message(u,msg)

	def motd(self,msg):
		return self.server.tcls.server_params["motd"]

	def offpm(self,msg,user):
		data=getDictFromMessage(msg)
		if "message" not in data: return "You must provide a message to send."
		elif "user" not in data: return "You must provide a user to send this message to."
		sender=user["nickname"]
		username=""
		for a in self.server.tcls.getAccounts():
			if a["username"]==data["user"]: username=data["user"]
		if username=="": return f'the user {data["user"]}, was not found on the server.'
		self.server.offLinePm(username,data["message"],sender)

	def received(self,msg,user):
		done=False
		for o in self.server.offlinePms:
			if user["username"]==o.username: o.received=True;done=True
		if not done: return "You have no offline messages."
		if done: 
			self.server.updateOffLinePms()
			return "Your offline messages have been cleared."

	def join(self,msg):
		c=None
		for ch in self.server.tcls.channels:
			if ch["channel"].lstrip("/").rstrip("/") in msg: c=ch
		if c is None: return "channel not found."
		passwd=msg.split(c["channel"].lstrip("/").rstrip("/")+" ")
		if len(passwd)>2: passwd=passwd[1]
		else: passwd=""
		if not passwd=="": self.server.tcls.join(c,passwd)
		else: self.server.tcls.join(c)

	def kickall(self,msg):
		for u in self.server.tcls.users:
			if self.server.tcls.me["userid"]==u["userid"]: continue
			self.server.tcls.kick(u)

	def kick(self,msg):
		u=[]
		for ul in getListFromMessage(msg):
			for us in self.server.tcls.users:
				if us["nickname"] in msg: u.append(us)
		if u==[]: return "User not found."
		for user in u:
			self.server.tcls.kick(user)
 
	def jail(self,msg):
		u=""
		for us in self.server.tcls.users:
			if us["nickname"]==msg: 
				u=us
		if u=="":
			for us in self.server.tcls	.getAccounts():
				if us["username"]==msg:
					u=us
		if u=="": return f'the user {msg}, was not found.'
		data=[]
		data.append(u["username"])
		if hasattr(u,"ipaddr")!=False: data.append(u["ipaddr"])
		stat=self.server.jail(data)
		if stat==0: return f'the user {u["username"]}, is now in jail.'
		else: return f'the user {u["username"]}, is already in jail'

	def unjail(self,msg):
		u=None
		for us in self.server.jailed.values():
			if msg in us["users"]: 
				u=us
				uns=self.server.unjail(us["users"])
				if uns==0: 
					return f'the user {str(us["users"])}, has been removed from jail'
				else: return f'The user {msg}, is already out of jail.'
		if u is None: return f'the user {msg}, was not found.'

	def move(self,msg):
		u=[]
		nu=[]
		for ul in getListFromMessage(msg):
			for us in self.server.tcls.users:
				if us["nickname"] in ul: u.append(us)
		if u==[]: return "user not found."
		c=None
		for ch in self.server.tcls.channels:
			if ch["channel"].lstrip("/").rstrip("/") in msg and ch["channel"].lstrip("/").rstrip("/")!="": c=ch;print("found channel "+ch["channel"].lstrip("/").rstrip("/"))
			elif ch["channel"] in msg: c=ch
		if c is None: return "channel not found."
		for user in u:
			if user["chanid"] is not None and user["chanid"]==ch["chanid"]: continue
			self.server.tcls.move(user,c)

	def pm(self,msg):
		u=""
		for us in self.server.tcls.users:
			if us["nickname"] in msg: u=us;break
		if u=="": return "user not found"
		self.server.tcls.user_message(u,msg.split(u["nickname"]+" ")[1])

	def broadcast(self,msg):
		self.server.tcls.broadcast_message(msg)

	def ban(self,msg):
		u=[]
		for ul in getListFromMessage(msg):
			for us in self.server.tcls.users:
				if us["nickname"] in ul: u.append(us["userid"])
		if u==[]: return "User not found."
		for user in u:
			self.server.tcls.ban(user)
		self.server.tcls.kick(user)

	def unban(self,msg):
		u=None
		for us in self.server.tcls.getBans():
			if us["nickname"] in msg: u=us["ipaddr"]
			elif us["ipaddr"] in msg: u=us["ipaddr"]
		if u is None: return "user not found or already unbanned."
		self.server.tcls.unban(u)

	def help(self,msg):
		return f'commands for {self.server.tcls.get_user(self.server.tcls.me["userid"])["clientname"]}, {", ".join(self.commands)}'

	def bans(self,msg):
		return str(self.server.tcls.getBans())

	def announcer(self,msg):
		u=""
		for us in self.server.tcls.users:
			if us["nickname"] in msg: u=us
		if u=="": return "user not found"
		if u in self.server.announcers: 
			self.server.announcers.remove(u)
			if not self.server.autoSub: server.tcls.unsubscribe_from(u,teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG)
			self.cbroadcast(f'user {u["nickname"]} is no longer announcing')
			return
		if not self.server.autoSub: server.tcls.subscribe_to(u,teamtalk.SUBSCRIBE_INTERCEPT_CHANNEL_MSG)
		self.cbroadcast(f'user {u["nickname"]} is now announcing')
		self.server.announcers.append(u)

	def accounts(self,msg):
		return str(self.server.tcls.getAccounts())

	def newaccount(self,msg):
		data=getDictFromMessage(msg)
		for u in self.server.tcls.getAccounts():
			if u["username"]==data["username"]: return f'the account {u["username"]} already exists, try a different name'
		self.server.tcls.newAccount(data["username"],data["password"],int(data["type"]))

	def delaccount(self,msg):
		u=None
		for us in self.server.tcls.getAccounts():
			if us["username"]==msg: u=us
		if u is None: return "useraccount "+msg+" not found."
		self.server.tcls.deleteAccount(u["username"])

	def talkto(self,msg,user):
		u=[]
		for ul in getListFromMessage(msg):
			for us in self.server.tcls.users:
				if us["nickname"] in msg: 
					if us["userid"]==user["userid"]: return "Sorry, you can not talk to yourself."
					u.append(us)
		if u==[]: return "user not found."
		u.append(user)
		un=[]
		for ul in u:
			if u.index(ul)>=len(u)-1: break
			un.append(ul["nickname"])
		self.server.tcls.send(f'makechannel parentid=1 name="{u[-1]["nickname"]} talking to {", ".join(un)}" password={secrets.token_hex(32)} audiocodec=[3,48000,2,2049,10,1,0,64000,0,0,1920,1] audiocfg=[0,0]')
		self.server.tcls._sleep(0.2)
		for ul in u:
			self.server.tcls.move(ul,f'/{u[-1]["nickname"]} talking to {", ".join(un)}/')

	def setconfig(self,msg):
		settings=getDictFromMessage(msg)
		for k,v in settings.items():
			self.server.configObj.set(self.server.name,str(k),str(v))
			self.server.configObj.write()


	def quit(self):
		self.server.disconnect()

	def restart(self):
		self.server.restarting=True
		self.server.disconnect()
