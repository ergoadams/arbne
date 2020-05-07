from cartridge import cartridge
from random import randint
import pygame, time

class ppu:
    def __init__(self):
        self.running = True
        self.tblName = [[0] * 1024, [0] * 1024]
        self.tblPattern = [[0] * 4096, [0] * 4096]
        self.tblPalette = [0] * 32
        self.palScreen = {0: (84, 84, 84), 1: (0, 30, 116), 2: (8, 16, 144), 3: (48, 0, 136), 4: (68, 0, 100), 5: (92, 0, 48), 6: (84, 4, 0), 7: (60, 24, 0), 8: (32, 42, 0), 9: (8, 58, 0), 10: (0, 64, 0), 11: (0, 60, 0), 12: (0, 50, 60), 13: (0, 0, 0), 14: (0, 0, 0), 15: (0, 0, 0),
                         16: (152, 150, 152), 17: (8, 76, 196), 18: (48, 50, 236), 19: (92, 30, 228), 20: (136, 20, 176), 21: (160, 20, 100), 22: (152, 34, 32), 23: (120, 60, 0), 24: (84, 90, 0), 25: (40, 114, 0), 26: (8, 124, 0), 27: (0, 118, 40), 28: (0, 102, 120), 29: (0, 0, 0), 30: (0, 0, 0), 31: (0, 0, 0),
                         32: (236, 238, 236), 33: (76, 154, 236), 34: (120, 124, 236), 35: (176, 98, 236), 36: (228, 84, 236), 37: (236, 88, 180), 38: (236, 106, 100), 39: (212, 136, 32), 40: (160, 170, 0), 41: (116, 196, 0), 42: (76, 208, 32), 43: (56, 204, 108), 44: (56, 180, 204), 45: (60, 60, 60), 46: (0, 0, 0), 47: (0, 0, 0),
                         48: (236, 238, 236), 49: (168, 204, 236), 50: (188, 188, 236), 51: (212, 178, 236), 52: (236, 174, 236), 53: (236, 174, 212), 54: (236, 180, 176), 55: (228, 196, 144), 56: (204, 210, 120), 57: (180, 222, 120), 58: (168, 226, 144), 59: (152, 226, 180), 60: (160, 214, 228), 61: (160, 162, 160), 62: (0, 0, 0), 63: (0, 0, 0)
                        }
        self.framecount = 0
        self.frametime = 0
        self.starttime = 0
        self.cycle = 0
        self.scanline = 0
        self.framecomplete = False
        self.controller = [0, 0]
        self.selectedPalette = 0
        self.statusreg_unused = 0
        self.statusreg_sprite_overflow = 0
        self.statusreg_sprite_zero_hit = 0
        self.statusreg_vertical_blank = 0
        self.statusreg = 0
        self.maskreg_grayscale = 0
        self.maskreg_render_background_left = 0
        self.maskreg_render_sprites_left = 0
        self.maskreg_render_background = 0
        self.maskreg_render_sprites = 0
        self.maskreg_enhance_red = 0
        self.maskreg_enhance_green = 0
        self.maskreg_enhance_blue = 0
        self.maskreg = 0
        self.controlreg_nametable_x = 0
        self.controlreg_nametable_y = 0
        self.controlreg_increment_mode = 0
        self.controlreg_pattern_sprite = 0
        self.controlreg_pattern_background = 0
        self.controlreg_sprite_size = 0
        self.controlreg_slave_mode = 0
        self.controlreg_enable_nmi = 0
        self.controlreg = 0
        self.vram_addr_coarse_x = 0
        self.vram_addr_coarse_y = 0
        self.vram_addr_nametable_x = 0
        self.vram_addr_nametable_y = 0
        self.vram_addr_fine_y = 0
        self.vram_addr_unused = 0
        self.vram_addr = 0
        self.tram_addr_coarse_x = 0
        self.tram_addr_coarse_y = 0
        self.tram_addr_nametable_x = 0
        self.tram_addr_nametable_y = 0
        self.tram_addr_fine_y = 0
        self.tram_addr_unused = 0
        self.tram_addr = 0
        self.fine_x = 0
        self.address_latch = 0
        self.ppu_data_buffer = 0
        self.bg_next_tile_id = 0
        self.bg_next_tile_attrib = 0
        self.bg_next_tile_lsb = 0
        self.bg_next_tile_msb = 0
        self.bg_shifter_pattern_lo = 0
        self.bg_shifter_pattern_hi = 0
        self.bg_shifter_attrib_lo = 0
        self.bg_shifter_attrib_hi = 0
        self.nmi = False
        self.oam = [0] * 256
        self.oam_addr = 0
        self.spriteScanline = [0] * 32
        self.sprite_count = 0
        self.sprite_shifter_pattern_lo = [0] * 8
        self.sprite_shifter_pattern_hi = [0] * 8
        self.spriteZeroHitPossible = False
        self.spriteZeroBeingRendered = False
        self.odd_frame = False
        pygame.init()
        #TODO: add scaling support
        self.scaling_factor = 1
        self.screen_width, self.screen_height = 256, 240
        self.window = pygame.display.set_mode((self.screen_width*self.scaling_factor, self.screen_height*self.scaling_factor))
        self.screenarray = [0] * 256*240*3

    def getColorFromPaletteRam(self, addr):
        self.addr = addr & 0x1F
        self.addr = 0 if self.addr == 0x10 else 0x04 if self.addr == 0x14 else 0x08 if self.addr == 0x18 else 0x0C if self.addr == 0x18 else self.addr
        self.addr = self.tblPalette[self.addr] & 0x30 if self.maskreg_grayscale else self.tblPalette[self.addr] & 0x3F
        self.addr &= 0x3F
        return self.palScreen[self.addr]

    def cpuRead(self, addr, readOnly = False):
        self.data = 0x00
        if addr == 0x0000:
            pass
        elif addr == 0x0001:
            pass
        elif addr == 0x0002:
            self.statusreg = self.statusreg_unused
            self.statusreg |= (self.statusreg_sprite_overflow << 5)
            self.statusreg |= (self.statusreg_sprite_zero_hit << 6)
            self.statusreg |= (self.statusreg_vertical_blank << 7)
            self.data = (self.statusreg & 0xE0) | (self.ppu_data_buffer & 0x1F)
            self.statusreg_vertical_blank = 0
            self.address_latch = 0
        elif addr == 0x0003:
            pass
        elif addr == 0x0004:
            self.data = self.oam[self.oam_addr]
        elif addr == 0x0005:
            pass
        elif addr == 0x0006:
            pass
        elif addr == 0x0007:
            self.data = self.ppu_data_buffer
            self.vram_addr = self.vram_addr_coarse_x
            self.vram_addr |= (self.vram_addr_coarse_y << 5)
            self.vram_addr |= (self.vram_addr_nametable_x << 10)
            self.vram_addr |= (self.vram_addr_nametable_y << 11)
            self.vram_addr |= (self.vram_addr_fine_y << 12)
            self.vram_addr |= (self.vram_addr_unused << 15)
            self.data = self.ppuRead(self.vram_addr)
            if self.vram_addr & 0x3FFF < 0x3F00:
                self.buffer = self.data
                self.data = self.ppu_data_buffer
                self.ppu_data_buffer = self.buffer
            else:
                self.ppu_data_buffer = self.ppuRead(self.vram_addr - 0x1000)
            self.vram_addr = self.vram_addr + 32 if self.controlreg_increment_mode else self.vram_addr + 1
            self.vram_addr_coarse_x = self.vram_addr & 0b11111
            self.vram_addr_coarse_y = (self.vram_addr & 0b1111100000) >> 5
            self.vram_addr_nametable_x = (self.vram_addr & 0b10000000000) >> 10
            self.vram_addr_nametable_y = (self.vram_addr & 0b100000000000) >> 11
            self.vram_addr_fine_y = (self.vram_addr & 0b111000000000000) >> 12
            self.vram_addr_unused = (self.vram_addr & 0b1000000000000000) >> 15
        return self.data

    def cpuWrite(self, addr, data):
        if addr == 0x0000:
            self.controlreg = data
            self.controlreg_nametable_x= self.controlreg & 0b1
            self.controlreg_nametable_y = (self.controlreg & 0b10) >> 1
            self.controlreg_increment_mode = (self.controlreg & 0b100) >> 2
            self.controlreg_pattern_sprite = (self.controlreg & 0b1000) >> 3
            self.controlreg_pattern_background = (self.controlreg & 0b10000) >> 4
            self.controlreg_sprite_size = (self.controlreg & 0b100000) >> 5
            self.controlreg_slave_mode = (self.controlreg & 0b1000000) >> 6
            self.controlreg_enable_nmi = (self.controlreg & 0b10000000) >> 7
            self.tram_addr_nametable_x = self.controlreg_nametable_x
            self.tram_addr_nametable_y = self.controlreg_nametable_y
        elif addr == 0x0001:
            self.maskreg = data
            self.maskreg_grayscale= self.maskreg & 0b1
            self.maskreg_render_background_left = (self.maskreg & 0b10) >> 1
            self.maskreg_render_sprites_left = (self.maskreg & 0b100) >> 2
            self.maskreg_render_background = (self.maskreg & 0b1000) >> 3
            self.maskreg_render_sprites = (self.maskreg & 0b10000) >> 4
            self.maskreg_enhance_red = (self.maskreg & 0b100000) >> 5
            self.maskreg_enhance_green = (self.maskreg & 0b1000000) >> 6
            self.maskreg_enhance_blue = (self.maskreg & 0b10000000) >> 7
        elif addr == 0x0002:
            pass
        elif addr == 0x0003:
            self.oam_addr = data & 0xFF
        elif addr == 0x0004:
            self.oam[self.oam_addr] = data
            self.oam_addr = (self.oam_addr + 1) & 0xFF
        elif addr == 0x0005:
            if self.address_latch == 0:
                self.finex = data & 0x07
                self.tram_addr_coarse_x = data >> 3
                self.address_latch = 1
            else:
                self.tram_addr_fine_y = data & 0x07
                self.tram_addr_coarse_y = data >> 3
                self.address_latch = 0
        elif addr == 0x0006:
            self.tram_addr = self.tram_addr_coarse_x
            self.tram_addr |= (self.tram_addr_coarse_y << 5)
            self.tram_addr |= (self.tram_addr_nametable_x << 10)
            self.tram_addr |= (self.tram_addr_nametable_y << 11)
            self.tram_addr |= (self.tram_addr_fine_y << 12)
            self.tram_addr |= (self.tram_addr_unused << 15)
            if self.address_latch == 0:
                self.tram_addr = ((data & 0x3F) << 8) | (self.tram_addr & 0x00FF)
                self.address_latch = 1
            else:
                self.tram_addr = (self.tram_addr & 0xFF00) | data
                self.vram_addr = self.tram_addr
                self.vram_addr_coarse_x = self.vram_addr & 0b11111
                self.vram_addr_coarse_y = (self.vram_addr & 0b1111100000) >> 5
                self.vram_addr_nametable_x = (self.vram_addr & 0b10000000000) >> 10
                self.vram_addr_nametable_y = (self.vram_addr & 0b100000000000) >> 11
                self.vram_addr_fine_y = (self.vram_addr & 0b111000000000000) >> 12
                self.vram_addr_unused = (self.vram_addr & 0b1000000000000000) >> 15
                self.address_latch = 0
            self.tram_addr_coarse_x = self.tram_addr & 0b11111
            self.tram_addr_coarse_y = (self.tram_addr & 0b1111100000) >> 5
            self.tram_addr_nametable_x = (self.tram_addr & 0b10000000000) >> 10
            self.tram_addr_nametable_y = (self.tram_addr & 0b100000000000) >> 11
            self.tram_addr_fine_y = (self.tram_addr & 0b111000000000000) >> 12
            self.tram_addr_unused = (self.tram_addr & 0b1000000000000000) >> 15
        elif addr == 0x0007: #PPU data
            self.vram_addr = self.vram_addr_coarse_x
            self.vram_addr |= (self.vram_addr_coarse_y << 5)
            self.vram_addr |= (self.vram_addr_nametable_x << 10)
            self.vram_addr |= (self.vram_addr_nametable_y << 11)
            self.vram_addr |= (self.vram_addr_fine_y << 12)
            self.vram_addr |= (self.vram_addr_unused << 15)
            self.ppuWrite(self.vram_addr, data)
            self.vram_addr += 32 if self.controlreg_increment_mode else 1
            self.vram_addr_coarse_x = self.vram_addr & 0b11111
            self.vram_addr_coarse_y = (self.vram_addr & 0b1111100000) >> 5
            self.vram_addr_nametable_x = (self.vram_addr & 0b10000000000) >> 10
            self.vram_addr_nametable_y = (self.vram_addr & 0b100000000000) >> 11
            self.vram_addr_fine_y = (self.vram_addr & 0b111000000000000) >> 12
            self.vram_addr_unused = (self.vram_addr & 0b1000000000000000) >> 15

    def ppuRead(self, addr, readOnly = False):
        self.data = 0x00
        self.addr = addr & 0x3FFF
        if self.cartridge.ppuRead(self.addr, readOnly) == True:
            self.data = self.cartridge.CHRmemory[self.cartridge.mapped_addr]
        elif self.addr >= 0x0000 and self.addr <= 0x1FFF:
            self.data = self.tblPattern[(self.addr & 0x1000) >> 12][self.addr & 0x0FFF]
        elif self.addr >= 0x2000 and self.addr <= 0x3EFF:
            self.addr &= 0x0FFF
            if self.cartridge.mirror == "VERTICAL":
                if self.addr >= 0 and self.addr <= 0x03FF:
                    self.data = self.tblName[0][self.addr & 0x03FF]
                elif self.addr >= 0x0400 and self.addr <= 0x07FF:
                    self.data = self.tblName[1][self.addr & 0x03FF]
                elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
                    self.data = self.tblName[0][self.addr & 0x03FF]
                elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
                    self.data = self.tblName[1][self.addr & 0x03FF]
            elif self.cartridge.mirror == "HORIZONTAL":
                if self.addr >= 0 and self.addr <= 0x03FF:
                    self.data = self.tblName[0][self.addr & 0x03FF]
                elif self.addr >= 0x0400 and self.addr <= 0x07FF:
                    self.data = self.tblName[0][self.addr & 0x03FF]
                elif self.addr >= 0x0800 and self.addr <= 0x0BFF:
                    self.data = self.tblName[1][self.addr & 0x03FF]
                elif self.addr >= 0x0C00 and self.addr <= 0x0FFF:
                    self.data = self.tblName[1][self.addr & 0x03FF]
        return self.data

    def ppuWrite(self, addr, data):
        self.addr = addr & 0x3FFF
        if self.cartridge.ppuWrite(self.addr, data) == False:
            if self.addr >= 0x0000 and self.addr <= 0x1FFF:
                self.tblPattern[(self.addr & 0x1000) >> 12][self.addr & 0x0FFF] = data
            elif self.addr >= 0x2000 and self.addr <= 0x3EFF:
                self.addr &= 0x0FFF
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
                self.addr &= 0x1F
                self.addr = 0 if self.addr == 0x10 else 0x04 if self.addr == 0x14 else 0x08 if self.addr == 0x18 else 0x0C if self.addr == 0x1C else self.addr
                self.tblPalette[self.addr] = data

    def connectCartridge(self, cartridge):
        self.cartridge = cartridge

    def reset(self):
        self.fine_x = 0
        self.address_latch = 0
        self.ppu_data_buffer = 0
        self.scanline = 0
        self.cycle = 0
        self.bg_next_tile_id = 0
        self.bg_next_tile_attrib = 0
        self.bg_next_tile_lsb = 0
        self.bg_next_tile_msb = 0
        self.bg_shifter_pattern_lo = 0
        self.bg_shifter_pattern_hi = 0
        self.bg_shifter_attrib_lo = 0
        self.bg_shifter_attrib_hi = 0
        self.statusreg = 0
        self.statusreg_unused = 0
        self.statusreg_sprite_overflow = 0
        self.statusreg_sprite_zero_hit = 0
        self.statusreg_vertical_blank = 0
        self.maskreg = 0
        self.maskreg_grayscale = 0
        self.maskreg_render_background_left = 0
        self.maskreg_render_sprites_left = 0
        self.maskreg_render_background = 0
        self.maskreg_render_sprites = 0
        self.maskreg_enhance_red = 0
        self.maskreg_enhance_green = 0
        self.maskreg_enhance_blue = 0
        self.controlreg = 0
        self.controlreg_nametable_x = 0
        self.controlreg_nametable_y = 0
        self.controlreg_increment_mode = 0
        self.controlreg_pattern_sprite = 0
        self.controlreg_pattern_background = 0
        self.controlreg_sprite_size = 0
        self.controlreg_slave_mode = 0
        self.controlreg_enable_nmi = 0
        self.vram_addr = 0
        self.vram_addr_coarse_x = 0
        self.vram_addr_coarse_y = 0
        self.vram_addr_nametable_x = 0
        self.vram_addr_nametable_y = 0
        self.vram_addr_fine_y = 0
        self.vram_addr_unused = 0
        self.tram_addr = 0
        self.tram_addr_coarse_x = 0
        self.tram_addr_coarse_y = 0
        self.tram_addr_nametable_x = 0
        self.tram_addr_nametable_y = 0
        self.tram_addr_fine_y = 0
        self.tram_addr_unused = 0
        self.odd_frame = False

    def incrementScrollX(self):
        if self.maskreg_render_background or self.maskreg_render_sprites:
            if self.vram_addr_coarse_x == 31:
                self.vram_addr_coarse_x = 0
                self.vram_addr_nametable_x = ~self.vram_addr_nametable_x
            else:
                self.vram_addr_coarse_x += 1

    def incrementScrollY(self):
        if self.maskreg_render_background or self.maskreg_render_sprites:
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
        if self.maskreg_render_background or self.maskreg_render_sprites:
            self.vram_addr_nametable_x = self.tram_addr_nametable_x
            self.vram_addr_coarse_x = self.tram_addr_coarse_x

    def transferAddressY(self):
        if self.maskreg_render_background or self.maskreg_render_sprites:
            self.vram_addr_fine_y = self.tram_addr_fine_y
            self.vram_addr_nametable_y = self.tram_addr_nametable_y
            self.vram_addr_coarse_y = self.tram_addr_coarse_y

    def loadBackgroundShifters(self):
        self.bg_shifter_pattern_lo = (self.bg_shifter_pattern_lo & 0xFF00) | self.bg_next_tile_lsb
        self.bg_shifter_pattern_hi = (self.bg_shifter_pattern_hi & 0xFF00) | self.bg_next_tile_msb
        self.bg_shifter_attrib_lo = self.bg_shifter_attrib_lo | 0xFF if self.bg_next_tile_attrib & 0x01 else self.bg_shifter_attrib_lo & 0xFF00
        self.bg_shifter_attrib_hi = self.bg_shifter_attrib_hi | 0xFF if self.bg_next_tile_attrib & 0x02 else self.bg_shifter_attrib_hi & 0xFF00

    def updateShifters(self):
        if self.maskreg_render_background:
            self.bg_shifter_pattern_lo <<= 1
            self.bg_shifter_pattern_hi <<= 1
            self.bg_shifter_attrib_lo <<= 1
            self.bg_shifter_attrib_hi <<= 1

        if self.maskreg_render_sprites and self.cycle > 0 and self.cycle < 258:
            for i in range(self.sprite_count):
                if self.spriteScanline[(i * 4) + 3]:
                    self.spriteScanline[(i * 4) + 3] -= 1
                else:
                    self.sprite_shifter_pattern_lo[i] <<= 1
                    self.sprite_shifter_pattern_hi[i] <<= 1

    def flipByte(self, b):
        b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
        b = (b & 0xCC) >> 2 | (b & 0x33) << 2
        b = (b & 0xAA) >> 1 | (b & 0x55) << 1
        return b

    def clock(self):
        if (self.scanline >= -1) and (self.scanline < 240):
            if self.scanline == 0 and self.cycle == 0 and self.odd_frame and (self.maskreg_render_background or self.maskreg_render_sprites):
                self.cycle = 1
            if self.scanline == -1 and self.cycle == 1:
                self.statusreg_vertical_blank = self.statusreg_sprite_zero_hit = self.statusreg_sprite_overflow = 0
                self.sprite_shifter_pattern_lo = [0] * 8
                self.sprite_shifter_pattern_hi = [0] * 8
            if (self.cycle >= 2 and self.cycle < 258) or (self.cycle >= 321 and self.cycle < 338):
                self.updateShifters()
                self.switchcase = (self.cycle - 1) % 8
                if self.switchcase == 0:
                    self.loadBackgroundShifters()
                    self.vram_addr = self.vram_addr_coarse_x
                    self.vram_addr |= (self.vram_addr_coarse_y << 5)
                    self.vram_addr |= (self.vram_addr_nametable_x << 10)
                    self.vram_addr |= (self.vram_addr_nametable_y << 11)
                    self.vram_addr |= (self.vram_addr_fine_y << 12)
                    self.vram_addr |= (self.vram_addr_unused << 15)
                    self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))
                elif self.switchcase == 2:
                    self.bg_next_tile_attrib = self.ppuRead(0x23C0 | (self.vram_addr_nametable_y << 11) | (self.vram_addr_nametable_x << 10) | ((self.vram_addr_coarse_y >> 2) << 3) | (self.vram_addr_coarse_x >> 2))
                    if self.vram_addr_coarse_y & 0x02:
                        self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 4
                    if self.vram_addr_coarse_x & 0x02:
                        self.bg_next_tile_attrib = self.bg_next_tile_attrib >> 2
                    self.bg_next_tile_attrib &= 0x03
                elif self.switchcase == 4:
                    self.bg_next_tile_lsb = self.ppuRead((self.controlreg_pattern_background << 12) + (self.bg_next_tile_id << 4) + self.vram_addr_fine_y)
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
                self.vram_addr = 0 | self.vram_addr_coarse_x
                self.vram_addr |= (self.vram_addr_coarse_y << 5)
                self.vram_addr |= (self.vram_addr_nametable_x << 10)
                self.vram_addr |= (self.vram_addr_nametable_y << 11)
                self.vram_addr |= (self.vram_addr_fine_y << 12)
                self.vram_addr |= (self.vram_addr_unused << 15)
                self.bg_next_tile_id = self.ppuRead(0x2000 | (self.vram_addr & 0x0FFF))
            if self.scanline == -1 and self.cycle >= 280 and self.cycle < 305:
                self.transferAddressY()
            if self.cycle == 257 and self.scanline >= 0:
                self.spriteScanline = [255] * 32
                self.sprite_count = 0
                self.sprite_shifter_pattern_lo = [0] * 8
                self.sprite_shifter_pattern_hi = [0] * 8
                self.oamEntry = self.oam_addr & 0xFF
                self.spriteZeroHitPossible = False
                while self.oamEntry < 255 and self.sprite_count <= 9:
                    self.diff = self.scanline - self.oam[self.oamEntry]
                    self.tempdiff = 16 if self.controlreg_sprite_size else 8
                    if (self.diff >= 0) and (self.diff < self.tempdiff) and self.sprite_count < 8:
                        if self.sprite_count < 8:
                            if self.oamEntry == 0:
                                self.spriteZeroHitPossible = True
                            self.tempaddr = self.sprite_count * 4
                            self.spriteScanline[self.tempaddr] = self.oam[self.oamEntry]
                            self.spriteScanline[self.tempaddr + 1] = self.oam[self.oamEntry + 1]
                            self.spriteScanline[self.tempaddr + 2] = self.oam[self.oamEntry + 2]
                            self.spriteScanline[self.tempaddr + 3] = self.oam[self.oamEntry + 3]
                        self.sprite_count += 1
                    self.oamEntry += 4
                self.statusreg_sprite_overflow = 1 if self.sprite_count >= 8 else 0
            if self.cycle == 340:
                for i in range(self.sprite_count):
                    self.sprite_pattern_bits_lo = self.sprite_pattern_bits_hi = 0
                    self.sprite_pattern_addr_lo = self.sprite_pattern_addr_hi = 0
                    self.tempaddr = i * 4
                    if self.controlreg_sprite_size == 0:
                        if (self.spriteScanline[self.tempaddr + 2]  & 0x80) == 0x00:
                            self.sprite_pattern_addr_lo = (self.controlreg_pattern_sprite << 12) | (self.spriteScanline[self.tempaddr + 1] << 4) | (self.scanline - self.spriteScanline[self.tempaddr])
                        else:
                            self.sprite_pattern_addr_lo = (self.controlreg_pattern_sprite << 12) | (self.spriteScanline[self.tempaddr + 1] << 4) | (7 - (self.scanline - self.spriteScanline[self.tempaddr]))
                    else:
                        if (self.spriteScanline[(i * 4) + 2] & 0x80) == 0x00:
                            if (self.scanline - self.spriteScanline[i * 4]) < 8:
                                self.pattern_addr_lo = ((self.spriteScanline[self.tempaddr + 1] & 0x01) << 12) | ((self.spriteScanline[self.tempaddr + 1] & 0xFE) << 4) | ((self.scanline - (self.spriteScanline[self.tempaddr]) & 0x07))
                            else:
                                self.pattern_addr_lo = ((self.spriteScanline[self.tempaddr + 1] & 0x01) << 12) | (((self.spriteScanline[self.tempaddr + 1] & 0xFE) + 1) << 4) | ((self.scanline - (self.spriteScanline[self.tempaddr]) & 0x07))
                        else:
                            if (self.scanline - self.spriteScanline[self.tempaddr]) < 8:
                                self.pattern_addr_lo = ((self.spriteScanline[self.tempaddr + 1] & 0x01) << 12) | (((self.spriteScanline[self.tempaddr + 1] & 0xFE) + 1) << 4) | (7 - (self.scanline - (self.spriteScanline[self.tempaddr] & 0x07)))
                            else:
                                self.pattern_addr_lo = ((self.spriteScanline[self.tempaddr + 1] & 0x01) << 12) | ((self.spriteScanline[self.tempaddr + 1] & 0xFE) << 4) | (7 - (self.scanline - (self.spriteScanline[self.tempaddr] & 0x07)))


                    self.sprite_pattern_addr_hi = self.sprite_pattern_addr_lo + 8
                    self.sprite_pattern_bits_lo = self.ppuRead(self.sprite_pattern_addr_lo)
                    self.sprite_pattern_bits_hi = self.ppuRead(self.sprite_pattern_addr_hi)
                    if self.spriteScanline[self.tempaddr + 2] & 0x40:
                        self.sprite_pattern_bits_lo = self.flipByte(self.sprite_pattern_bits_lo)
                        self.sprite_pattern_bits_hi = self.flipByte(self.sprite_pattern_bits_hi)
                    self.sprite_shifter_pattern_lo[i] = self.sprite_pattern_bits_lo
                    self.sprite_shifter_pattern_hi[i] = self.sprite_pattern_bits_hi
        if self.scanline >= 241 and self.scanline < 261:
            if self.scanline == 241 and self.cycle == 1:
                self.statusreg_vertical_blank = 1
                if self.controlreg_enable_nmi:
                    self.nmi = True
        self.bg_pixel, self.bg_palette = 0, 0
        if self.maskreg_render_background:
            if self.maskreg_render_background_left or self.cycle >= 9:
                self.bit_mux = 0x8000 >> self.fine_x
                self.p0_pixel = 1 if self.bg_shifter_pattern_lo & self.bit_mux else 0
                self.p1_pixel = 1 if self.bg_shifter_pattern_hi & self.bit_mux else 0
                self.bg_pixel = (self.p1_pixel << 1) | self.p0_pixel
                self.bg_pal0 = 1 if self.bg_shifter_attrib_lo & self.bit_mux else 0
                self.bg_pal1 = 1 if self.bg_shifter_attrib_hi & self.bit_mux else 0
                self.bg_palette = (self.bg_pal1 << 1) | self.bg_pal0
        self.fg_pixel, self.fg_palette, self.fg_priority = 0, 0, 0
        if self.maskreg_render_sprites:
            if self.maskreg_render_sprites_left or self.cycle >= 9:
                self.spriteZeroBeingRendered = False
                for i in range(self.sprite_count):
                    self.tempaddr = i * 4
                    if self.spriteScanline[self.tempaddr + 3] == 0:
                        self.fg_pixel_lo = 1 if (self.sprite_shifter_pattern_lo[i]) & 0x80 else 0
                        self.fg_pixel_hi = 1 if (self.sprite_shifter_pattern_hi[i]) & 0x80 else 0
                        self.fg_pixel = (self.fg_pixel_hi << 1) | self.fg_pixel_lo
                        self.fg_palette = (self.spriteScanline[self.tempaddr + 2] & 0x03) + 0x04
                        self.fg_priority = 1 if (self.spriteScanline[self.tempaddr + 2]  & 0x20) == 0x00 else 0
                        if self.fg_pixel:
                            if i == 0:
                                self.spriteZeroBeingRendered = True
                            break
        self.pixel, self.palette = 0, 0
        if self.bg_pixel == 0 and self.fg_pixel == 0:
            self.pixel, self.palette = 0, 0
        elif self.bg_pixel == 0 and self.fg_pixel > 0:
            self.pixel, self.palette = self.fg_pixel, self.fg_palette
        elif self.bg_pixel > 0 and self.fg_pixel == 0:
            self.pixel, self.palette = self.bg_pixel, self.bg_palette
        elif self.bg_pixel > 0 and self.fg_pixel > 0:
            self.pixel, self.palette = (self.fg_pixel, self.fg_palette) if self.fg_priority else (self.bg_pixel, self.bg_palette)
            if self.spriteZeroHitPossible == True and self.spriteZeroBeingRendered == True and self.maskreg_render_background & self.maskreg_render_sprites:
                if (self.maskreg_render_background_left | self.maskreg_render_sprites_left) == 0 and self.cycle >= 9 and self.cycle < 256:
                    self.statusreg_sprite_zero_hit = 1
                else:
                    if self.cycle >= 1 and self.cycle < 256:
                        self.statusreg_sprite_zero_hit = 1
        if self.cycle <= 256 and self.cycle >= 1 and self.scanline < 240:
            self.offset = self.scanline*256*3 + (self.cycle-1)*3
            self.tempcolor = self.getColorFromPaletteRam(0x3F00 + (self.palette << 2) + self.pixel)
            self.screenarray[self.offset + 0] = self.tempcolor[0]
            self.screenarray[self.offset + 1] = self.tempcolor[1]
            self.screenarray[self.offset + 2] = self.tempcolor[2]
        self.cycle += 1
        if (self.maskreg_render_background or self.maskreg_render_sprites) and self.cycle == 260 and self.scanline < 240:
            self.cartridge.umapper.scanline()
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            if self.scanline >= 261:
                self.scanline = -1
                self.odd_frame = True if self.odd_frame == False else False
                self.framecomplete = True
                self.framecount += 1
                #Render frame
                self.img = pygame.image.frombuffer(bytearray(self.screenarray), (256, 240), "RGB")
                self.window.blit(self.img, (0, 0), pygame.Rect(0, 0, 256, 240))
                pygame.display.update()
                self.pressedKey = pygame.key.get_pressed()
                self.controller[0] = 0x00
                if self.pressedKey[pygame.K_x]:
                    self.controller[0] |= 0x80
                if self.pressedKey[pygame.K_z]:
                    self.controller[0] |= 0x40
                if self.pressedKey[pygame.K_a]:
                    self.controller[0] |= 0x20
                if self.pressedKey[pygame.K_s]:
                    self.controller[0] |= 0x10
                if self.pressedKey[pygame.K_UP]:
                    self.controller[0] |= 0x08
                if self.pressedKey[pygame.K_DOWN]:
                    self.controller[0] |= 0x04
                if self.pressedKey[pygame.K_LEFT]:
                    self.controller[0] |= 0x02
                if self.pressedKey[pygame.K_RIGHT]:
                    self.controller[0] |= 0x01
                if self.pressedKey[pygame.K_r]:
                    self.reset()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

