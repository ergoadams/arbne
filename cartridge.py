from mapper import mapper

class cartridge:
    def __init__(self, filename):

        self.mapperID = 0
        self.PRGbanks = 0
        self.CHRbanks = 0
        self.mapper = 0
        self.imageValid = False
        self.mirror = "HORIZONTAL"
        with open(filename, 'rb') as fp:
            self.name = fp.read(4)                    #char 4
            self.prg_rom_chunks = ord(fp.read(1))     #1 byte
            self.chr_rom_chunks = ord(fp.read(1))     #1 byte
            self.mapper1 = ord(fp.read(1))            #1 byte
            self.mapper2 = ord(fp.read(1))            #1 byte
            self.prg_ram_size = ord(fp.read(1))       #1 byte
            self.tv_system1 = ord(fp.read(1))         #1 byte
            self.tv_system2 = ord(fp.read(1))         #1 byte
            self.unused = fp.read(5)                  #char 5
            if self.mapper1 & 0x04:
                fp.read(512)
            self.mapperID = ((self.mapper2 >> 4) << 4) | (self.mapper1 >> 4)
            self.mirror = "VERTICAL" if self.mapper1 & 0x01 else "HORIZONTAL"
            self.filetype = 1
            if (self.mapper2 & 0x0C) == 0x08:
                self.filetype = 2
            if self.filetype == 1:
                self.PRGbanks = self.prg_rom_chunks
                self.PRGmemory = bytearray(fp.read(self.PRGbanks*16384))
                self.CHRbanks = self.chr_rom_chunks
                self.CHRmemory = bytearray(8192) if self.CHRbanks == 0 else bytearray(fp.read(self.CHRbanks*8192))
            elif self.filetype == 2:
                self.PRGbanks = ((self.prg_ram_size & 0x07) << 8) | self.prg_rom_chunks
                self.PRGmemory = bytearray(fp.read(self.PRGbanks*16384))
                self.CHRbanks = ((self.prg_ram_size & 0x38) << 8) | self.chr_rom_chunks
                self.CHRmemory = bytearray(fp.read(self.CHRbanks*8192))
            self.mapper = mapper()
            if self.mapperID == 0:
                self.umapper = self.mapper.mapper_000(self.PRGbanks, self.CHRbanks)
            elif self.mapperID == 1:
                self.umapper = self.mapper.mapper_001(self.PRGbanks, self.CHRbanks)
            elif self.mapperID == 2:
                self.umapper = self.mapper.mapper_002(self.PRGbanks, self.CHRbanks)
            elif self.mapperID == 3:
                self.umapper = self.mapper.mapper_003(self.PRGbanks, self.CHRbanks)
            elif self.mapperID == 4:
                self.umapper = self.mapper.mapper_004(self.PRGbanks, self.CHRbanks)
            elif self.mapperID == 66:
                self.umapper = self.mapper.mapper_066(self.PRGbanks, self.CHRbanks)
            else:
                print("Mapper not yet implemented")
            self.imageValid = True

            print("Name:", self.name)
            print("PRG rom chunks:", self.prg_rom_chunks)
            print("CHR rom chunks:", self.chr_rom_chunks)
            print("Mapper1, Mapper2:", self.mapper1, self.mapper2)
            print("PRG ram size:", self.prg_ram_size)
            print("TV system 1, TV system 2:", self.tv_system1, self.tv_system2)
            print("Mirror:", self.mirror)
            print("Filetype:", self.filetype)
            print("MapperID:", self.mapperID)

    def imageValid(self):
        return self.imageValid
    def reset(self):
        self.umapper.reset()
    def cpuRead(self, addr):
        self.tempcheck, self.mapped_addr, self.data = self.umapper.cpuMapRead(addr)
        if self.tempcheck:
            if self.mapped_addr == 0xFFFFFFFFF:
                return True, self.data
            return True, self.PRGmemory[self.mapped_addr]
        return False, 0
    def cpuWrite(self, addr, data):
        self.tempcheck, self.mapped_addr = self.umapper.cpuMapWrite(addr, data)
        if self.tempcheck:
            if self.mapped_addr == 0xFFFFFFFF:
                return True
            else:
                self.PRGmemory[self.mapped_addr] = data
                return True
        return False
    def ppuRead(self, addr, readOnly = False):
        self.tempcheck, self.mapped_addr = self.umapper.ppuMapRead(addr)
        return True if self.tempcheck else False
    def ppuWrite(self, addr, data):
        if self.umapper.ppuMapWrite(addr):
            self.CHRmemory[addr] = data
            return True
        return False
