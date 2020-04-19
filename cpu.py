from enum import Enum

class cpu:

	#Addressing modes
	def IMP(self):
		self.fetched = self.a
		return 0
	def IMM(self):
		self.addr_abs += self.pc
		self.pc += 1
		return 0
	def ZP0(self):
		self.addr_abs = self.read(self.pc)
		self.pc += 1
		self.addr_abs = self.addr_abs & 0xFF
		return 0
	def ZPX(self):
		self.addr_abs = self.read(self.pc + self.x)
		self.pc += 1
		self.addr_abs = self.addr_abs & 0xFF
		return 0
	def ZPY(self):
		self.addr_abs = self.read(self.pc + self.y)
		self.pc += 1
		self.addr_abs = self.addr_abs & 0xFF
		return 0
	def REL(self):
		self.addr_rel = self.read(self.pc)
		self.pc += 1
		if self.addr_rel & 0x80:
			self.addr_rel = self.addr_rel | 0xFF00
		return 0
	def ABS(self):
		self.lo = self.read(self.pc)
		self.pc += 1
		self.hi = self.read(self.pc)
		self.pc += 1
		self.addr_abs = (self.hi << 8) | self.lo
		return 0
	def ABX(self):
		self.lo = self.read(self.pc)
		self.pc += 1
		self.hi = self.read(self.pc)
		self.pc += 1
		self.addr_abs = (self.hi << 8) | self.lo
		self.addr_abs += self.x

		if (self.addr_abs & 0xFF00) != (self.hi << 8):
			return 1
		else:
			return 0
	def ABY(self):
		self.lo = self.read(self.pc)
		self.pc += 1
		self.hi = self.read(self.pc)
		self.pc += 1
		self.addr_abs = (self.hi << 8) | (self.lo)
		self.addr_abs += self.y

		if (self.addr_abs & 0xFF00) != (self.hi << 8):
			return 1
		else:
			return 0
	def IND(self):
		self.ptr_lo = self.read(self.pc)
		self.pc += 1
		self.ptr_hi = self.read(self.pc)
		self.pc += 1

		self.ptr = (self.ptr_hi << 8) | self.ptr_lo

		if self.ptr_lo == 0xFF:
			self.addr_abs = (self.read(self.ptr & 0xFF00) << 8) | self.read(self.ptr + 0)
		else:
			self.addr_abs = (self.read(self.ptr + 1) << 8) | self.read(self.ptr + 0)

		return 0
	def IZX(self):
		self.t = self.read(self.pc)
		self.pc += 1
		self.lo = self.read((self.t + self.x) & 0xFF)
		self.hi = self.read((self.t + self.x + 1) & 0xFF)
		self.addr_abs = (self.hi << 8) | self.lo
		return 0
	def IZY(self):
		self.t = self.read(self.pc, False)
		self.pc += 1
		self.lo = self.read(self.t & 0xFF, False)
		self.hi = self.read((self.t + 1) & 0xFF, False)
		self.addr_abs = (self.hi << 8) | self.lo
		self.addr_abs += self.y

		if (self.addr_abs & 0xFF00) != (self.hi << 8):
			return 1
		else:
			return 0

	#Opcodes
	def ADC(self):
		self.fetch()
		self.temp = self.a + self.fetched + self.getFlag(flags.C.value)
		self.setFlag(flags.C.value, self.temp > 0xFF)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.setFlag(flags.V.value, (~(self.a ^ self.fetched) & (self.a ^ self.temp)) & 0x80)
		self.a = self.temp & 0xFF
		return 1
	def AND(self):
		self.fetch()
		self.a = self.a & self.fetched
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 1
	def ASL(self):
		self.fetch()
		self.temp = self.fetched << 1
		self.setFlag(flags.C.value, (self.temp & 0xFF00) > 0x00)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		if self.lookup[self.temp1][self.temp2][1] == self.IMP:
			self.a = self.temp & 0xFF
		else:
			write(self.addr_abs, self.temp & 0xFF)
		return 0
	def BCC(self):
		if self.getFlag(flags.C.value) == 0x00:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BCS(self):
		if self.getFlag(flags.C.value) == 0x01:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BEQ(self):
		if self.getFlag(flags.Z.value) == 0x01:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BIT(self):
		self.fetch()
		self.temp = self.a & self.fetched
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.fetched & (1 << 7))
		self.setFlag(flags.V.value, self.fetched & (1 << 6))
		return 0
	def BMI(self):
		if self.getFlag(flags.N.value) == 0x01:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BNE(self):
		if self.getFlag(flags.Z.value) == 0x00:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BPL(self):
		if self.getFlag(flags.N.value) == 0x00:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BRK(self):
		self.pc += 1
		self.setFlag(flags.I.value, 1)
		self.write(0x0100 + self.stkp, (self.pc >> 8) & 0xFF)
		self.stkp += -1
		self.write(0x0100 + self.stkp, self.pc & 0xFF)
		self.stkp += -1

		self.setFlag(flags.B.value, 1)
		self.write(0x0100 + self.stkp, self.status)
		self.stkp += -1
		self.setFlag(flags.B.value, 0)
		self.pc = self.read(0xFFFE) | (self.read(0xFFFF) << 8)
	def BVC(self):
		if self.getFlag(flags.V.value) == 0:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BVS(self):
		if self.getFlag(flags.V.value) == 1:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def CLC(self):
		self.setFlag(flags.C.value, False)
		return 0
	def CLD(self):
		self.setFlag(flags.D.value, False)
		return 0
	def CLI(self):
		self.setFlag(flags.I.value, False)
		return 0
	def CLV(self):
		self.setFlag(flags.V.value, False)
		return 0
	def CMP(self):
		self.fetch()
		self.temp = self.a - self.fetched
		self.setFlag(flags.C.value, self.a >= self.fetched)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		return 1
	def CPX(self):
		self.fetch()
		self.temp = self.x - self.fetched
		self.setFlag(flags.C.value, self.x >= self.fetched)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		return 0
	def CPY(self):
		self.fetch()
		self.temp = self.y - self.fetched
		self.setFlag(flags.C.value, self.y >= self.fetched)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		return 0
	def DEC(self):
		self.fetch()
		self.temp = self.fetched - 1
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		return 0
	def DEX(self):
		self.x += -1
		self.setFlag(flags.Z.value, self.x == 0x00)
		self.setFlag(flags.N.value, self.x & 0x80)
		return 0
	def DEY(self):
		self.y += -1
		self.setFlag(flags.Z.value, self.y == 0x00)
		self.setFlag(flags.N.value, self.y & 0x80)
		return 0
	def EOR(self):
		self.fetch()
		self.a = self.a ^ self.fetched
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 1
	def INC(self):
		self.fetch()
		self.temp = self.fetched + 1
		self.write(self.addr_abs, self.temp & 0xFF)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		return 0
	def INX(self):
		self.x += 1
		self.setFlag(flags.Z.value, self.x == 0x00)
		self.setFlag(flags.N.value, self.x & 0x80)
		return 0
	def INY(self):
		self.y += 1
		self.setFlag(flags.Z.value, self.y == 0x00)
		self.setFlag(flags.N.value, self.y & 0x80)
		return 0
	def JMP(self):
		self.pc = self.addr_abs
		return 0
	def JSR(self):
		self.pc += -1
		self.write(0x0100 + self.stkp, (self.pc >> 8) & 0xFF)
		self.stkp += -1
		self.write(0x0100 + self.stkp, self.pc & 0xFF)
		self.stkp += -1
		self.pc = self.addr_abs
		return 0
	def LDA(self):
		self.fetch()
		self.a = self.fetched
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 1
	def LDX(self):
		self.fetch()
		self.x = self.fetched
		self.setFlag(flags.Z.value, self.x == 0x00)
		self.setFlag(flags.N.value, self.x & 0x80)
		return 1
	def LDY(self):
		self.fetch()
		self.y = self.fetched
		self.setFlag(flags.Z.value, self.y == 0)
		self.setFlag(flags.N.value, self.y & 0x80)
		return 1
	def LSR(self):
		self.fetch()
		self.setFlag(flags.C.value, self.fetched & 1)
		self.temp = self.fetched >> 1
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		if lookup[self.temp1][self.temp2][1] == selp.IMP:
			self.a = self.temp & 0xFF
		else:
			self.write(self.addr_abs, self.temp & 0xFF)
		return 0
	def NOP(self):
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		if self.temp1 == 15 and self.temp2 == 11:
			return 1
		return 0
	def ORA(self):
		self.fetch()
		self.a = self.a | self.fetched
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 1
	def PHA(self):
		write(0x0100 + self.stkp, self.a)
		self.stkp += -1
		return 0
	def PHP(self):
		self.write(0x0100 + self.stkp, self.status | flags.B.value | flags.U.value)
		self.setFlag(flags.B.value, 0)
		self.setFlag(flags.U.value, 0)
		self.stkp += -1
		return 0
	def PLA(self):
		self.stkp += 1
		self.a = read(0x0100 + self.stkp)
		setFlag(flags.Z.value, self.a == 0)
		setFlag(flags.N.value, self.a & 0x80)
		return 0
	def PLP(self):
		self.stkp += 1
		self.status = self.read(0x0100 + self.stkp)
		self.setFlag(flags.U.value, 1)
		return 1
	def ROL(self):
		self.fetch()
		self.temp = (self.fetched << 1) | self.getFlag(flags.C.value)
		self.setFlag(flags.C.value, self.temp & 0xFF00)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		if self.lookup[self.temp1][self.temp2][1] == self.IMP:
			self.a = self.temp & 0xFF
		else:
			self.write(self.addr_abs, self.temp & 0xFF)
		return 0
	def ROR(self):
		self.fetch()
		self.temp = (self.getFlag(flags.C.value) << 7) | (self.fetched >> 1)
		self.setFlag(flags.C.value, self.fetched & 0x01)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		if self.lookup[self.temp1][self.temp2][1] == self.IMP:
			self.a = self.temp & 0xFF
		else:
			self.write(self.addr_abs, self.temp & 0xFF)
		return 0
	def RTI(self):
		self.stkp += 1
		self.status = self.read(0x0100 + self.stkp)
		self.status = self.status & ~flags.B.value
		self.status = self.status & ~flags.U.value
		self.stkp += 1
		self.pc = self.read(0x0100 + self.stkp)
		self.stkp += 1
		self.pc = self.pc | self.read(0x0100 + self.stkp) << 8
		return 0
	def RTS(self):
		self.stkp += 1
		self.pc = self.read(0x0100 + self.stkp)
		self.stkp += 1
		self.pc = self.pc | (self.read(0x0100 + self.stkp) << 8)
	def SBC(self):
		self.fetch()
		self.value = self.fetched ^ 0xFF
		self.temp = self.a + self.value + self.getFlag(flags.C.value)
		self.setFlag(flags.C.value, self.temp & 0xFF00)
		self.setFlag(flags.Z.value, (self.temp & 0xFF) == 0x00)
		self.setFlag(flags.N.value, self.temp & 0x80)
		self.setFlag(flags.V.value, (self.temp ^ self.a) & (self.temp ^ self.value) & 0x80)
		self.a = self.temp & 0xFF
		return 1
	def SEC(self):
		self.setFlag(flags.C.value, True)
		return 0
	def SED(self):
		self.setFlag(flags.D.value, True)
		return 0
	def SEI(self):
		self.setFlag(flags.I.value, True)
		return 0
	def STA(self):
		self.write(self.addr_abs, self.a)
		return 0
	def STX(self):
		self.write(self.addr_abs, self.x)
		return 0
	def STY(self):
		self.write(self.addr_abs, self.y)
		return 0
	def TAX(self):
		self.x = self.a
		self.setFlag(flags.Z.value, self.x == 0x00)
		self.setFlag(flags.N.value, self.x & 0x80)
		return 0
	def TAY(self):
		self.y = self.a
		self.setFlag(flags.Z.value, self.y == 0x00)
		self.setFlag(flags.N.value, self.y & 0x80)
		return 0
	def TSX(self):
		self.x = self.stkp
		self.setFlag(flags.Z.value, self.x == 0x00)
		self.setFlag(flags.N.value, self.x & 0x80)
		return 0
	def TXA(self):
		self.a = self.x
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 0
	def TXS(self):
		self.stkp = self.x
		return 0
	def TYA(self):
		self.a = self.y
		self.setFlag(flags.Z.value, self.a == 0x00)
		self.setFlag(flags.N.value, self.a & 0x80)
		return 0
	def XXX(self):
		return 0

	def __init__(self, cpuram, bus):
		self.cpuram = cpuram         #Passing RAM to the cpu
		self.bus = bus
		self.a = 0x00             #Accumulator register
		self.x = 0x00             #X register
		self.y = 0x00             #Y register
		self.stkp = 0x00          #Stack pointer (points to location on bus)
		self.pc = 0x0000            #Program counter
		self.status = 0x00        #Status register

		self.fetched = 0x00       #Fetched data

		self.addr_abs = 0x0000
		self.addr_rel =  0x00
		self.opcode =  0x00
		self.cycles = 0

		self.lookup = [[[self.BRK, self.IMM, 7], [self.ORA, self.IZX, 6], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 3], [self.ORA, self.ZP0, 3], [self.ASL, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.PHP, self.IMP, 3], [self.ORA, self.IMM, 2], [self.ASL, self.IMP, 2], [self.XXX, self.IMP, 2], [self.NOP, self.IMP, 4], [self.ORA, self.ABS, 4], [self.ASL, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BPL, self.REL, 2], [self.ORA, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.ORA, self.ZPX, 4], [self.ASL, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.CLC, self.IMP, 2], [self.ORA, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.ORA, self.ABX, 4], [self.ASL, self.ABX, 7], [self.XXX, self.IMP, 7]],
					   [[self.JSR, self.ABS, 6], [self.AND, self.IZX, 6], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.BIT, self.ZP0, 3], [self.AND, self.ZP0, 3], [self.ROL, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.PLP, self.IMP, 4], [self.AND, self.IMM, 2], [self.ROL, self.IMP, 2], [self.XXX, self.IMP, 2], [self.BIT, self.ABS, 4], [self.AND, self.ABS, 4], [self.ROL, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BMI, self.REL, 2], [self.AND, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.AND, self.ZPX, 4], [self.ROL, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.SEC, self.IMP, 2], [self.AND, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.AND, self.ABX, 4], [self.ROL, self.ABX, 7], [self.XXX, self.IMP, 7]],
					   [[self.RTI, self.IMP, 6], [self.EOR, self.IZX, 6], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 3], [self.EOR, self.ZP0, 3], [self.LSR, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.PHA, self.IMP, 3], [self.EOR, self.IMM, 2], [self.LSR, self.IMP, 2], [self.XXX, self.IMP, 2], [self.JMP, self.ABS, 3], [self.EOR, self.ABS, 4], [self.LSR, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BVC, self.REL, 2], [self.EOR, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.EOR, self.ZPX, 4], [self.LSR, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.CLI, self.IMP, 2], [self.EOR, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.EOR, self.ABX, 4], [self.LSR, self.ABX, 7], [self.XXX, self.IMP, 7]],
					   [[self.RTS, self.IMP, 6], [self.ADC, self.IZX, 6], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 3], [self.ADC, self.ZP0, 3], [self.ROR, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.PLA, self.IMP, 4], [self.ADC, self.IMM, 2], [self.ROR, self.IMP, 2], [self.XXX, self.IMP, 2], [self.JMP, self.IND, 5], [self.ADC, self.ABS, 4], [self.ROR, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BVS, self.REL, 2], [self.ADC, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.ADC, self.ZPX, 4], [self.ROR, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.SEI, self.IMP, 2], [self.ADC, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.ADC, self.ABX, 4], [self.ROR, self.ABX, 7], [self.XXX, self.IMP, 7]],
					   [[self.NOP, self.IMP, 2], [self.STA, self.IZX, 6], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 6], [self.STY, self.ZP0, 3], [self.STA, self.ZP0, 3], [self.STX, self.ZP0, 3], [self.XXX, self.IMP, 3], [self.DEY, self.IMP, 2], [self.NOP, self.IMP, 2], [self.TXA, self.IMP, 2], [self.XXX, self.IMP, 2], [self.STY, self.ABS, 4], [self.STA, self.ABS, 4], [self.STX, self.ABS, 4], [self.XXX, self.IMP, 4]],
					   [[self.BCC, self.REL, 2], [self.STA, self.IZY, 6], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 6], [self.STY, self.ZPX, 4], [self.STA, self.ZPX, 4], [self.STX, self.ZPY, 4], [self.XXX, self.IMP, 4], [self.TYA, self.IMP, 2], [self.STA, self.ABY, 5], [self.TXS, self.IMP, 2], [self.XXX, self.IMP, 5], [self.NOP, self.IMP, 5], [self.STA, self.ABX, 5], [self.XXX, self.IMP, 5], [self.XXX, self.IMP, 5]],
					   [[self.LDY, self.IMM, 2], [self.LDA, self.IZX, 6], [self.LDX, self.IMP, 2], [self.XXX, self.IMP, 6], [self.LDY, self.ZP0, 3], [self.LDA, self.ZP0, 3], [self.LDX, self.ZP0, 3], [self.XXX, self.IMP, 3], [self.TAY, self.IMP, 2], [self.LDA, self.IMM, 2], [self.TAX, self.IMP, 2], [self.XXX, self.IMP, 2], [self.LDY, self.ABS, 4], [self.LDA, self.ABS, 4], [self.LDX, self.ABS, 4], [self.XXX, self.IMP, 4]],
					   [[self.BCS, self.REL, 2], [self.LDA, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 5], [self.LDY, self.ZPX, 4], [self.LDA, self.ZPX, 4], [self.LDX, self.ZPY, 4], [self.XXX, self.IMP, 4], [self.CLV, self.IMP, 2], [self.LDA, self.ABY, 4], [self.TSX, self.IMP, 2], [self.XXX, self.IMP, 4], [self.LDY, self.ABX, 4], [self.LDA, self.ABX, 4], [self.LDX, self.ABY, 4], [self.XXX, self.IMP, 4]],
					   [[self.CPY, self.IMM, 2], [self.CMP, self.IZX, 6], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 8], [self.CPY, self.ZP0, 3], [self.CMP, self.ZP0, 3], [self.DEC, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.INY, self.IMP, 2], [self.CMP, self.IMM, 2], [self.DEX, self.IMP, 2], [self.XXX, self.IMP, 2], [self.CPY, self.ABS, 4], [self.CMP, self.ABS, 4], [self.DEC, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BNE, self.REL, 2], [self.CMP, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.CMP, self.ZPX, 4], [self.DEC, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.CLD, self.IMP, 2], [self.CMP, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.CMP, self.ABX, 4], [self.DEC, self.ABX, 7], [self.XXX, self.IMP, 7]],
					   [[self.CPX, self.IMM, 2], [self.SBC, self.IZX, 6], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 8], [self.CPX, self.ZP0, 3], [self.SBC, self.ZP0, 3], [self.INC, self.ZP0, 5], [self.XXX, self.IMP, 5], [self.INX, self.IMP, 2], [self.SBC, self.IMM, 2], [self.NOP, self.IMP, 2], [self.SBC, self.IMP, 2], [self.CPX, self.ABS, 4], [self.SBC, self.ABS, 4], [self.INC, self.ABS, 6], [self.XXX, self.IMP, 6]],
					   [[self.BEQ, self.REL, 2], [self.SBC, self.IZY, 5], [self.XXX, self.IMP, 2], [self.XXX, self.IMP, 8], [self.NOP, self.IMP, 4], [self.SBC, self.ZPX, 4], [self.INC, self.ZPX, 6], [self.XXX, self.IMP, 6], [self.SED, self.IMP, 2], [self.SBC, self.ABY, 4], [self.NOP, self.IMP, 2], [self.XXX, self.IMP, 7], [self.NOP, self.IMP, 4], [self.SBC, self.ABX, 4], [self.INC, self.ABX, 7], [self.XXX, self.IMP, 7]]]

	def write(self, addr, data):
		self.bus.cpuWrite(addr, data)
	def read(self, addr, readOnly = False):
		self.temp3 = self.bus.cpuRead(addr, readOnly)
		#print("read:", self.temp3)
		return self.temp3
	def setFlag(self, flag, v):
		if v == True:
			self.status = self.status|flag
		else:
			self.status = self.status&(~flag)
	def getFlag(self, flag):
		if (self.status & flag) > 0:
			return 1
		else:
			return 0
	def clock(self):
		if self.cycles == 0:
			self.opcode = self.read(self.pc)
			self.setFlag(flags.U.value, True)
			print("opcode:", self.opcode)
			print("pc:", self.pc)
			self.pc += 1
			self.temp1 = ((self.opcode >> 4) & 0xFF)
			self.temp2 = ((self.opcode) & 0x0F)
			print("opcode pos:", self.temp1, self.temp2)
			print("lookupi tulemus:", self.lookup[self.temp1][self.temp2])
			self.cycles = self.lookup[self.temp1][self.temp2][2]
			self.additional_cycle1 = self.lookup[self.temp1][self.temp2][1]()
			self.additional_cycle2 = self.lookup[self.temp1][self.temp2][0]()
			if self.additional_cycle1 == 1 and self.additional_cycle2 == 1:
				self.cycles += 1
			self.setFlag(flags.U.value, True)
		self.cycles += -1
	def reset(self):
		self.addr_abs = 0xFFFC
		self.lo = self.read(self.addr_abs + 0)
		self.hi = self.read(self.addr_abs + 1)
		self.pc = (self.hi << 8) | self.lo
		self.pc = 0xC004
		print("pc:", self.pc)
		self.a = 0
		self.x = 0
		self.y = 0
		self.stkp = 0xFD
		self.status = 0x00 | flags.U.value
		self.addr_rel = 0x0000
		self.addr_abs = 0x0000
		self.fetched = 0x00
		self.cycles = 8
	def irq(self):
		if getFlag(flags.I.value) == 0:
			write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
			self.stkp += -1
			write(0x0100 + self.stkp, self.pc & 0x00FF)
			self.stkp += -1

			setFlag(flags.B.value, 0)
			setFlag(flags.U.value, 1)
			setFlag(flags.I.value, 1)
			write(0x0100 + self.stkp, self.status)
			self.stkp += -1

			self.addr_abs  = 0xFFFE
			self.lo = read(self.addr_abs + 0)
			self.hi = read(self.addr_abs + 1)
			self.pc = (self.hi << 8) | self.lo

			self.cycles = 7
	def nmi(self):
		write(0x0100 + self.stkp, (self.pc >> 8) & 0x00FF)
		self.stkp += -1
		write(0x0100 + self.stkp, self.pc & 0x00FF)
		self.stkp += -1

		setFlag(flags.B.value, 0)
		setFlag(flags.U.value, 1)
		setFlag(flags.I.value, 1)
		write(0x0100 + self.stkp, self.status)
		self.stkp += -1

		self.addr_abs  = 0xFFFA
		self.lo = read(self.addr_abs + 0)
		self.hi = read(self.addr_abs + 1)
		self.pc = (self.hi << 8) | self.lo

		self.cycles = 8
	def fetch(self):
		#print("fetch opcode:", self.opcode)
		#print(self.fetched)
		self.temp1 = ((self.opcode >> 4) & 0xFF)
		self.temp2 = ((self.opcode) & 0x0F)
		#print("fetch opcode pos:", self.temp1, self.temp2)
		if self.lookup[self.temp1][self.temp2][1] != self.IMP:
			self.fetched = self.read(self.addr_abs)
		return self.fetched

	def connectBus(self, bus):
		self.bus = bus

class flags(Enum):
	C = 1 << 0 #Carry bit
	Z = 1 << 1 #Zero
	I = 1 << 2 #Disable interrupts
	D = 1 << 3 #Decimal mode
	B = 1 << 4 #Break
	U = 1 << 5 #Unused
	V = 1 << 6 #Overflow
	N = 1 << 7 #Negative
