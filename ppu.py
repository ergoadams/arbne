from cartridge import cartridge

class ppu:
	def __init__(self):
		self.tblName = bytearray(2*1024)
		self.tblPalette = bytearray(32)
		self.cycle = 0
		self.scanline = 0
		self.framecomplete = False

	#Communication with main bus
	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00
		if addr == 0x0000: #Controll
			pass
		elif addr == 0x0001: #Mask
			pass
		elif addr == 0x0002: #Status
			pass
		elif addr == 0x0003: #OAM address
			pass
		elif addr == 0x0004: #OAM data
			pass
		elif addr == 0x0005: #Scroll
			pass
		elif addr == 0x0006: #PPU address
			pass
		elif addr == 0x0007: #PPU data
			pass
		return self.data

	def cpuWrite(self, addr, data):
		if addr == 0x0000: #Controll
			pass
		elif addr == 0x0001: #Mask
			pass
		elif addr == 0x0002: #Status
			pass
		elif addr == 0x0003: #OAM address
			pass
		elif addr == 0x0004: #OAM data
			pass
		elif addr == 0x0005: #Scroll
			pass
		elif addr == 0x0006: #PPU address
			pass
		elif addr == 0x0007: #PPU data
			pass

	#Communication with ppu bus
	def ppuRead(self, addr, readOnly = False):
		self.data = 0x00
		addr = addr & 0x3FFF

		if self.cartridge.ppuRead(addr, readOnly):
			pass

		return self.data
	def ppuWrite(self, addr, data):
		addr = addr & 0x3FFF
		if self.cartridge.ppuWrite(addr, data):
			pass

	def connectCartridge(self, cartridge):
		self.cartridge = cartridge

	def clock(self):
		#color one pixel at cycle-1;scanline
		self.cycle += 1
		if self.cycle >= 341:
			self.cycle = 0
			self.scanline += 1
			if self.scanline >= 261:
				self.scanline = -1
				self.framecomplete = True
