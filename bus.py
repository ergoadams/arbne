class bus:
	def __init__(self, ram):
		self.ram = ram

	def write(self, addr, data):
		if addr >= 0 and addr <= 65535:
			self.ram[addr] = data

	def read(self, addr, readOnly):
		if addr >= 0 and addr <= 65535:
			print("read addr:", addr)
			return self.ram[addr]
		return 0
