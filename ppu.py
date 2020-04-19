from cartridge import cartridge

class ppu:
	def cpuRead(self, addr, readOnly):
		data = 0
		if addr == 0: #Controll
			pass
		elif addr == 1: #Mask
			pass
		elif addr == 2: #Status
			pass
		elif addr == 3: #OAM address
			pass
		elif addr == 4: #OAM data
			pass
		elif addr == 5: #Scroll
			pass
		elif addr == 6: #PPU address
			pass
		elif addr == 7: #PPU data
			pass
		return data

	def cpuWrite(self, addr, data):
		if addr == 0: #Controll
			pass
		elif addr == 1: #Mask
			pass
		elif addr == 2: #Status
			pass
		elif addr == 3: #OAM address
			pass
		elif addr == 4: #OAM data
			pass
		elif addr == 5: #Scroll
			pass
		elif addr == 6: #PPU address
			pass
		elif addr == 7: #PPU data
			pass

	def ppuRead(self, addr, readOnly):
		data = 0
		addr = addr & 16383

		return data
	def ppuWrite(self, addr, data):
		addr = addr & 16383

	def connectCartridge(self, cartridge):
		pass

	def clock(self):
		pass
