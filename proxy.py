import socket
from threading import Thread
import parser_file as parser
from importlib import reload
class Proxy2Server(Thread):

	def __init__(self, host, port):
		super(Proxy2Server, self).__init__()
		self.game = None # Will later be the socket connected to game client
		self.host = host
		self.port = port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.connect((host, port))

	# run in thread
	def run(self):
		while True:
			data = self.server.recv(4096)
			try:
				reload(parser)
				parser.parse(data, self.port, 'server')
			except Exception as e:
				print(f'client[{self.port}] {e}')
			#print(f"[{self.port}] <- {data.hex()}")
			if data:
				# forward to client (we don't have one rn)
				self.game.sendall(data)

class Game2Proxy(Thread):

	def __init__(self, host, port):
		super(Game2Proxy, self).__init__()
		self.server = None
		self.port = port 
		self.host = host
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((host, port))
		sock.listen(1)
		# waiting for a connection
		self.game, addr = sock.accept()

	def run(self):
		while True:
			data = self.game.recv(4096)
			if data:
				try:
					reload(parser)
					data = parser.parse(data, self.port, 'client')
				except Exception as e:
					print(f'server[{self.port}] {e}')
				# forward to server
				self.server.sendall(data)

class Proxy(Thread):

	def __init__(self, from_host, to_host, port):
		super(Proxy, self).__init__()
		self.from_host = from_host
		self.to_host = to_host
		self.port = port

	def run(self):
		while True:
			print("[proxy({})] setting up".format(self.port))
			self.g2p = Game2Proxy(self.from_host, self.port)
			self.p2s = Proxy2Server(self.to_host, self.port)	
			print("[proxy({})] connection established".format(self.port))
			self.g2p.server = self.p2s.server
			self.p2s.game = self.g2p.game

			self.g2p.start()
			self.p2s.start()

real_ip = 'vidyascape.org'
real_port = 43594

master_server = Proxy('0.0.0.0', real_ip, real_port)
master_server.start()

for port in range(real_port-3, real_port+3):
	_game_server = Proxy('0.0.0.0', real_ip, port)
	_game_server.start()