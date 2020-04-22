from cpu import cpu
from ppu import ppu
from cartridge import cartridge
import pygame
import time

class bus:
	def __init__(self):
		self.cpu = cpu(self)
		self.ppu = ppu()
		pygame.init()

		self.controller = [0, 0]
		self.controller_state = [0, 0]

		self.systemClockCounter = 0

	def cpuWrite(self, addr, data):
		if self.cartridge.cpuWrite(addr, data):
			pass

		elif addr >= 0x0000 and addr <= 0x1FFF:
			#print(addr, data)
			self.cpu.cpuram[addr & 0x07FF] = data

		elif addr >= 0x2000 and addr <= 0x3FFF:
			self.ppu.cpuWrite(addr & 0x0007, data)

		elif addr >= 0x4016 and addr <= 0x4017:
			self.controller_state[addr & 0x0001] = self.controller[addr & 0x0001]

	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00
		self.tempcheck, self.data = self.cartridge.cpuRead(addr)
		if self.tempcheck == True:
			pass
		elif addr >= 0x0000 and addr <= 0x1FFF:
			self.data = self.cpu.cpuram[addr & 0x07FF]

		elif addr >= 0x2000 and addr <= 0x3FFF:
			self.data = self.ppu.cpuRead(addr & 0x0007, readOnly)

		elif addr >= 0x4016 and addr <= 0x4017:
			if self.controller_state[addr & 0x0001] & 0x80 > 0:
				self.data = 1
			else:
				self.data = 0
			self.controller_state[addr & 0x0001] = self.controller_state[addr & 0x0001] << 1

		return self.data

	def insertCartridge(self, filename):
		self.cartridge = cartridge(filename)
		self.ppu.connectCartridge(self.cartridge)

	def reset(self):
		self.cpu.reset()
		self.systemClockCounter = 0

	def clock(self):
		self.ppu.clock()
		self.pressedKey = pygame.key.get_pressed()

		self.controller[0] = 0x00
		if self.pressedKey[pygame.K_x]: #X
			self.controller[0] |= 0x80
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_z]: #Z
			self.controller[0] |= 0x40
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_a]: #A
			self.controller[0] |= 0x20
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_s]: #S
			self.controller[0] |= 0x10
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_UP]: #UP
			self.controller[0] |= 0x08
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_DOWN]: #DOWN
			self.controller[0] |= 0x04
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_RIGHT]: #RIGHT
			self.controller[0] |= 0x02
		else:
			self.controller[0] |= 0x00

		if self.pressedKey[pygame.K_LEFT]: #LEFT
			self.controller[0] |= 0x01
		else:
			self.controller[0] |= 0x00

		if self.systemClockCounter % 3 == 0:
			self.cpu.clock()

		if self.ppu.nmi == True:
			self.ppu.nmi = False
			self.cpu.nmi()

		self.systemClockCounter += 1
