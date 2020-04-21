from cartridge import cartridge
import pygame
from random import randint

class ppu:
	def __init__(self):
		self.tblName = [bytearray(1024), bytearray(1024)]
		self.tblPattern = [bytearray(4096), bytearray(4096)]
		self.tblPalette = bytearray(32)

		self.palScreen = [[84, 84, 84], [0, 30, 116], [8, 16, 144], [48, 0, 136], [68, 0, 100], [92, 0, 48], [84, 4, 0], [60, 24, 0], [32, 42, 0], [8, 58, 0], [0, 64, 0], [0, 60, 0], [0, 50, 60], [0, 0, 0], [0, 0, 0], [0, 0, 0],
						  [152, 150, 152], [8, 76, 196], [48, 50, 236], [92, 30, 228], [136, 20, 176], [160, 20, 100], [152, 34, 32], [120, 60, 0], [84, 90, 0], [40, 114, 0], [8, 124, 0], [0, 118, 40], [0, 102, 120], [0, 0, 0], [0, 0, 0], [0, 0, 0],
						  [236, 238, 236], [76, 154, 236], [120, 124, 236], [176, 98, 236], [228, 84, 236], [236, 88, 180], [236, 106, 100], [212, 136, 32], [160, 170, 0], [116, 196, 0], [76, 208, 32], [56, 204, 108], [56, 180, 204], [60, 60, 60], [0, 0, 0], [0, 0, 0],
						  [236, 238, 236], [168, 204, 236], [188, 188, 236], [212, 178, 236], [236, 174, 236], [236, 174, 212], [236, 180, 176], [228, 196, 144], [204, 210, 120], [180, 222, 120], [168, 226, 144], [152, 226, 180], [160, 214, 228], [160, 162, 160], [0, 0, 0], [0, 0, 0]]


		self.framecount = 0
		self.cycle = 0
		self.scanline = 0
		self.framecomplete = False

		self.screen = [[0 for _ in range(256)] for _ in range(240)]
		self.nameTable = [[[0 for _ in range(256)] for _ in range(240)], [[0 for _ in range(256)] for _ in range(240)]]
		self.patternTable = [[[0 for _ in range(128)] for _ in range(128)], [[0 for _ in range(128)] for _ in range(128)]]

		self.selectedPalette = 0x00

		self.statusreg = 0b00000000
		self.maskreg = 0b00000000
		self.controlreg = 0b00000000
		self.vram_addr = 0x0000
		self.tram_addr = 0x0000
		self.finex = 0x00

		self.address_latch = 0x00
		self.ppu_data_buffer = 0x00

		self.bg_next_tile_id = 0x00
		self.bg_next_tile_attrib = 0x00
		self.bg_next_tile_lsb = 0x00
		self.bg_next_tile_msb = 0x00

		self.nmi = False

		pygame.init()
		self.screen = pygame.display.set_mode((256, 240))
		pygame.display.flip()


	def getPatternTable(self, i, palette):
		for self.tileY in range(0, 16):
			for self.tileX in range(0, 16):
				self.offset = (self.tileY * 256) + (self.tileX * 16)
				for self.row in range(0, 8):
					self.tile_lsb = self.ppuRead((i * 0x1000) + self.offset + self.row + 0x0000)
					self.tile_msb = self.ppuRead((i * 0x1000) + self.offset + self.row + 0x0008)
					for self.col in range(0, 8):
						self.pixel = (self.tile_lsb & 0x01) + ((self.tile_msb & 0x01) << 1)
						#print(self.pixel, "PIXEL", self.getColorFromPaletteRam(palette, self.pixel))
						self.tile_lsb = self.tile_lsb >> 1
						self.tile_msb = self.tile_msb >> 1
						self.patternTable[i][(self.tileX * 8) + (7 - self.col)][(self.tileY * 8) + self.row] = self.getColorFromPaletteRam(palette, self.pixel)
		return self.patternTable[i]

	def getColorFromPaletteRam(self, palette, pixel):
		#self.ppuRead(0x3F00 + (palette << 2) + pixel)
		#print("read", self.ppuRead(0x3F00 + (palette << 2) + pixel))
		return self.palScreen[self.ppuRead(0x3F00 + (palette << 2) + pixel)]

	#Communication with main bus
	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00

		if addr == 0x0000: #Controll
			pass
		elif addr == 0x0001: #Mask
			pass
		elif addr == 0x0002: #Status
			self.statusreg = self.statusreg | 0b10000000
			self.data = (self.statusreg & 0xE0) | (self.ppu_data_buffer & 0x1F)
			self.statusreg = self.statusreg & (~0b10000000)
			self.address_latch = 0
		elif addr == 0x0003: #OAM address
			pass
		elif addr == 0x0004: #OAM data
			pass
		elif addr == 0x0005: #Scroll
			pass
		elif addr == 0x0006: #PPU address
			pass
		elif addr == 0x0007: #PPU data
			self.data = self.ppu_data_buffer
			self.ppu_data_buffer = self.ppuRead(self.vram_addr)
			#print(self.ppu_address, self.ppu_data_buffer)

			if self.vram_addr > 0x3F00:
				self.data = self.ppu_data_buffer
			if self.controlreg & 0b00000100 == 0b00000100:
				self.vram_addr += 32
			else:
				self.vram_addr += 1
		return self.data

	def cpuWrite(self, addr, data):
		if addr == 0x0000: #Controll
			self.controlreg = data
			self.tram_addr = self.tram_addr | ((self.controlreg & 0b00000001) << 10)
			self.tram_addr = self.tram_addr | ((self.controlreg & 0b00000001) << 11)
		elif addr == 0x0001: #Mask
			self.maskreg = data
		elif addr == 0x0002: #Status
			pass
		elif addr == 0x0003: #OAM address
			pass
		elif addr == 0x0004: #OAM data
			pass
		elif addr == 0x0005: #Scroll
			if self.address_latch == 0:
				self.finex = data & 0x07
				self.tram_addr = self.tram_addr | (data >> 3) #maybe push to left by 4?
				self.address_latch = 1
			else:
				self.tram_addr = self.tram_addr | ((data & 0x07) << 12) #hard math maybe not 12
				self.tram_addr = self.tram_addr | ((data >> 3) << 5)
				self.address_latch = 0
		elif addr == 0x0006: #PPU address
			if self.address_latch == 0:
				self.tram_addr = (self.tram_addr & 0x00FF) | (data << 8)
				self.vram_addr = self.tram_addr
				self.address_latch = 1
			else:
				self.tram_addr = (self.tram_addr & 0xFF00) | data
				self.address_latch = 0
		elif addr == 0x0007: #PPU data
			self.ppuWrite(self.vram_addr, data)

			if self.controlreg & 0b00000100 == 0b00000100:
				self.vram_addr += 32
			else:
				self.vram_addr += 1

	#Communication with ppu bus
	def ppuRead(self, addr, readOnly = False):
		self.data = 0x00
		self.addr = addr & 0x3FFF

		self.tempcheck, self.tempdata = self.cartridge.ppuRead(addr, readOnly)
		if self.tempcheck == True:
			self.data = self.tempdata
		elif self.addr >= 0x0000 and self.addr <= 0x1FFF:
			self.data = self.tblPattern[(self.addr & 0x1000) >> 12][self.addr & 0x0FFF]

		elif self.addr >= 0x2000 and self.addr <= 0x3EFF:
			self.addr = self.addr & 0x0FFF
			if self.cartridge.mirror == "VERTICAL":
				if self.addr >= 0x0000 and self.addr <= 0x03FF:
					self.data = self.tblName[0][self.addr & 0x03FF]
				elif self.addr >= 0x0400 and self.addr <= 0x07FF:
					self.data = self.tblName[1][self.addr & 0x03FF]
				elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
					self.data = self.tblName[0][self.addr & 0x03FF]
				elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
					self.data = self.tblName[1][self.addr & 0x03FF]

			elif self.cartridge.mirror == "HORIZONTAL":
				if self.addr >= 0x0000 and self.addr <= 0x03FF:
					self.data = self.tblName[0][self.addr & 0x03FF]
				elif self.addr >= 0x0400 and self.addr <= 0x07FF:
					self.data = self.tblName[0][self.addr & 0x03FF]
				elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
					self.data = self.tblName[1][self.addr & 0x03FF]
				elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
					self.data = self.tblName[1][self.addr & 0x03FF]

		elif self.addr >= 0x3F00 and self.addr <= 0x3FFF:
			#print("PPUREADPALETTE")
			self.addr = self.addr & 0x001F
			if self.addr == 0x0010:
				self.addr = 0x0000
			if self.addr == 0x0014:
				self.addr = 0x0004
			if self.addr == 0x0018:
				self.addr = 0x0008
			if self.addr == 0x001C:
				self.addr = 0x000C
			self.data = self.tblPalette[self.addr]
		return self.data

	def ppuWrite(self, addr, data):
		self.addr = addr & 0x3FFF

		if self.cartridge.ppuWrite(self.addr, data):
			pass

		elif self.addr >= 0x0000 and self.addr <= 0x1FFF:
			self.tblPattern[(self.addr & 0x1000) >> 12][self.addr & 0x0FFF] = data

		elif self.addr >= 0x2000 and self.addr <= 0x3EFF:
			self.addr = self.addr & 0x0FFF
			if self.cartridge.mirror == "VERTICAL":
				if self.addr >= 0x0000 and self.addr <= 0x03FF:
					self.tblName[0][self.addr & 0x03FF] = data
				elif self.addr >= 0x0400 and self.addr <= 0x07FF:
					self.tblName[1][self.addr & 0x03FF] = data
				elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
					self.tblName[0][self.addr & 0x03FF] = data
				elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
					self.tblName[1][self.addr & 0x03FF] = data

			elif self.cartridge.mirror == "HORIZONTAL":
				if self.addr >= 0x0000 and self.addr <= 0x03FF:
					self.tblName[0][self.addr & 0x03FF] = data
				elif self.addr >= 0x0400 and self.addr <= 0x07FF:
					self.tblName[0][self.addr & 0x03FF] = data
				elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
					self.tblName[1][self.addr & 0x03FF] = data
				elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
					self.tblName[1][self.addr & 0x03FF] = data

		elif self.addr >= 0x3F00 and self.addr <= 0x3FFF:
			#print("PPUWRITEPALETTE")
			self.addr = self.addr & 0x001F

			if self.addr == 0x0010:
				self.addr = 0x0000
			if self.addr == 0x0014:
				self.addr = 0x0004
			if self.addr == 0x0018:
				self.addr = 0x0008
			if self.addr == 0x001C:
				self.addr = 0x000C

			self.tblPalette[self.addr] = data

	def connectCartridge(self, cartridge):
		self.cartridge = cartridge

	def clock(self):
		if self.scanline >= -1 and self.scanline < 240:
			if self.scanline == -1 and self.cycle == 1:
				self.statusreg = self.statusreg & ~0b10000000

			if (self.cycle >= 2 and self.cycle < 258) or (self.cycle >= 321 and self.cycle < 338):
				self.switchcase = (self.cycle - 1) % 8
				if self.switchcase == 0:
					self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))
				elif self.switchcase == 2:
					self.bg_next_tile_attrib = self.ppuRead(0x23C0 | (self.vram_addr & 0b100000000000) | (self.vram_addr & 0b10000000000) | (((self.vram_addr & 0b1111100000) >> 7) << 3) | (((self.vram_addr & 0b11111) >> 2)))
					if (((self.vram_addr & 0b1111100000) >> 5) & 0x02) != 0x00:
						self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 4
					if (self.vram_addr & 0b11111) & 0x02 != 0:
						self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 2
					self.bg_next_tile_attrib = self.bg_next_tile_attrib & 0x03
				elif self.switchcase == 4:
					self.bg_next_tile_lsb = self.ppuRead(((self.controlreg & 0b10000) << 8) + (self.bg_next_tile_id << 4) +  ((self.vram_addr & 0b111000000000000) >> 12) + 0)
				elif self.switchcase == 6:
					self.bg_next_tile_msb = self.ppuRead(((self.controlreg & 0b10000) << 8) + (self.bg_next_tile_id << 4) +  ((self.vram_addr & 0b111000000000000) >> 12) + 0)
				elif self.switchcase == 7:
					pass
					#self.incrementScrollX()
			if self.cycle == 256:
				pass
				#self.incrementScrollY()

			if self.cycle == 257:
				pass
				#self.transferAddressX()

			if self.scanline == -1 and self.cycle >= 280 and self.cycle < 305:
				pass
				#self.transferAddressY()

		if self.scanline == 240:
			pass
		#print(self.scanline, self.cycle)
		if self.scanline == 241 and self.cycle == 1:
			self.statusreg = self.statusreg | 0b10000000
			if (self.controlreg & 0b10000000) != 0:
				self.nmi = True

		#if self.cycle < 128 and self.scanline < 128:
		#	self.screen.set_at((self.cycle, self.scanline), self.patternTable[0][self.scanline][self.cycle])

		self.cycle += 1
		if self.cycle >= 341:
			self.cycle = 0
			self.scanline += 1
			if self.scanline >= 261:
				self.scanline = -1
				self.framecomplete = True

				self.patternTable[0] = self.getPatternTable(0, self.selectedPalette)
				self.framecount += 1
				print(self.framecount)

				for self.tempy in range(128):
					for self.tempx in range(128):
						self.screen.set_at((self.tempy, self.tempx), self.patternTable[0][self.tempy][self.tempx])
				pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
