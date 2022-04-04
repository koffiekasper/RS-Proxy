global viewChat
viewClient = True
viewServer = False

# Client stuff
viewChat = True
viewClick = True
viewMove = False
viewRestClient = False

viewRestServer = True
viewEmptyServer = False

def parse(data, port, origin):
	if origin == 'client' and viewClient:
		if isChatMessage(data):
			if viewChat:	
	#			data = alterChatMessage(data)
				parseChatMessage(data)
#			print(f"[{origin}({port})] 'Outgoing Chat message:' {data}")
		elif isClickMessage(data):
			if viewClick:
				print(f"[{origin}({port})] Click message {data}")
		elif isMoveMessage(data):
			if viewMove:
				print(f"[{origin}({port})] Move message {data}")

		else:
			if viewRestClient:
				print(f"[{origin}({port})] {data}")
	elif origin == 'server' and viewServer:
		if len(data) == 0:
			if viewEmptyServer:
				print(f"[{origin}({port})] {data}")
		else:
			if viewRestServer:
				print(f"[{origin}({port})] {data}")
	return data

	# Checks bytes 2 and 3 if they are empty
def isClickMessage(data):
	if data[1:3] == b'\x00\x00':
		return True
	return False

def isMoveMessage(data):
	if data[-2:] == b'\x0c\x00':
		return True
	return False

	# Checks bytes 3 and 4. Returns true if they are both x80
def isChatMessage(data):
	if data[2:4] == b'\x80\x80':
		return True
	else:
		return False

def parseChatMessage(data):
	print(f"[CHAT OUT] {data}")

def alterChatMessage(data):
	fixChatLengthByte(data)
	data = data + data[4:] + b"\xa5\x87\x84\x85\x82\x8f\x81\x98\x87\x85\x80\x81\x92\x83\x88\x88\x81\x8d"
	data = fixChatLengthByte(data)
	return data

def fixChatLengthByte(data):
	messageLength = len(data[4:])
	newData = data[:1] + (messageLength+2).to_bytes(1, byteorder='big') + data[2:]
	return newData