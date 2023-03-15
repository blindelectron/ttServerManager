"""
Offline message class for server manager.
author: blindelectron
"""
class offlinePM:
	def __init__(self, message: str, username: str, sender: str, received: bool):
		self.message=message
		self.username=username
		self.sender=sender
		self.received=received

	def jsonify(self):
			return {"username":self.username,"message":self.message,"sender":self.sender,"received":self.received}

def unJsonafy(dct):
	return offlinePM(dct["message"],dct["username"],dct["sender"],dct["received"])