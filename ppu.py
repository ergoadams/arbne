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

		self.statusreg_unused = 0b00000
		self.statusreg_sprite_overflow = 0b0
		self.statusreg_sprite_zero_hit = 0b0
		self.statusreg_vertical_blank = 0b0
		self.statusreg = 0b00000000

		self.maskreg_grayscale = 0b0
		self.maskreg_render_background_left = 0b0
		self.maskreg_render_sprites_left = 0b0
		self.maskreg_render_background = 0b0
		self.maskreg_render_sprites = 0b0
		self.maskreg_enhance_red = 0b0
		self.maskreg_enhance_green = 0b0
		self.maskreg_enhance_blue = 0b0
		self.maskreg = 0b00000000

		self.controlreg_nametable_x = 0b0
		self.controlreg_nametable_y = 0b0
		self.controlreg_increment_mode = 0b0
		self.controlreg_pattern_sprite = 0b0
		self.controlreg_pattern_background = 0b0
		self.controlreg_sprite_size = 0b0
		self.controlreg_slave_mode = 0b0
		self.controlreg_enable_nmi = 0b0
		self.controlreg = 0b00000000

		self.vram_addr_coarse_x = 0b00000
		self.vram_addr_coarse_y = 0b00000
		self.vram_addr_nametable_x = 0b0
		self.vram_addr_nametable_y = 0b0
		self.vram_addr_fine_y = 0b000
		self.vram_addr_unused = 0b0
		self.vram_addr = 0b0000000000000000

		self.tram_addr_coarse_x = 0b00000
		self.tram_addr_coarse_y = 0b00000
		self.tram_addr_nametable_x = 0b0
		self.tram_addr_nametable_y = 0b0
		self.tram_addr_fine_y = 0b000
		self.tram_addr_unused = 0b0
		self.tram_addr = 0b0000000000000000

		self.fine_x = 0x00

		self.address_latch = 0x00
		self.ppu_data_buffer = 0x00

		self.bg_next_tile_id = 0x00
		self.bg_next_tile_attrib = 0x00
		self.bg_next_tile_lsb = 0x00
		self.bg_next_tile_msb = 0x00
		self.bg_shifter_pattern_lo = 0x0000
		self.bg_shifter_pattern_hi = 0x0000
		self.bg_shifter_attrib_lo = 0x0000
		self.bg_shifter_attrib_hi = 0x0000

		self.nmi = False

		self.oam = [0x00 for _ in range(256)] # 64 *4 bytes
		self.oam_addr = 0x00

		self.spriteScanline = [0x00 for _ in range(32)]
		self.sprite_count = 0

		self.sprite_shifter_pattern_lo = [0x00 for _ in range(8)]
		self.sprite_shifter_pattern_hi = [0x00 for _ in range(8)]

		self.spriteZeroHitPossible = False
		self.spriteZeroBeingRendered = False

		pygame.init()
		self.scaling_factor = 3
		self.screen_width, self.screen_height = 256, 240
		self.window = pygame.display.set_mode((self.screen_width*self.scaling_factor + 128, self.screen_height*self.scaling_factor))
		self.screen = pygame.Surface((self.screen_width, self.screen_height))
		pygame.display.flip()


	def getPatternTable(self, i, palette):
		for self.tileY in range(16):
			for self.tileX in range(16):
				self.offset = (self.tileY * 256) + (self.tileX * 16)
				for self.row in range(8):
					self.tile_lsb = self.ppuRead((i * 0x1000) + self.offset + self.row + 0x0000)
					self.tile_msb = self.ppuRead((i * 0x1000) + self.offset + self.row + 0x0008)
					for self.col in range(8):
						self.pixel = ((self.tile_lsb & 0x01) << 1) | ((self.tile_msb & 0x01))
						#print(self.pixel, "PIXEL", self.getColorFromPaletteRam(palette, self.pixel))
						self.tile_lsb = self.tile_lsb >> 1
						self.tile_msb = self.tile_msb >> 1
						self.patternTable[i][(self.tileX * 8) + (7 - self.col)][(self.tileY * 8) + self.row] = self.getColorFromPaletteRam(palette, self.pixel)
		return self.patternTable[i]

	def getColorFromPaletteRam(self, palette, pixel):
		return self.palScreen[self.ppuRead(0x3F00 + (palette << 2) + pixel) & 0x3F]

	#Communication with main bus
	def cpuRead(self, addr, readOnly = False):
		self.data = 0x00

		if addr == 0x0000: #Controll
			pass
		elif addr == 0x0001: #Mask
			pass
		elif addr == 0x0002: #Status
			self.statusreg = 0b00000000 | self.statusreg_unused
			self.statusreg |= (self.statusreg_sprite_overflow << 5)
			self.statusreg |= (self.statusreg_sprite_zero_hit << 6)
			self.statusreg |= (self.statusreg_vertical_blank << 7)

			self.data = (self.statusreg & 0xE0) | (self.ppu_data_buffer & 0x1F)
			self.statusreg_vertical_blank = 0
			self.address_latch = 0
		elif addr == 0x0003: #OAM address
			pass
		elif addr == 0x0004: #OAM data
			self.data = self.oam[self.oam_addr]
		elif addr == 0x0005: #Scroll
			pass
		elif addr == 0x0006: #PPU address
			pass
		elif addr == 0x0007: #PPU data
			self.data = self.ppu_data_buffer

			self.vram_addr = 0b0000000000000000 | self.vram_addr_coarse_x
			self.vram_addr |= (self.vram_addr_coarse_y << 5)
			self.vram_addr |= (self.vram_addr_nametable_x << 10)
			self.vram_addr |= (self.vram_addr_nametable_y << 11)
			self.vram_addr |= (self.vram_addr_fine_y << 12)
			self.vram_addr |= (self.vram_addr_unused << 15)

			self.ppu_data_buffer = self.ppuRead(self.vram_addr)

			if self.vram_addr >= 0x3F00:
				self.data = self.ppu_data_buffer

			if self.controlreg_increment_mode != 0:
				self.vram_addr += 32
			else:
				self.vram_addr += 1

			self.tempreg = str("{:016b}".format(self.vram_addr))
			self.vram_addr_coarse_x = int(self.tempreg[11::], 2)
			self.vram_addr_coarse_y = int(self.tempreg[6:11], 2)
			self.vram_addr_nametable_x = int(self.tempreg[5], 2)
			self.vram_addr_nametable_y = int(self.tempreg[4], 2)
			self.vram_addr_fine_y = int(self.tempreg[1:4], 2)
			self.vram_addr_unused = int(self.tempreg[0], 2)
		return self.data

	def cpuWrite(self, addr, data):
		if addr == 0x0000: #Controll
			self.controlreg = data

			self.tempreg = str("{:08b}".format(self.controlreg))
			self.controlreg_nametable_x = int(self.tempreg[7], 2)
			self.controlreg_nametable_y = int(self.tempreg[6], 2)
			self.controlreg_increment_mode = int(self.tempreg[5], 2)
			self.controlreg_pattern_sprite = int(self.tempreg[4], 2)
			self.controlreg_pattern_background = int(self.tempreg[3], 2)
			self.controlreg_sprite_size = int(self.tempreg[2], 2)
			self.controlreg_slave_mode = int(self.tempreg[1], 2)
			self.controlreg_enable_nmi = int(self.tempreg[0], 2)

			self.tram_addr_nametable_x = self.controlreg_nametable_x
			self.tram_addr_nametable_y = self.controlreg_nametable_y
		elif addr == 0x0001: #Mask
			self.maskreg = data

			self.tempreg = str("{:08b}".format(self.maskreg))
			self.maskreg_grayscale = int(self.tempreg[7], 2)
			self.maskreg_render_background_left = int(self.tempreg[6], 2)
			self.maskreg_render_sprites_left = int(self.tempreg[5], 2)
			self.maskreg_render_background = int(self.tempreg[4], 2)
			self.maskreg_render_sprites = int(self.tempreg[3], 2)
			self.maskreg_enhance_red = int(self.tempreg[2], 2)
			self.maskreg_enhance_green = int(self.tempreg[1], 2)
			self.maskreg_enhance_blue = int(self.tempreg[0], 2)
		elif addr == 0x0002: #Status
			pass
		elif addr == 0x0003: #OAM address
			self.oam_addr = data
			#print("2003 WRITE", self.oam_addr)
		elif addr == 0x0004: #OAM data
			self.oam[self.oam_addr] = data
			self.oam_addr = (self.oam_addr + 1) & 0xFF
			#print("2004 WRITE", self.oam_addr)
		elif addr == 0x0005: #Scroll
			if self.address_latch == 0:
				self.finex = data & 0x07
				self.tram_addr_coarse_x = data >> 3
				self.address_latch = 1
			else:
				self.tram_addr_fine_y = data & 0x07
				self.tram_addr_coarse_y = data >> 3
				self.address_latch = 0
		elif addr == 0x0006: #PPU address
			if self.address_latch == 0:
				self.tram_addr = 0b0000000000000000 | self.tram_addr_coarse_x
				self.tram_addr |= (self.tram_addr_coarse_y << 5)
				self.tram_addr |= (self.tram_addr_nametable_x << 10)
				self.tram_addr |= (self.tram_addr_nametable_y << 11)
				self.tram_addr |= (self.tram_addr_fine_y << 12)
				self.tram_addr |= (self.tram_addr_unused << 15)

				self.tram_addr = ((data & 0x3F) << 8) | (self.tram_addr & 0x00FF)

				self.tempreg = str("{:016b}".format(self.tram_addr))
				self.tram_addr_coarse_x = int(self.tempreg[11::], 2)
				self.tram_addr_coarse_y = int(self.tempreg[6:11], 2)
				self.tram_addr_nametable_x = int(self.tempreg[5], 2)
				self.tram_addr_nametable_y = int(self.tempreg[4], 2)
				self.tram_addr_fine_y = int(self.tempreg[1:4], 2)
				self.tram_addr_unused = int(self.tempreg[0], 2)
				self.address_latch = 1

			else:
				self.tram_addr = 0b0000000000000000 | self.tram_addr_coarse_x
				self.tram_addr |= (self.tram_addr_coarse_y << 5)
				self.tram_addr |= (self.tram_addr_nametable_x << 10)
				self.tram_addr |= (self.tram_addr_nametable_y << 11)
				self.tram_addr |= (self.tram_addr_fine_y << 12)
				self.tram_addr |= (self.tram_addr_unused << 15)

				self.tram_addr = (self.tram_addr & 0xFF00) | data

				self.tempreg = str("{:016b}".format(self.tram_addr))
				self.tram_addr_coarse_x = int(self.tempreg[11::], 2)
				self.tram_addr_coarse_y = int(self.tempreg[6:11], 2)
				self.tram_addr_nametable_x = int(self.tempreg[5], 2)
				self.tram_addr_nametable_y = int(self.tempreg[4], 2)
				self.tram_addr_fine_y = int(self.tempreg[1:4], 2)
				self.tram_addr_unused = int(self.tempreg[0], 2)

				self.vram_addr = self.tram_addr

				self.tempreg = str("{:016b}".format(self.vram_addr))
				self.vram_addr_coarse_x = int(self.tempreg[11::], 2)
				self.vram_addr_coarse_y = int(self.tempreg[6:11], 2)
				self.vram_addr_nametable_x = int(self.tempreg[5], 2)
				self.vram_addr_nametable_y = int(self.tempreg[4], 2)
				self.vram_addr_fine_y = int(self.tempreg[1:4], 2)
				self.vram_addr_unused = int(self.tempreg[0], 2)

				self.address_latch = 0
		elif addr == 0x0007: #PPU data
			self.vram_addr = 0b0000000000000000 | self.vram_addr_coarse_x
			self.vram_addr |= (self.vram_addr_coarse_y << 5)
			self.vram_addr |= (self.vram_addr_nametable_x << 10)
			self.vram_addr |= (self.vram_addr_nametable_y << 11)
			self.vram_addr |= (self.vram_addr_fine_y << 12)
			self.vram_addr |= (self.vram_addr_unused << 15)

			self.ppuWrite(self.vram_addr, data)

			if self.controlreg_increment_mode != 0:
				self.vram_addr += 32
			else:
				self.vram_addr += 1

			self.tempreg = str("{:016b}".format(self.vram_addr))
			self.vram_addr_coarse_x = int(self.tempreg[11::], 2)
			self.vram_addr_coarse_y = int(self.tempreg[6:11], 2)
			self.vram_addr_nametable_x = int(self.tempreg[5], 2)
			self.vram_addr_nametable_y = int(self.tempreg[4], 2)
			self.vram_addr_fine_y = int(self.tempreg[1:4], 2)
			self.vram_addr_unused = int(self.tempreg[0], 2)

	#Communication with ppu bus
	def ppuRead(self, addr, readOnly = False):
		self.data = 0x00
		self.addr = addr & 0x3FFF

		self.tempcheck, self.tempdata = self.cartridge.ppuRead(self.addr, readOnly)
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
			self.addr = self.addr & 0x001F
			if self.addr == 0x0010:
				self.addr = 0x0000
			if self.addr == 0x0014:
				self.addr = 0x0004
			if self.addr == 0x0018:
				self.addr = 0x0008
			if self.addr == 0x001C:
				self.addr = 0x000C
			if self.maskreg_grayscale != 0:
				self.data = self.tblPalette[self.addr] & 0x30
			else:
				self.data = self.tblPalette[self.addr] & 0x3F
		return self.data

	def ppuWrite(self, addr, data):
		self.addr = addr & 0x3FFF

		self.tempcheck = self.cartridge.ppuWrite(self.addr, data)

		if self.tempcheck == True:
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

	def reset(self):
		self.fine_x = 0x00
		self.address_latch = 0x00
		self.ppu_data_buffer = 0x00
		self.scanline = 0x00
		self.cycle = 0x00
		self.bg_next_tile_id = 0x00
		self.bg_next_tile_attrib = 0x00
		self.bg_next_tile_lsb = 0x00
		self.bg_next_tile_msb = 0x00
		self.bg_shifter_pattern_lo = 0x00
		self.bg_shifter_pattern_hi = 0x00
		self.bg_shifter_attrib_lo = 0x00
		self.bg_shifter_attrib_hi = 0x00
		self.statusreg = 0x00
		self.statusreg_unused = 0b00000
		self.statusreg_sprite_overflow = 0b0
		self.statusreg_sprite_zero_hit = 0b0
		self.statusreg_vertical_blank = 0b0

		self.maskreg = 0x00
		self.maskreg_grayscale = 0b0
		self.maskreg_render_background_left = 0b0
		self.maskreg_render_sprites_left = 0b0
		self.maskreg_render_background = 0b0
		self.maskreg_render_sprites = 0b0
		self.maskreg_enhance_red = 0b0
		self.maskreg_enhance_green = 0b0
		self.maskreg_enhance_blue = 0b0

		self.controlreg = 0x00
		self.controlreg_nametable_x = 0b0
		self.controlreg_nametable_y = 0b0
		self.controlreg_increment_mode = 0b0
		self.controlreg_pattern_sprite = 0b0
		self.controlreg_pattern_background = 0b0
		self.controlreg_sprite_size = 0b0
		self.controlreg_slave_mode = 0b0
		self.controlreg_enable_nmi = 0b0

		self.vram_addr = 0x00
		self.vram_addr_coarse_x = 0b00000
		self.vram_addr_coarse_y = 0b00000
		self.vram_addr_nametable_x = 0b0
		self.vram_addr_nametable_y = 0b0
		self.vram_addr_fine_y = 0b000
		self.vram_addr_unused = 0b0

		self.tram_addr = 0x00
		self.tram_addr_coarse_x = 0b00000
		self.tram_addr_coarse_y = 0b00000
		self.tram_addr_nametable_x = 0b0
		self.tram_addr_nametable_y = 0b0
		self.tram_addr_fine_y = 0b000
		self.tram_addr_unused = 0b0

	def incrementScrollX(self):
		if (self.maskreg_render_background != 0) or (self.maskreg_render_sprites != 0):
			if self.vram_addr_coarse_x == 31:
				self.vram_addr_coarse_x = 0
				self.vram_addr_nametable_x = ~self.vram_addr_nametable_x
			else:
				self.vram_addr_coarse_x += 1

	def incrementScrollY(self):
		if (self.maskreg_render_background != 0) or (self.maskreg_render_sprites != 0):
			if self.vram_addr_fine_y < 7:
				self.vram_addr_fine_y += 1
			else:
				self.vram_addr_fine_y = 0
				if self.vram_addr_coarse_y == 29:
					self.vram_addr_coarse_y = 0
					self.vram_addr_nametable_y = ~self.vram_addr_nametable_y
				elif self.vram_addr_coarse_y == 31:
					self.vram_addr_coarse_y = 0
				else:
					self.vram_addr_coarse_y += 1

	def transferAddressX(self):
		if (self.maskreg_render_background != 0) or (self.maskreg_render_sprites != 0):
			self.vram_addr_nametable_x = self.tram_addr_nametable_x
			self.vram_addr_coarse_x = self.tram_addr_coarse_x

	def transferAddressY(self):
		if (self.maskreg_render_background != 0) or (self.maskreg_render_sprites != 0):
			self.vram_addr_fine_y = self.tram_addr_fine_y
			self.vram_addr_nametable_y = self.tram_addr_nametable_y
			self.vram_addr_coarse_y = self.tram_addr_coarse_y

	def loadBackgroundShifters(self):
		self.bg_shifter_pattern_lo = (self.bg_shifter_pattern_lo & 0xFF00) | self.bg_next_tile_lsb
		self.bg_shifter_pattern_hi = (self.bg_shifter_pattern_hi & 0xFF00) | self.bg_next_tile_msb

		if self.bg_next_tile_attrib & 0b01 != 0:
			self.bg_shifter_attrib_lo = (self.bg_shifter_attrib_lo & 0xFF00) | 0xFF
		else:
			self.bg_shifter_attrib_lo = (self.bg_shifter_attrib_lo & 0xFF00) | 0x00

		if self.bg_next_tile_attrib & 0b10 != 0:
			self.bg_shifter_attrib_hi = (self.bg_shifter_attrib_hi & 0xFF00) | 0xFF
		else:
			self.bg_shifter_attrib_hi = (self.bg_shifter_attrib_hi & 0xFF00) | 0x00

	def updateShifters(self):
		if self.maskreg_render_background != 0:
			self.bg_shifter_pattern_lo = self.bg_shifter_pattern_lo << 1
			self.bg_shifter_pattern_hi = self.bg_shifter_pattern_hi << 1
			self.bg_shifter_attrib_lo = self.bg_shifter_attrib_lo << 1
			self.bg_shifter_attrib_hi = self.bg_shifter_attrib_hi << 1

		if (self.maskreg_render_sprites != 0) and (self.cycle >= 1) and (self.cycle < 258):
			for i in range(self.sprite_count):
				if self.spriteScanline[(i * 4) + 3] > 0:
					self.spriteScanline[(i * 4) + 3] += -1
				else:
					self.sprite_shifter_pattern_lo[i] = self.sprite_shifter_pattern_lo[i] << 1
					self.sprite_shifter_pattern_hi[i] = self.sprite_shifter_pattern_hi[i] << 1

	def flipByte(self, b):
		self.b = ((b & 0xF0) >> 4) | ((b & 0x0F) << 4)
		self.b = ((self.b & 0xCC) >> 2) | ((self.b & 0x33) << 2)
		self.b = ((self.b & 0xAA) >> 1) | ((self.b & 0x55) << 1)
		return self.b

	def clock(self):
		if (self.scanline >= -1) and (self.scanline < 240):
			if self.scanline == 0 and self.cycle == 0 and (self.maskreg_render_background != 0 or self.maskreg_render_sprites != 0):
				self.cycle = 1

			if self.scanline == -1 and self.cycle == 1:
				self.statusreg_vertical_blank = 0
				self.statusreg_sprite_zero_hit = 0
				self.statusreg_sprite_overflow = 0

				for i in range(8):
					self.sprite_shifter_pattern_lo[i] = 0
					self.sprite_shifter_pattern_hi[i] = 0

			if (self.cycle >= 2 and self.cycle < 258) or (self.cycle >= 321 and self.cycle < 338):
				self.updateShifters()
				self.switchcase = (self.cycle - 1) % 8
				if self.switchcase == 0:
					self.loadBackgroundShifters()
					self.vram_addr = 0b0000000000000000 | self.vram_addr_coarse_x
					self.vram_addr |= (self.vram_addr_coarse_y << 5)
					self.vram_addr |= (self.vram_addr_nametable_x << 10)
					self.vram_addr |= (self.vram_addr_nametable_y << 11)
					self.vram_addr |= (self.vram_addr_fine_y << 12)
					self.vram_addr |= (self.vram_addr_unused << 15)

					self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))

				elif self.switchcase == 2:
					self.bg_next_tile_attrib = self.ppuRead(0x23C0 | (self.vram_addr_nametable_y << 11) | (self.vram_addr_nametable_x << 10) | ((self.vram_addr_coarse_y >> 2) << 3) | (self.vram_addr_coarse_x >> 2))
					if (self.vram_addr_coarse_y & 0x02) != 0:
						self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 4
					if (self.vram_addr_coarse_x & 0x02) != 0:
						self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 2
					self.bg_next_tile_attrib &= 0x03

				elif self.switchcase == 4:
					self.bg_next_tile_lsb = self.ppuRead((self.controlreg_pattern_background << 12) + (self.bg_next_tile_id << 4) + self.vram_addr_fine_y + 0)

				elif self.switchcase == 6:
					self.bg_next_tile_msb = self.ppuRead((self.controlreg_pattern_background << 12) + (self.bg_next_tile_id << 4) + self.vram_addr_fine_y + 8)

				elif self.switchcase == 7:
					self.incrementScrollX()

			if self.cycle == 256:
				self.incrementScrollY()

			if self.cycle == 257:
				self.loadBackgroundShifters()
				self.transferAddressX()

			if (self.cycle == 338) or (self.cycle == 340):
				self.vram_addr = 0b0000000000000000 | self.vram_addr_coarse_x
				self.vram_addr |= (self.vram_addr_coarse_y << 5)
				self.vram_addr |= (self.vram_addr_nametable_x << 10)
				self.vram_addr |= (self.vram_addr_nametable_y << 11)
				self.vram_addr |= (self.vram_addr_fine_y << 12)
				self.vram_addr |= (self.vram_addr_unused << 15)

				self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))

			if self.scanline == -1 and self.cycle >= 280 and self.cycle < 305:
				self.transferAddressY()

			# FOREGROUND RENDERING ------------------------------------------------------------------------------------------------------

			if self.cycle == 257 and self.scanline >= 0:
				self.spriteScanline = [0xFF for _ in range(32)]
				self.sprite_count = 0

				for i in range(8):
					self.sprite_shifter_pattern_lo[i] = 0
					self.sprite_shifter_pattern_hi[i] = 0

				self.oamEntry = 0
				self.spriteZeroHitPossible = False

				while self.oamEntry < 64 and self.sprite_count < 9: # <=
					self.diff = self.scanline - self.oam[self.oamEntry * 4]
					if self.controlreg_sprite_size != 0:
						self.tempdiff = 16
					else:
						self.tempdiff = 8

					if (self.diff >= 0) and (self.diff < self.tempdiff) and self.sprite_count < 8:
						if self.sprite_count < 8:
							if self.oamEntry == 0:
								self.spriteZeroHitPossible = True
							self.spriteScanline[self.sprite_count * 4] = self.oam[self.oamEntry * 4]
							self.spriteScanline[(self.sprite_count * 4) + 1] = self.oam[(self.oamEntry * 4) + 1]
							self.spriteScanline[(self.sprite_count * 4) + 2] = self.oam[(self.oamEntry * 4) + 2]
							self.spriteScanline[(self.sprite_count * 4) + 3] = self.oam[(self.oamEntry * 4) + 3]
						self.sprite_count += 1
					self.oamEntry += 1

				if self.sprite_count >= 8:
					self.statusreg_sprite_overflow = 1
				else:
					self.statusreg_sprite_overflow = 0

			if self.cycle == 340:
				for i in range(self.sprite_count):
					self.sprite_pattern_bits_lo, self.sprite_pattern_bits_hi = 0x00, 0x00
					self.sprite_pattern_addr_lo, self.sprite_pattern_addr_hi = 0x0000, 0x0000

					if self.controlreg_sprite_size == 0:
						#8x8 Sprite Mode
						if (self.spriteScanline[(i * 4) + 2]  & 0x80) == 0x00:
							#Sprite is not flipped vertically
							self.sprite_pattern_addr_lo = (self.controlreg_pattern_sprite << 12) | (self.spriteScanline[(i * 4) + 1] << 4) | (self.scanline - self.spriteScanline[i * 4])

						else:
							#Sprite is flipped vertically
							self.sprite_pattern_addr_lo = (self.controlreg_pattern_sprite << 12) | (self.spriteScanline[(i * 4) + 1] << 4) | (7 - (self.scanline - self.spriteScanline[i * 4]))
					else:
						#8x16 Sprite Mode
						if (self.spriteScanline[(i * 4) + 2] & 0x80) == 0x00:
							#Sprite is not flipped vertically
							if (self.scanline - self.spriteScanline[i * 4]) < 8:
								#Reading top half of tile
								self.pattern_addr_lo = ((self.spriteScanline[(i * 4) + 1] & 0x01) << 12) | ((self.spriteScanline[(i * 4) + 1] & 0xFE) << 4) | ((self.scanline - (self.spriteScanline[i * 4]) & 0x07))
							else:
								#Reading bottom half of tile
								self.pattern_addr_lo = ((self.spriteScanline[(i * 4) + 1] & 0x01) << 12) | (((self.spriteScanline[(i * 4) + 1] & 0xFE) + 1) << 4) | ((self.scanline - (self.spriteScanline[i * 4]) & 0x07))
						else:
							#Sprite is flipped vertically
							if (self.scanline - self.spriteScanline[i * 4]) < 8:
								#Reading top half of tile
								self.pattern_addr_lo = ((self.spriteScanline[(i * 4) + 1] & 0x01) << 12) | (((self.spriteScanline[(i * 4) + 1] & 0xFE) + 1) << 4) | (7 - (self.scanline - (self.spriteScanline[i * 4] & 0x07)))
							else:
								#Reading bottom half of tile
								self.pattern_addr_lo = ((self.spriteScanline[(i * 4) + 1] & 0x01) << 12) | ((self.spriteScanline[(i * 4) + 1] & 0xFE) << 4) | (7 - (self.scanline - (self.spriteScanline[i * 4] & 0x07)))

					self.sprite_pattern_addr_hi = self.sprite_pattern_addr_lo + 8
					self.sprite_pattern_bits_lo = self.ppuRead(self.sprite_pattern_addr_lo)
					self.sprite_pattern_bits_hi = self.ppuRead(self.sprite_pattern_addr_hi)

					if (self.spriteScanline[(i * 4) + 2] & 0x40) != 0x00:

						self.sprite_pattern_bits_lo = self.flipByte(self.sprite_pattern_bits_lo)
						self.sprite_pattern_bits_hi = self.flipByte(self.sprite_pattern_bits_hi)

					self.sprite_shifter_pattern_lo[i] = self.sprite_pattern_bits_lo
					self.sprite_shifter_pattern_hi[i] = self.sprite_pattern_bits_hi

		if self.scanline == 240:
			pass
		#print(self.scanline, self.cycle)
		if self.scanline >= 241 and self.scanline < 261:
			if self.scanline == 241 and self.cycle == 1:
				self.statusreg_vertical_blank = 1
				if self.controlreg_enable_nmi != 0:
					self.nmi = True

		self.bg_pixel = 0x00
		self.bg_palette = 0x00
		if self.maskreg_render_background != 0:
			if self.maskreg_render_background_left != 0 or (self.cycle >= 9):
				self.bit_mux = 0x8000 >> self.fine_x

				if (self.bg_shifter_pattern_lo & self.bit_mux) != 0:
					self.p0_pixel = 1
				else:
					self.p0_pixel = 0

				if (self.bg_shifter_pattern_hi & self.bit_mux) != 0:
					self.p1_pixel = 1
				else:
					self.p1_pixel = 0

				self.bg_pixel = (self.p1_pixel << 1) | self.p0_pixel

				if (self.bg_shifter_attrib_lo & self.bit_mux) != 0:
					self.bg_pal0 = 1
				else:
					self.bg_pal0 = 0

				if (self.bg_shifter_attrib_hi & self.bit_mux) != 0:
					self.bg_pal1 = 1
				else:
					self.bg_pal1 = 0

				self.bg_palette = (self.bg_pal1 << 1) | self.bg_pal0

		self.fg_pixel = 0x00
		self.fg_palette = 0x00
		self.fg_priority = 0x00
		if self.maskreg_render_sprites != 0:
			self.spriteZeroBeingRendered = False
			for i in range(self.sprite_count):
				if self.spriteScanline[(i * 4) + 3] == 0:

					if (self.sprite_shifter_pattern_lo[i] & 0x80) != 0x00:
						self.fg_pixel_lo = 1
					else:
						self.fg_pixel_lo = 0

					if (self.sprite_shifter_pattern_hi[i] & 0x80) != 0x00:
						self.fg_pixel_hi = 1
					else:
						self.fg_pixel_hi = 0

					self.fg_pixel = (self.fg_pixel_hi << 1) | self.fg_pixel_lo

					self.fg_palette = (self.spriteScanline[(i * 4) + 2] & 0x03) + 0x04

					if (self.spriteScanline[(i * 4) + 2]  & 0x20) == 0x00:
						self.fg_priority = 1
					else:
						self.fg_priority = 0

					if self.fg_pixel != 0:
						if i == 0:
							self.spriteZeroBeingRendered = True
						break

		self.pixel = 0x00
		self.palette = 0x00
		if self.bg_pixel == 0 and self.fg_pixel == 0:
			self.pixel = 0x00
			self.palette = 0x00

		elif self.bg_pixel == 0 and self.fg_pixel > 0:
			self.pixel = self.fg_pixel
			self.palette = self.fg_palette

		elif self.bg_pixel > 0 and self.fg_pixel == 0:
			self.pixel = self.bg_pixel
			self.palette = self.bg_palette

		elif self.bg_pixel > 0 and self.fg_pixel > 0:
			if self.fg_priority != 0:
				self.pixel = self.fg_pixel
				self.palette = self.fg_palette
			else:
				self.pixel = self.bg_pixel
				self.palette = self.bg_palette

			if self.spriteZeroHitPossible == True and self.spriteZeroBeingRendered == True:
				if self.maskreg_render_background != 0 & self.maskreg_render_sprites != 0:
					if (self.maskreg_render_background_left | self.maskreg_render_sprites_left) == 0:
						if self.cycle >= 9 and self.cycle < 258:
							self.statusreg_sprite_zero_hit = 1
					else:
						if self.cycle >= 1 and self.cycle < 258:
							self.statusreg_sprite_zero_hit = 1

		self.screen.set_at((self.cycle - 1, self.scanline), self.getColorFromPaletteRam(self.palette, self.pixel))

		self.cycle += 1
		if self.cycle >= 341:
			self.cycle = 0
			self.scanline += 1
			if self.scanline >= 261:
				self.scanline = -1
				self.framecomplete = True

				self.framecount += 1
				print(self.framecount)
				#print(self.oam)
				self.patternTable[0] = self.getPatternTable(0, self.selectedPalette)
				self.patternTable[1] = self.getPatternTable(1, self.selectedPalette)
				#print(self.patternTable[0])
				for self.tempy in range(128):
					for self.tempx in range(128):
						self.window.set_at((self.tempx + self.screen_width*self.scaling_factor, self.tempy), self.patternTable[0][self.tempx][self.tempy])
						self.window.set_at((self.tempx + self.screen_width*self.scaling_factor, self.tempy + 128), self.patternTable[1][self.tempx][self.tempy])
				self.scalesize = self.window.get_rect().size
				self.scalesize = (self.scalesize[0] - 128, self.scalesize[1])
				self.window.blit(pygame.transform.scale(self.screen, self.scalesize), (0, 0))
				pygame.display.flip()
				#print("OAM ADDR", self.oam_addr)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
