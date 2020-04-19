from ppu import ppu
from cpu import cpu
from cartridge import cartridge

class bus:
	def __init__(self, ram, ppu, cartridge):
		self.ram = ram
		self.ppu = ppu
		self.cartridge = cartridge
		self.systemClockCounter = 0

	def cpuWrite(self, addr, data):
		if addr >= 0 and addr <= 8191:
			self.ram[addr & 2047] = data
		elif addr >= 8192 and addr <= 16383:
			ppu.cpuWrite(addr & 7, data)

	def cpuRead(self, addr, readOnly):
		self.data = 0
		if addr >= 0 and addr <= 8191:
			print("read cpu addr:", addr & 2047)
			data = self.ram[addr & 2047]
		elif addr >= 8192 and addr <= 16383:
			print("read ppu addr:", addr & 7)
			data = ppu.cpuRead(addr & 7, readOnly)
		return data

	def insertCartridge(self, cartridge):
		self.cartridge = cartridge()
		ppu.connectCartridge(self.cartridge)

	def reset():
		cpu.reset()
		self.systemClockCounter = 0

	def clock():
		pass
