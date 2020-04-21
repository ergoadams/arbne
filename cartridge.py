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
			self.name = fp.read(4)		#char 4
			self.prg_rom_chunks = ord(fp.read(1)) 	#1 byte
			self.chr_rom_chunks = ord(fp.read(1))	#1 byte
			self.mapper1 = ord(fp.read(1))			#1 byte
			self.mapper2 = ord(fp.read(1))			#1 byte
			self.prg_ram_size = ord(fp.read(1))		#1 byte
			self.tv_system1 = ord(fp.read(1)) 		#1 byte
			self.tv_system2 = ord(fp.read(1))		#1 byte
			self.unused = fp.read(5)			#char 5

			if self.mapper1 & 0x04:
				fp.read(512)

			self.mapperID = ((self.mapper2 >> 4) << 4) | (self.mapper1 >> 4)
			if self.mapper1 & 0x01 == 0x01:
				self.mirror = "VERTICAL"
			else:
				self.mirror = "HORIZONTAL"


			self.filetype = 1

			if self.filetype == 0:
				pass

			elif self.filetype == 1:
				self.PRGbanks = self.prg_rom_chunks
				self.PRGmemory = bytearray(fp.read(self.PRGbanks*16384))
				print(len(self.PRGmemory))

				self.CHRbanks = self.chr_rom_chunks
				self.CHRmemory = bytearray(fp.read(self.CHRbanks*8192))
				print(len(self.CHRmemory))

			elif self.filetype == 2:
				pass

			print("MapperID:", self.mapperID)
			self.mapper = mapper()
			if self.mapperID == 0:
				self.umapper = self.mapper.mapper_000(self.PRGbanks, self.CHRbanks)

			self.imageValid = True


	def imageValid(self):
		return self.imageValid

	#Communication with main bus
	def cpuRead(self, addr):
		self.tempcheck, self.mapped_addr = self.umapper.cpuMapRead(addr)
		if self.tempcheck == True:
			self.data = self.PRGmemory[self.mapped_addr]
			return True, self.data
		else:
			return False, 0x00

	def cpuWrite(self, addr, data):
		self.tempcheck, self.mapped_addr = self.umapper.cpuMapWrite(addr)
		if self.tempcheck == True:
			self.PRGmemory[self.mapped_addr] = data
			return True
		else:
			return False

	#Communication with ppu bus
	def ppuRead(self, addr, readOnly = False):
		self.tempcheck, self.mapped_addr = self.umapper.ppuMapRead(addr)
		if self.tempcheck == True:
			self.data = self.CHRmemory[self.mapped_addr]
			return True, self.data
		else:
			return False, 0x00

	def ppuWrite(self, addr, data):
		self.tempcheck, self.mapped_addr = self.umapper.ppuMapWrite(addr)
		if self.tempcheck == True:
			self.CHRmemory[self.mapped_addr] = data
			return True
		else:
			return False
