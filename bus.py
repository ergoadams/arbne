from cpu import cpu
from ppu import ppu
from cartridge import cartridge
import time

class bus:
	def __init__(self):
		self.cpu = cpu(self)
		self.ppu = ppu()

		self.systemClockCounter = 0

	def cpuWrite(self, addr, data):
		if self.cartridge.cpuWrite(addr, data):
			pass

		elif addr >= 0x0000 and addr <= 0x1FFF:
			#print(addr, data)
			self.cpu.cpuram[addr & 0x07FF] = data

		elif addr >= 0x2000 and addr <= 0x3FFF:
			self.ppu.cpuWrite(addr & 0x0007, data)

	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00
		self.tempcheck, self.data = self.cartridge.cpuRead(addr)
		if self.tempcheck == True:
			pass
		elif addr >= 0x0000 and addr <= 0x1FFF:
			self.data = self.cpu.cpuram[addr & 0x07FF]

		elif addr >= 0x2000 and addr <= 0x3FFF:
			self.data = self.ppu.cpuRead(addr & 0x0007, readOnly)

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

		if self.ppu.nmi == True:
			self.ppu.nmi = False
			self.cpu.nmi()

		self.systemClockCounter += 1
