from cpu import cpu
from ppu import ppu
from cartridge import cartridge

class bus:
	def __init__(self):
		self.cpuram = bytearray(2048)
		self.cpu = cpu(self.cpuram, self)

		self.ppu = ppu()
		self.systemClockCounter = 0

	def cpuWrite(self, addr, data):
		if self.cartridge.cpuWrite(addr, data):
			pass
		elif addr >= 0x0000 and addr <= 0x1FFF:
			print("cpu write addr:", addr & 0x07FF)
			self.cpuram[addr & 0x07FF] = data
		elif addr >= 0x2000 and addr <= 0x3FFF:
			print("ppu write addr:", addr & 0x0007)
			self.ppu.cpuWrite(addr & 0x0007, data)

	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00
		if self.cartridge.cpuRead(addr):
			self.trash, self.data = self.cartridge.cpuRead(addr)
		elif addr >= 0x0000 and addr <= 0x1FFF:
			print("cpu read addr:", addr & 0x07FF)
			self.data = self.cpuram[addr & 0x07FF]
		elif addr >= 0x2000 and addr <= 0x3FFF:
			print("ppu read addr:", addr & 0x0007)
			self.data = self.ppu.cpuRead(addr & 0x0007)
		return self.data



	def insertCartridge(self, filename):
		self.cartridge = cartridge(filename)
		self.ppu.connectCartridge(self.cartridge)

	def reset(self):
		self.cpu.reset()
		self.systemClockCounter = 0

	def clock(self):
		self.ppu.clock()
		if self.systemClockCounter % 3 == 0:
			self.cpu.clock()
		self.systemClockCounter += 1
