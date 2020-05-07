from cpu import cpu
from ppu import ppu
from cartridge import cartridge
import pygame

class bus:
	def __init__(self):
		self.cpu = cpu(self)
		self.ppu = ppu()
		self.controller_state = [0, 0]
		self.systemClockCounter = 0
		self.dma_page = 0
		self.dma_addr = 0
		self.dma_data = 0
		self.dma_transfer = False
		self.dma_dummy = True
		self.cpucycles = 0
		self.ppucycles = 0
		self.cpuavg = 0
		self.cputotal = 0
		self.ppuavg = 0
		self.pputotal = 0
		self.cpustarttime = 0
		self.ppustarttime = 0

	def cpuWrite(self, addr, data):
		if not self.cartridge.cpuWrite(addr, data):
			if addr >= 0x0000 and addr <= 0x1FFF:
				self.cpu.cpuram[addr & 0x07FF] = data
			elif addr >= 0x2000 and addr <= 0x3FFF:
				self.ppu.cpuWrite(addr & 0x0007, data)
			elif addr == 0x4014:
				self.dma_page = data
				self.dma_addr = self.ppu.oam_addr
				self.dma_addr_start = self.ppu.oam_addr
				self.dma_transfer = True
			elif addr == 0x4016 or addr == 0x4017:
				self.controller_state[0 if addr == 0x4016 else 1] = self.ppu.controller[0 if addr == 0x4016 else 1]

	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00
		self.tempcheck, self.data = self.cartridge.cpuRead(addr)
		if not self.tempcheck:
			if addr >= 0x0000 and addr <= 0x1FFF:
				self.data = self.cpu.cpuram[addr & 0x07FF]
			elif addr >= 0x2000 and addr <= 0x3FFF:
				self.data = self.ppu.cpuRead(addr & 0x0007, readOnly)
			elif addr == 0x4016 or addr == 0x4017:
				self.data = 1 if (self.controller_state[addr & 0x0001] & 0x80) > 0 else 0
				self.controller_state[addr & 0x0001] = self.controller_state[addr & 0x0001] << 1
		return self.data

	def insertCartridge(self, filename):
		self.cartridge = cartridge(filename)
		self.ppu.connectCartridge(self.cartridge)

	def reset(self):
		self.cartridge.reset()
		self.cpu.reset()
		self.ppu.reset()
		self.systemClockCounter = 0
		self.dma_page = 0x00
		self.dma_addr = 0x00
		self.dma_data = 0x00
		self.dma_dummy = True
		self.dma_transfer = False

	def clock(self):
		self.ppu.clock()
		if self.systemClockCounter % 3 == 0:
			if self.dma_transfer:
				if self.dma_dummy:
					if self.systemClockCounter % 2 == 1:
						self.dma_dummy = False
				else:
					if self.systemClockCounter % 2 == 0:
						self.dma_data = self.cpuRead((self.dma_page << 8) | self.dma_addr)
					else:
						self.ppu.oam[self.dma_addr] = self.dma_data
						self.dma_addr = (self.dma_addr + 1) & 0xFF
						if self.dma_addr == self.dma_addr_start:
							self.dma_transfer = False
							self.dma_dummy = True
			else:
				self.cpu.clock()
				self.cpucycles += 1
				if self.ppu.nmi:
					self.ppu.nmi = False
					self.cpu.nmi()
				if self.cartridge.umapper.irqState():
					self.cartridge.umapper.irqClear()
					self.cpu.irq()
		self.systemClockCounter += 1
