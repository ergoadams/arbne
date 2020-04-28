class mapper:
	class mapper_000:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
		def reset(self):
			pass
		def irqState(self):
			pass
		def irqClear(self):
			pass
		def scanline(self):
			pass
		def cpuMapRead(self, addr):
			if addr >= 0x8000  and addr <= 0xFFFF:
				return True, addr & 0x7FFF if self.prgBanks > 1 else addr & 0x3FFF, 0
			return False, addr, 0
		def cpuMapWrite(self, addr, data):
			if addr >= 0x8000  and addr <= 0xFFFF:
				return True, addr & 0x7FFF if self.prgBanks > 1 else addr & 0x3FFF
			return False, addr
		def ppuMapRead(self, addr):
			if addr >= 0  and addr <= 0x1FFF:
				return True, addr
			return False, addr
		def ppuMapWrite(self, addr):
			return True if addr >= 0x0000 and addr <= 0x1FFF and self.chrBanks == 0 else False

	class mapper_001:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
			self.CHRbankSelect4Lo = 0
			self.CHRbankSelect4Hi = 0
			self.CHRbankSelect8 = 0
			self.PRGbankSelect16Lo = 0
			self.PRGbankSelect16Hi = 0
			self.PRGbankSelect32 = 0
			self.loadRegister = 0
			self.loadRegisterCount = 0
			self.controlRegister = 0
			self.mirrormode = "HORIZONTAL"
			self.ramStatic = bytearray(32 * 1024)
		def reset(self):
			self.controlRegister = 0x1C
			self.loadRegister = 0
			self.loadRegisterCount = 0
			self.CHRbankSelect4Lo = 0
			self.CHRbankSelect4Hi = 0
			self.CHRbankSelect8 = 0
			self.PRGbankSelect32 = 0
			self.PRGbankSelect16Lo = 0
			self.PRGbankSelect16Hi = self.prgBanks - 1
		def mirror(self):
			return self.mirrormode
		def irqState(self):
			pass
		def irqClear(self):
			pass
		def scanline(self):
			pass
		def cpuMapRead(self, addr):
			if addr >= 0x6000  and addr <= 0x7FFF:
				return True, 0xFFFFFFFF, self.ramStatic[addr & 0x1FFF]
			if addr >= 0x8000:
				if self.controlRegister & 0b01000:
					if addr >= 0x8000 and addr <= 0xBFFF:
						return True, self.PRGbankSelect16Lo * 0x4000 + (addr & 0x3FFF), 0
					if addr >= 0xC000 and addr <= 0xFFFF:
						return True, self.PRGbankSelect16Hi * 0x4000 + (addr & 0x3FFF), 0
				else:
					return True, self.PRGbankSelect32 * 0x8000 + (addr & 0x7FFF), 0
			return False, addr, 0
		def cpuMapWrite(self, addr, data):
			if addr >= 0x6000  and addr <= 0x7FFF:
				self.ramStatic[addr & 0x1FFF] = data
				return True, 0xFFFFFFFF
			if addr >= 0x8000:
				if data & 0x80:
					self.loadRegister = 0x00
					self.loadRegisterCount = 0
					self.controlRegister |= 0x0C
				else:
					self.loadRegister >>= 1
					self.loadRegister |= (data & 0x01) << 4
					self.loadRegisterCount += 1
					if self.loadRegisterCount == 5:
						self.targetRegister = (addr >> 13) & 0x03
						if self.targetRegister == 0:
							self.controlRegister = self.loadRegister & 0x1F
							self.switchcase = self.controlRegister & 0x03
							if self.switchcase == 0:
								self.mirrormode = "ONESCREEN_LO"
							elif self.switchcase == 1:
								self.mirrormode = "ONESCREEN_HI"
							elif self.switchcase == 2:
								self.mirrormode = "VERTICAL"
							elif self.switchcase == 3:
								self.mirrormode = "HORIZONTAL"
						elif self.targetRegister == 1:
							if self.controlRegister & 0b10000:
								self.CHRbankSelect4Lo = self.loadRegister & 0x1F
							else:
								self.CHRbankSelect8 = self.loadRegister & 0x1E
						elif self.targetRegister == 2:
							if self.controlRegister & 0b10000:
								self.CHRbankSelect4Hi = self.loadRegister & 0x1F
						elif self.targetRegister == 3:
							self.PRGmode = (self.controlRegister >> 2) & 0x03
							if self.PRGmode == 0 or self.PRGmode == 1:
								self.PRGbankSelect32 = (self.loadRegister & 0x0E) >> 1
							elif self.PRGmode == 2:
								self.PRGbankSelect16Lo = 0
								self.PRGbankSelect16Hi = self.loadRegister & 0x0F
							elif self.PRGmode == 3:
								self.PRGbankSelect16Lo = self.loadRegister & 0x0F
								self.PRGbankSelect16Hi = self.prgBanks -1
						self.loadRegister = 0
						self.loadRegisterCount = 0
			return False, addr
		def ppuMapRead(self, addr):
			if addr >= 0x0000  and addr <= 0x1FFF:
				if self.chrBanks == 0:
					return True, addr
				else:
					if self.controlRegister & 0b10000:
						if addr >= 0 and addr <= 0x0FFF:
							return True, self.CHRbankSelect4Lo * 0x1000 + (addr & 0x0FFF)
						if addr >= 0x1000 and addr <= 0x1FFF:
							return True, self.CHRbankSelect4Hi * 0x1000 + (addr & 0x0FFF)
					else:
						return True, self.CHRbankSelect8 * 0x2000 + (addr & 0x1FFF)
			return False, addr
		def ppuMapWrite(self, addr):
			return True if addr >= 0x0000 and addr <= 0x1FFF else False

	class mapper_002:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
			self.PRGbankSelectLo = 0
			self.PRGbankSelectHi = 0
		def reset(self):
			self.PRGbankSelectLo = 0
			self.PRGbankSelectHi = self.prgBanks - 1
		def irqState(self):
			pass
		def irqClear(self):
			pass
		def scanline(self):
			pass
		def cpuMapRead(self, addr):
			if addr >= 0x8000  and addr <= 0xBFFF:
				return True, self.PRGbankSelectLo * 0x4000 + (addr & 0x3FFF), 0
			if addr >= 0xC000 and addr <= 0xFFFF:
				return True, self.PRGbankSelectHi * 0x4000 + (addr & 0x3FFF), 0
			return False, addr, 0
		def cpuMapWrite(self, addr, data):
			if addr >= 0x8000  and addr <= 0xFFFF:
				self.PRGbankSelectLo = data & 0x0F
			return False, addr
		def ppuMapRead(self, addr):
			if addr >= 0  and addr <= 0x1FFF:
				return True, addr
			return False, addr
		def ppuMapWrite(self, addr):
			return True if addr >= 0 and addr <= 0x1FFF and self.chrBanks == 0 else False

	class mapper_003:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
			self.CHRbankSelect = 0
		def reset(self):
			self.CHRbankSelect = 0
		def irqState(self):
			pass
		def irqClear(self):
			pass
		def scanline(self):
			pass
		def cpuMapRead(self, addr):
			if addr >= 0x8000  and addr <= 0xFFFF:
				return True, addr & 0x3FFF if self.prgBanks == 1 else addr & 0x7FFF if self.prgBanks == 2 else 0
			return False, addr
		def cpuMapWrite(self, addr, data):
			if addr >= 0x8000  and addr <= 0xFFFF:
				self.CHRbankSelect = data & 0x03
			return False, addr
		def ppuMapRead(self, addr):
			return False, addr
		def ppuMapWrite(self, addr):

			return True if addr >= 0x0000 and addr <= 0x1FFF and self.chrBanks == 0 else False

	class mapper_004:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
			self.ramStatic = bytearray(32 * 1024)
			self.targetRegister = 0
			self.PRGbankMode = False
			self.CHRinversion = False
			self.mirrormode = "HORIZONTAL"
			self.register = bytearray(8)
			self.CHRbank = bytearray(8)
			self.PRGbank = bytearray(4)
			self.irqActive = False
			self.irqEnable = False
			self.irqUpdate = False
			self.irqCounter = 0
			self.irqReload = 0
		def reset(self):
			self.targetRegister = 0
			self.PRGbankMode = False
			self.CHRinversion = False
			self.mirrormode = "HORIZONTAL"
			self.irqActive = False
			self.irqEnable = False
			self.irqUpdate = False
			self.irqCounter = 0
			self.irqReload = 0
			self.PRGbank = self.PRGbank = bytearray(4)
			self.CHRbank = self.register = bytearray(8)
			self.PRBbank[0] = 0 * 0x2000
			self.PRBbank[1] = 1 * 0x2000
			self.PRBbank[2] = (self.prgBanks * 2 - 2) * 0x2000
			self.PRBbank[3] = (self.prgBanks * 2 - 1) * 0x2000
		def irqState(self):
			return self.irqActive
		def irqClear(self):
			self.irqActive = False
		def scanline(self):

			self.irqCounter = self.ireReload if self.irqCounter == 0 else self.irqCounter - 1
			if self.irqCounter == 0 and self.ireEnable:
				self.irqActive = True
		def mirror(self):
			return self.mirrormode
		def cpuMapRead(self, addr):
			if addr >= 0x6000 and addr <= 0x7FFF:
				return True, 0xFFFFFFFF, self.ramStatic[addr & 0x1FFF]
			if addr >= 0x8000  and addr <= 0x9FFF:
				return True, self.PRGbank[0] + (addr & 0x1FFF), 0
			if addr >= 0xC000 and addr <= 0xDFFF:
				return True, self.PRGbank[2] + (addr & 0x1FFF), 0
			if addr >= 0xE000 and addr <= 0xFFFF:
				return True, self.PRGbank[3] + (addr & 0x1FFF), 0
			return False, addr, 0
		def cpuMapWrite(self, addr, data):
			if addr >= 0x6000 and addr <= 0x7FFF:
				self.ramStatic[addr & 0x1FFF] = data
				return True, 0xFFFFFFFF
			if addr >= 0x8000  and addr <= 0x9FFF:
				if (addr & 0x0001) == 0:
					self.targetRegister = data & 0x07
					self.PRGbankMode = data & 0x40
					self.CHRinversion = data & 0x80
				else:
					self.register[self.targetRegister] = data
					if self.CHRinversion:
						self.CHRbank[0] = self.register[2] * 0x0400
						self.CHRbank[1] = self.register[3] * 0x0400
						self.CHRbank[2] = self.register[4] * 0x0400
						self.CHRbank[3] = self.register[5] * 0x0400
						self.CHRbank[4] = (self.register[0] & 0xFE) * 0x0400
						self.CHRbank[5] = self.register[0] * 0x0400
						self.CHRbank[6] = (self.register[1] & 0xFE) * 0x0400
						self.CHRbank[7] = self.register[1] * 0x0400 + 0x0400
					else:
						self.CHRbank[0] = (self.register[0] & 0xFE) * 0x0400
						self.CHRbank[1] = self.register[0] * 0x0400
						self.CHRbank[2] = (self.register[1] & 0xFE) * 0x0400
						self.CHRbank[3] = self.register[1] * 0x0400 + 0x0400
						self.CHRbank[4] = self.register[2] * 0x0400
						self.CHRbank[5] = self.register[3] * 0x0400
						self.CHRbank[6] = self.register[4] * 0x0400
						self.CHRbank[7] = self.register[5] * 0x0400
					if self.PRBbankMode:
						self.PRGbankMode[2] = (self.register[6] & 0x3F) * 0x2000
						self.PRGbankMode[0] = (self.prgBanks *2 - 2) * 0x2000
					else:
						self.PRGbankMode[0] = (self.register[6] & 0x3F) * 0x2000
						self.PRGbankMode[2] = (self.prgBanks *2 - 2) * 0x2000
					self.PRGbank[1] = (self.register[7] & 0x3F) * 0x2000
					self.PRGbank[3] = (self.prgBanks * 2 - 1) * 0x2000
				return False, addr
			if addr >= 0xA000 and addr <= 0xBFFF:
				if addr & 0x0001 == 0:
					self.mirrormode = "HORIZONTAL" if data & 0x01 else "VERTICAL"
				return False, addr
			if addr >= 0xC000 and addr <= 0xDFFF:
				if addr & 0x0001 == 0:
					self.irqReload = data
				else:
					self.irqCounter = 0x0000
				return False, addr
			if addr >= 0xE000 and addr <= 0xFFFF:
				self.irqEnable, self.irqActive = False, False if addr & 0x01 == 0 else True, self.irqActive
				return False, addr
			return False, addr
		def ppuMapRead(self, addr):

			if addr >= 0x0000 and addr <= 0x03FF:
				return True, self.CHRBank[0] + (addr & 0x03FF)
			if addr >= 0x0400 and addr <= 0x07FF:
				return True, self.CHRBank[1] + (addr & 0x03FF)
			if addr >= 0x0800 and addr <= 0x0BFF:
				return True, self.CHRBank[2] + (addr & 0x03FF)
			if addr >= 0x0C00 and addr <= 0x0FFF:
				return True, self.CHRBank[3] + (addr & 0x03FF)
			if addr >= 0x1000 and addr <= 0x13FF:
				return True, self.CHRBank[4] + (addr & 0x03FF)
			if addr >= 0x1400 and addr <= 0x17FF:
				return True, self.CHRBank[5] + (addr & 0x03FF)
			if addr >= 0x1800 and addr <= 0x1BFF:
				return True, self.CHRBank[6] + (addr & 0x03FF)
			if addr >= 0x1C00 and addr <= 0x1FFF:
				return True, self.CHRBank[7] + (addr & 0x03FF)
			return False, addr
		def ppuMapWrite(self, addr):
			return False

	class mapper_066:
		def __init__(self, prgBanks, chrBanks):
			self.prgBanks = prgBanks
			self.chrBanks = chrBanks
			self.CHRbankSelect = 0
			self.PRGbankSelect = 0
		def reset(self):
			pass
		def irqState(self):
			pass
		def irqClear(self):
			pass
		def scanline(self):
			pass
		def cpuMapRead(self, addr):
			if addr >= 0x8000  and addr <= 0xFFFF:
				return True, self.PRGbankSelect * 0x8000 + (addr & 0x7FFF), 0
			return False, addr, 0
		def cpuMapWrite(self, addr, data):
			if addr >= 0x8000  and addr <= 0xFFFF:
				self.CHRbankSelect = data & 0x03
				self.PRGbankSelect = (data & 0x30) >> 4
			return False, addr
		def ppuMapRead(self, addr):
			if addr >= 0  and addr <= 0x1FFF:
				return True, self.CHRbankSelect * 0x2000 + addr
			return False, addr
		def ppuMapWrite(self, addr):
			return False
