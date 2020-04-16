from bus import bus
from enum import Enum

class cpu:

	#Addressing modes
	def IMP(self):
		self.fetched = self.a
		return 0
	def IMM(self):
		self.addr_abs = self.pc
		self.pc += 1
		return 0
	def ZP0(self):
		self.addr_abs = self.read(self.pc)
		self.pc += 1
		self.addr_abs = self.addr_abs & 255
		return 0
	def ZPX(self):
		self.addr_abs = self.read(self.pc + self.x)
		self.pc += 1
		self.addr_abs = self.addr_abs & 255
		return 0
	def ZPY(self):
		self.addr_abs = self.read(self.pc + self.y)
		self.pc += 1
		self.addr_abs = self.addr_abs & 255
		return 0
	def REL(self):
		self.addr_rel = self.read(self.pc)
		self.pc += 1
		if self.addr_rel & 128:
			self.addr_rel = self.addr_rel | 65280
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

		if (self.addr_abs & 65280) != (self.hi << 8):
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

		if (self.addr_abs & 65280) != (self.hi << 8):
			return 1
		else:
			return 0
	def IND(self):
		self.ptr_lo = self.read(self.pc)
		self.pc += 1
		self.ptr_hi = self.read(self.pc)
		self.pc += 1

		self.ptr = (self.ptr_hi << 8) | self.ptr_lo

		if self.ptr_lo == 255:
			self.addr_abs = (self.read(self.ptr & 65280) << 8) | self.read(self.ptr + 0)
		else:
			self.addr_abs = (self.read(self.ptr + 1) << 8) | self.read(self.ptr + 0)

		return 0
	def IZX(self):
		self.t = self.read(self.pc)
		self.pc += 1
		self.lo = self.read((self.t + self.x) & 255)
		self.hi = self.read((self.t + self.x + 1) & 255)
		self.addr_abs = (self.hi << 8) | self.lo
		return 0
	def IZY(self):
		self.t = self.read(self.pc, False)
		self.pc += 1
		self.lo = self.read(self.t & 255, False)
		self.hi = self.read((self.t + 1) & 255, False)
		self.addr_abs = (self.hi << 8) | self.lo
		self.addr_abs += self.y

		if (self.addr_abs & 65280) != (self.hi << 8):
			return 1
		else:
			return 0

	#Opcodes
	def ADC(self):
		self.fetch()
		self.temp = self.a + self.fetched + self.getFlag(flags.C.value)
		self.setFlag(flags.C.value, self.temp > 255)
		self.setFlag(flags.Z.value, (self.temp & 255) == 0)
		self.setFlag(flags.N.value, self.temp & 128)
		self.setFlag(flags.V.value, (~(self.a ^ self.fetched) & (self.a ^ self.temp)) & 128)
		self.a = self.temp & 255
		return 1
	def AND(self):
		self.fetch()
		self.a = self.a & self.fetched
		self.setFlag(flags.Z.value, self.a == 0)
		self.setFlag(flags.N.value, self.a & 128)
		return 1
	def ASL(self):
		pass
	def BCC(self):
		if self.getFlag(flags.C.value) == 0:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BCS(self):
		if self.getFlag(flags.C.value) == 1:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BEQ(self):
		if self.getFlag(flags.Z.value) == 1:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BIT(self):
		pass
	def BMI(self):
		if self.getFlag(flags.N.value) == 1:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BNE(self):
		if self.getFlag(flags.Z.value) == 0:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BPL(self):
		if self.getFlag(flags.N.value) == 0:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BRK(self):
		pass
	def BVC(self):
		if self.getFlag(flags.V.value) == 0:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
				self.cycles += 1
			self.pc = self.addr_abs
		return 0
	def BVS(self):
		if self.getFlag(flags.V.value) == 1:
			self.cycles += 1
			self.addr_abs = self.pc + self.addr_rel
			if (self.addr_abs & 65280) != (self.pc & 65280):
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
		pass
	def CPX(self):
		pass
	def CPY(self):
		pass
	def DEC(self):
		pass
	def DEX(self):
		pass
	def DEY(self):
		pass
	def EOR(self):
		pass
	def INC(self):
		pass
	def INX(self):
		pass
	def INY(self):
		pass
	def JMP(self):
		pass
	def JSR(self):
		pass
	def LDA(self):
		pass
	def LDX(self):
		pass
	def LDY(self):
		pass
	def LSR(self):
		pass
	def NOP(self):
		pass
	def ORA(self):
		self.fetch()
		self.a = self.a | self.fetched
		self.setFlag(flags.Z.value, self.a == 0)
		self.setFlag(flags.N.value, self.a & 128)
		return 1
	def PHA(self):
		write(256 + self.stkp, self.a)
		self.stkp += -1
		return 0
	def PHP(self):
		pass
	def PLA(self):
		self.stkp += 1
		self.a = read(256 + self.stkp)
		setFlag(flags.Z.value, self.a == 0)
		setFlag(flags.N.value, self.a & 128)
		return 0
	def PLP(self):
		pass
	def ROL(self):
		pass
	def ROR(self):
		pass
	def RTI(self):
		self.stkp += 1
		self.status = self.read(256 + self.stkp)
		self.status = self.status & ~flags.B.value
		self.status = self.status & ~flags.U.value
		self.stkp += 1
		self.pc = self.read(256 + self.stkp)
		self.stkp += 1
		self.pc = self.pc | self.read(256 + self.stkp) << 8
		return 0
	def RTS(self):
		pass
	def SBC(self):
		self.fetch()
		self.value = self.fetched ^ 255
		self.temp = self.a + self.value + self.getFlag(flags.C.value)
		self.setFlag(flags.C.value, self.temp & 65280)
		self.setFlag(flags.Z.value, (self.temp & 255) == 0)
		self.setFlag(flags.N.value, self.temp & 128)
		self.setFlag(flags.V.value, (self.temp ^ self.a) & (self.temp ^ self.value) & 128)
		self.a = self.temp & 255
		return 1
	def SEC(self):
		pass
	def SED(self):
		pass
	def SEI(self):
		pass
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
		pass
	def TAY(self):
		pass
	def TSX(self):
		pass
	def TXA(self):
		pass
	def TXS(self):
		pass
	def TYA(self):
		pass

	def XXX(self):
		pass

	def __init__(self, ram):
		self.ram = ram         #Passing RAM to the cpu
		self.a = 0             #Accumulator register
		self.x = 0             #X register
		self.y = 0             #Y register
		self.stkp = 0          #Stack pointer (points to location on bus)
		self.pc = 0            #Program counter
		self.status = 0  #Status register

		self.fetched = 0 #Fetched data

		self.addr_abs = 0
		self.addr_rel =  0
		self.opcode =  0
		self.cycles = 0

		#VAJA LÕPETADA
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

	def connectBus(self):
		self.bus = bus(self.ram)

	def write(self, addr, data):
		self.bus.write(addr, data)

	def read(self, addr, readOnly=False):
		return self.bus.read(addr, readOnly)

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
			self.opcode = self.read(self.pc, False)
			self.pc += 1
			self.temp1 = ((self.opcode >> 4) & 255) - 1
			self.temp2 = ((self.opcode) & 15) - 1
			print("opcode pos:", self.temp1, self.temp2)
			print("lookupi tulemus:", self.lookup[self.temp1][self.temp2])
			self.cycles = self.lookup[self.temp1][self.temp2][2]
			self.additional_cycle1 = self.lookup[self.temp1][self.temp2][1]()
			self.additional_cycle2 = self.lookup[self.temp1][self.temp2][0]()
			if self.additional_cycle1 == 1 and self.additional_cycle2 == 1:
				self.cycles += 1
		self.cycles += -1

	def reset(self):
		self.addr_abs = 65532
		self.lo = self.read(self.addr_abs + 0)
		self.hi = self.read(self.addr_abs + 1)
		self.pc = (self.hi << 8) | self.lo
		self.a = 0
		self.x = 0
		self.y = 0
		self.stkp = 253
		self.addr_rel = 0
		self.addr_abs = 0
		self.fetched = 0
		self.cycles = 8

	def irq(self):
		if getFlag(flags.I.value) == 0:
			write(256 + self.stkp, (self.pc >> 8) & 255)
			self.stkp += -1
			write(256 + self.stkp, self.pc & 255)
			self.stkp += -1

			setFlag(flags.B.value, 0)
			setFlag(flags.U.value, 1)
			setFlag(flags.I.value, 1)
			write(256 + self.stkp, self.status)
			self.stkp += -1

			self.addr_abs  = 65534
			self.lo = read(self.addr_abs + 0)
			self.hi = read(self.addr_abs + 1)
			self.pc = (self.hi << 8) | self.lo

			self.cycles = 7
	def nmi(self):
		write(b'\x01\x00' + self.stkp, (self.pc >> 8) & b'\x00\xFF')
		self.stkp += -1
		write(b'\x01\x00' + self.stkp, self.pc & b'\x00\xFF')
		self.stkp += -1

		setFlag(flags.B.value, 0)
		setFlag(flags.U.value, 1)
		setFlag(flags.I.value, 1)
		write(b'\x01\x00' + self.stkp, self.status)
		self.stkp += -1

		self.addr_abs  = b'\xFF\xFA'
		self.lo = read(self.addr_abs + 0)
		self.hi = read(self.addr_abs + 1)
		self.pc = (self.hi << 8) | self.lo

		self.cycles = 8

	def fetch(self):
		self.temp1 = ((self.opcode >> 4) & 255) - 1
		self.temp2 = ((self.opcode) & 15) - 1
		if self.lookup[self.temp1][self.temp2][1] != self.IMP:
			self.fetched = self.read(self.addr_abs)
		return self.fetched

	#mingi stuct INSTRUCTION
	#string name
	#operation function pointer
	#addrmode function pointer
	#cycles

	#peaks olema kõik siis mingis listis paneb dictionarysse

class flags(Enum):
	C = 1 << 0 #Carry bit
	Z = 1 << 1 #Zero
	I = 1 << 2 #Disable interrupts
	D = 1 << 3 #Decimal mode
	B = 1 << 4 #Break
	U = 1 << 5 #Unused
	V = 1 << 6 #Overflow
	N = 1 << 7 #Negative
