class cpu:
    def fetch(self):
        if self.addressmode != self.IMP:
            self.fetched = self.read(self.addr_abs & 0xFFFF)
        return self.fetched

    #Addressing modes
    def IMP(self):
        self.fetched = self.a
        return 0
    def IMM(self):
        self.addr_abs = self.pc
        self.pc += 1
        return 0
    def ZP0(self):
        self.addr_abs = self.read(self.pc) & 0xFF
        self.pc += 1
        return 0
    def ZPX(self):
        self.addr_abs = (self.read(self.pc)  + self.x) & 0xFF
        self.pc += 1
        return 0
    def ZPY(self):
        self.addr_abs = (self.read(self.pc) + self.y) & 0xFF
        self.pc += 1
        return 0
    def REL(self):
        self.addr_rel = self.read(self.pc)
        self.addr_rel = self.addr_rel if self.addr_rel < 0x80 else self.addr_rel - 0x100
        self.pc += 1
        return 0
    def ABS(self):
        self.addr_abs = (self.read(self.pc + 1) << 8) | self.read(self.pc)
        self.pc += 2
        return 0
    def ABX(self):
        self.hi = self.read(self.pc + 1)
        self.addr_abs = ((self.hi << 8) | self.read(self.pc)) + self.x
        self.pc += 2
        return 1 if (self.addr_abs & 0xFF00) != (self.hi << 8) else 0
    def ABY(self):
        self.hi = self.read(self.pc + 1)
        self.addr_abs = ((self.hi << 8) | self.read(self.pc)) + self.y
        self.pc += 2
        return 1 if (self.addr_abs & 0xFF00) != (self.hi << 8) else 0
    def IND(self):
        self.ptr_lo = self.read(self.pc)
        self.ptr = (self.read(self.pc + 1) << 8) | self.ptr_lo
        self.addr_abs = (self.read(self.ptr & 0xFF00) << 8) | self.read(self.ptr) if self.ptr_lo == 0xFF else (self.read(self.ptr + 1) << 8) | self.read(self.ptr)
        self.pc += 2
        return 0
    def IZX(self):
        self.t = self.read(self.pc)
        self.pc += 1
        self.addr_abs = (self.read((self.t + self.x + 1) & 0x00FF) << 8) | self.read((self.t + self.x) & 0x00FF)
        return 0
    def IZY(self):
        self.t = self.read(self.pc)
        self.pc += 1
        self.hi = self.read((self.t + 1) & 0x00FF) << 8
        self.addr_abs = (self.hi | self.read(self.t & 0x00FF)) + self.y
        return 1 if (self.addr_abs & 0xFF00) != (self.hi << 8) else 0

    #Opcodes
    def ADC(self):
        self.fetch()
        self.temp = self.a + self.fetched + self.flagC
        self.flagC = 1 if self.temp > 255 else 0
        self.flagZ = 1 if not (self.temp & 0x00FF) else 0
        self.flagV = 1 if (~(self.a ^ self.fetched) & (self.a ^ self.temp)) & 0x80 else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        self.a = self.temp & 0x00FF
        return 1
    def AND(self):
        self.fetch()
        self.a &= self.fetched
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 1
    def ASL(self):
        self.fetch()
        self.temp = self.fetched << 1
        self.flagC = 1 if (self.temp & 0xFF00) else 0
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        if self.addressmode == self.IMP:
            self.a = self.temp & 0x00FF
        else:
            self.write(self.addr_abs, self.temp & 0xFF)
        return 0
    def BCC(self):
        if not self.flagC:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BCS(self):
        if self.flagC:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BEQ(self):
        if self.flagZ:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BIT(self):
        self.fetch()
        self.flagZ = 1 if not (self.a & self.fetched & 0xFF) else 0
        self.flagN = 1 if self.fetched & (1 << 7) else 0
        self.flagV = 1 if self.fetched & (1 << 6) else 0
        return 0
    def BMI(self):
        if self.flagN:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BNE(self):
        if not self.flagZ:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BPL(self):
        if not self.flagN:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BRK(self):
        self.flagI = 1
        self.write(0x0100 + self.stkp, ((self.pc + 1) >> 8) & 0xFF)
        self.write(0x0100 + self.stkp - 1, (self.pc + 1) & 0xFF)
        self.flagB = 1
        self.status = self.flagC | (self.flagZ << 1) | (self.flagI << 2) | (self.flagD << 3) | (self.flagB << 4) | (self.flagU << 5) | (self.flagV << 6) | (self.flagN << 7)
        self.write(0x0100 + self.stkp - 2, self.status)
        self.stkp += -3
        self.flagI = 0
        self.pc = self.read(0xFFFE) | (self.read(0xFFFF) << 8)
    def BVC(self):
        if not self.flagV:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def BVS(self):
        if self.flagV:
            self.addr_abs = self.pc + self.addr_rel
            self.cycles += 2 if (self.addr_abs & 0xFF00) != (self.pc & 0xFF00) else 1
            self.pc = self.addr_abs
        return 0
    def CLC(self):
        self.flagC = 0
        return 0
    def CLD(self):
        self.flagD = 0
        return 0
    def CLI(self):
        self.flagI = 0
        return 0
    def CLV(self):
        self.flagV = 0
        return 0
    def CMP(self):
        self.fetch()
        self.temp = self.a - self.fetched
        self.flagC = 1 if self.a >= self.fetched else 0
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        return 1
    def CPX(self):
        self.fetch()
        self.temp = self.x - self.fetched
        self.flagC = 1 if self.x >= self.fetched else 0
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        return 0
    def CPY(self):
        self.fetch()
        self.temp = self.y - self.fetched
        self.flagC = 1 if self.y >= self.fetched else 0
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        return 0
    def DEC(self):
        self.fetch()
        self.temp = self.fetched - 1
        self.write(self.addr_abs, self.temp & 0x00FF)
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        return 0
    def DEX(self):
        self.x = (self.x - 1) & 0xFF
        self.flagZ = 1 if not self.x else 0
        self.flagN = 1 if self.x & 0x80 else 0
        return 0
    def DEY(self):
        self.y = (self.y - 1) & 0xFF
        self.flagZ = 1 if not self.y else 0
        self.flagN = 1 if self.y & 0x80 else 0
        return 0
    def EOR(self):
        self.fetch()
        self.a ^= self.fetched
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 1
    def INC(self):
        self.fetch()
        self.temp = (self.fetched + 1) & 0xFF
        self.write(self.addr_abs, self.temp)
        self.flagZ = 1 if not (self.temp & 0xFF) else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        return 0
    def INX(self):
        self.x = (self.x + 1) & 0xFF
        self.flagZ = 1 if not self.x else 0
        self.flagN = 1 if self.x & 0x80 else 0
        return 0
    def INY(self):
        self.y = (self.y + 1) & 0xFF
        self.flagZ = 1 if not self.y else 0
        self.flagN = 1 if self.y & 0x80 else 0
        return 0
    def JMP(self):
        self.pc = self.addr_abs
        return 0
    def JSR(self):
        self.write(0x0100 + self.stkp, (self.pc - 1) >> 8)
        self.write(0x0100 + self.stkp - 1, self.pc - 1)
        self.stkp += -2
        self.pc = self.addr_abs
        return 0
    def LDA(self):
        self.a = self.fetch()
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 1
    def LDX(self):
        self.x = self.fetch()
        self.flagZ = 1 if not self.x else 0
        self.flagN = 1 if self.x & 0x80 else 0
        return 1
    def LDY(self):
        self.y = self.fetch()
        self.flagZ = 1 if not self.y else 0
        self.flagN = 1 if self.y & 0x80 else 0
        return 1
    def LSR(self):
        self.fetch()
        self.flagC = 1 if self.fetched & 0x01 else 0
        self.temp =  (self.fetched >> 1) & 0xFF
        self.flagZ = 1 if not self.temp else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        if self.addressmode == self.IMP:
            self.a = self.temp
        else:
            self.write(self.addr_abs, self.temp)
        return 0
    def NOP(self):
        if self.opcode == 0xFC:
            return 1
        elif self.opcode == 0x1C:
            pass
        elif self.opcode == 0x3C:
            pass
        elif self.opcode == 0x5C:
            pass
        elif self.opcode == 0x7C:
            pass
        elif self.opcode == 0xDC:
            pass
        return 0
    def ORA(self):
        self.fetch()
        self.a |= self.fetched
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 1
    def PHA(self):
        self.write(0x0100 + self.stkp, self.a)
        self.stkp -= 1
        return 0
    def PHP(self):
        self.status = self.flagC | (self.flagZ << 1) | (self.flagI << 2) | (self.flagD << 3) | (1 << 4) | (1 << 5) | (self.flagV << 6) | (self.flagN << 7)
        self.write(0x0100 + self.stkp, self.status)
        self.flagB = 0
        self.flagU = 0
        self.stkp -= 1
        return 0
    def PLA(self):
        self.stkp += 1
        self.a = self.read(0x0100 + self.stkp)
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 0
    def PLP(self):
        self.stkp += 1
        self.status = self.read(0x0100 + self.stkp)
        self.flagC = self.status & 0b1
        self.flagZ = (self.status & 0b10) >> 1
        self.flagI = (self.status & 0b100) >> 2
        self.flagD = (self.status & 0b1000) >> 3
        self.flagB = (self.status & 0b10000) >> 4
        self.flagU = 1
        self.flagV = (self.status & 0b1000000) >> 6
        self.flagN = (self.status & 0b10000000) >> 7
        return 0
    def ROL(self):
        self.fetch()
        self.temp = (self.fetched << 1) | self.flagC
        self.flagC = 1 if self.temp & 0xFF00 else 0
        self.temp &= 0xFF
        self.flagZ = 1 if not self.temp else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        if self.addressmode == self.IMP:
            self.a = self.temp
        else:
            self.write(self.addr_abs, self.temp)
        return 0
    def ROR(self):
        self.fetch()
        self.temp = (self.flagC << 7) | (self.fetched >> 1)
        self.flagC = 1 if self.fetched & 0x01 else 0
        self.temp &= 0xFF
        self.flagZ = 1 if not self.temp else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        if self.addressmode == self.IMP:
            self.a = self.temp
        else:
            self.write(self.addr_abs, self.temp)
        return 0
    def RTI(self):
        self.tempaddr = 0x0101 + self.stkp
        self.status = self.read(self.tempaddr)
        self.flagC = self.status & 0b1
        self.flagZ = (self.status & 0b10) >> 1
        self.flagI = (self.status & 0b100) >> 2
        self.flagD = (self.status & 0b1000) >> 3
        self.flagB = 0
        self.flagU = 0
        self.flagV = (self.status & 0b1000000) >> 6
        self.flagN = (self.status & 0b10000000) >> 7
        self.pc = self.read(self.tempaddr + 1) | (self.read(self.tempaddr + 2) << 8)
        self.stkp += 3
        return 0
    def RTS(self):
        self.stkp += 2
        self.tempaddr = 0x0100 + self.stkp
        self.pc = (self.read(self.tempaddr - 1) | (self.read(self.tempaddr) << 8)) + 1
        return 0
    def SBC(self):
        self.value = self.fetch() ^ 0xFF
        self.temp = self.a + self.value + self.flagC
        self.flagC = 1 if self.temp & 0xFF00 else 0
        self.flagV = 1 if (self.temp ^ self.a) & (self.temp ^ self.value) & 0x80 else 0
        self.temp &= 0xFF
        self.flagZ = 1 if not self.temp else 0
        self.flagN = 1 if self.temp & 0x80 else 0
        self.a = self.temp
        return 1
    def SEC(self):
        self.flagC = 1
        return 0
    def SED(self):
        self.flagD = 1
        return 0
    def SEI(self):
        self.flagI = 1
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
        self.flagZ = 1 if not self.x else 0
        self.flagN = 1 if self.x & 0x80 else 0
        return 0
    def TAY(self):
        self.y = self.a
        self.flagZ = 1 if not self.y else 0
        self.flagN = 1 if self.y & 0x80 else 0
        return 0
    def TSX(self):
        self.x = self.stkp
        self.flagZ = 1 if not self.x else 0
        self.flagN = 1 if self.x & 0x80 else 0
        return 0
    def TXA(self):
        self.a = self.x
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 0
    def TXS(self):
        self.stkp = self.x
        return 0
    def TYA(self):
        self.a = self.y
        self.flagZ = 1 if not self.a else 0
        self.flagN = 1 if self.a & 0x80 else 0
        return 0
    def XXX(self):
        return 0

    def __init__(self, bus):
        self.cpuram = [0] * 2048
        self.bus = bus
        self.a = 0
        self.x = 0
        self.y = 0
        self.stkp = 0
        self.pc = 0
        self.status = 0
        self.fetched = 0
        self.addr_abs = 0
        self.addr_rel = 0
        self.opcode = 0
        self.cycles = 0
        self.clock_count = 0
        self.lookup = {
                     0: (self.BRK, self.IMM, 7),   1: (self.ORA, self.IZX, 6),   2: (self.XXX, self.IMP, 2),   3: (self.XXX, self.IMP, 8),   4: (self.NOP, self.IMP, 3),   5: (self.ORA, self.ZP0, 3),   6: (self.ASL, self.ZP0, 5),   7: (self.XXX, self.IMP, 5),   8: (self.PHP, self.IMP, 3),   9: (self.ORA, self.IMM, 2),   10: (self.ASL, self.IMP, 2),  11: (self.XXX, self.IMP, 2),  12: (self.NOP, self.IMP, 4),  13: (self.ORA, self.ABS, 4), 14: (self.ASL, self.ABS, 6), 15: (self.XXX, self.IMP, 6),
                  16: (self.BPL, self.REL, 2),  17: (self.ORA, self.IZY, 5),  18: (self.XXX, self.IMP, 2),  19: (self.XXX, self.IMP, 8),  20: (self.NOP, self.IMP, 4),  21: (self.ORA, self.ZPX, 4),  22: (self.ASL, self.ZPX, 6),  23: (self.XXX, self.IMP, 6),  24: (self.CLC, self.IMP, 2),  25: (self.ORA, self.ABY, 4),  26: (self.NOP, self.IMP, 2),  27: (self.XXX, self.IMP, 7),  28: (self.NOP, self.IMP, 4),  29: (self.ORA, self.ABX, 4), 30: (self.ASL, self.ABX, 7), 31: (self.XXX, self.IMP, 7),
                  32: (self.JSR, self.ABS, 6),  33: (self.AND, self.IZX, 6),  34: (self.XXX, self.IMP, 2),  35: (self.XXX, self.IMP, 8),  36: (self.BIT, self.ZP0, 3),  37: (self.AND, self.ZP0, 3),  38: (self.ROL, self.ZP0, 5),  39: (self.XXX, self.IMP, 5),  40: (self.PLP, self.IMP, 4),  41: (self.AND, self.IMM, 2),  42: (self.ROL, self.IMP, 2),  43: (self.XXX, self.IMP, 2),  44: (self.BIT, self.ABS, 4),  45: (self.AND, self.ABS, 4), 46: (self.ROL, self.ABS, 6), 47: (self.XXX, self.IMP, 6),
                  48: (self.BMI, self.REL, 2),  49: (self.AND, self.IZY, 5),  50: (self.XXX, self.IMP, 2),  51: (self.XXX, self.IMP, 8),  52: (self.NOP, self.IMP, 4),  53: (self.AND, self.ZPX, 4),  54: (self.ROL, self.ZPX, 6),  55: (self.XXX, self.IMP, 6),  56: (self.SEC, self.IMP, 2),  57: (self.AND, self.ABY, 4),  58: (self.NOP, self.IMP, 2),  59: (self.XXX, self.IMP, 7),  60: (self.NOP, self.IMP, 4),  61: (self.AND, self.ABX, 4), 62: (self.ROL, self.ABX, 7), 63: (self.XXX, self.IMP, 7),
                  64: (self.RTI, self.IMP, 6),  65: (self.EOR, self.IZX, 6),  66: (self.XXX, self.IMP, 2),  67: (self.XXX, self.IMP, 8),  68: (self.NOP, self.IMP, 3),  69: (self.EOR, self.ZP0, 3),  70: (self.LSR, self.ZP0, 5),  71: (self.XXX, self.IMP, 5),  72: (self.PHA, self.IMP, 3),  73: (self.EOR, self.IMM, 2),  74: (self.LSR, self.IMP, 2),  75: (self.XXX, self.IMP, 2),  76: (self.JMP, self.ABS, 3),  77: (self.EOR, self.ABS, 4), 78: (self.LSR, self.ABS, 6), 79: (self.XXX, self.IMP, 6),
                  80: (self.BVC, self.REL, 2),  81: (self.EOR, self.IZY, 5),  82: (self.XXX, self.IMP, 2),  83: (self.XXX, self.IMP, 8),  84: (self.NOP, self.IMP, 4),  85: (self.EOR, self.ZPX, 4),  86: (self.LSR, self.ZPX, 6),  87: (self.XXX, self.IMP, 6),  88: (self.CLI, self.IMP, 2),  89: (self.EOR, self.ABY, 4),  90: (self.NOP, self.IMP, 2),  91: (self.XXX, self.IMP, 7),  92: (self.NOP, self.IMP, 4),  93: (self.EOR, self.ABX, 4), 94: (self.LSR, self.ABX, 7), 95: (self.XXX, self.IMP, 7),
                  96: (self.RTS, self.IMP, 6),  97: (self.ADC, self.IZX, 6),  98: (self.XXX, self.IMP, 2),  99: (self.XXX, self.IMP, 8),  100: (self.NOP, self.IMP, 3), 101: (self.ADC, self.ZP0, 3), 102: (self.ROR, self.ZP0, 5), 103: (self.XXX, self.IMP, 5), 104: (self.PLA, self.IMP, 4), 105: (self.ADC, self.IMM, 2), 106: (self.ROR, self.IMP, 2), 107: (self.XXX, self.IMP, 2), 108: (self.JMP, self.IND, 5), 109: (self.ADC, self.ABS, 4), 110: (self.ROR, self.ABS, 6), 111: (self.XXX, self.IMP, 6),
                  112: (self.BVS, self.REL, 2), 113: (self.ADC, self.IZY, 5), 114: (self.XXX, self.IMP, 2), 115: (self.XXX, self.IMP, 8), 116: (self.NOP, self.IMP, 4), 117: (self.ADC, self.ZPX, 4), 118: (self.ROR, self.ZPX, 6), 119: (self.XXX, self.IMP, 6), 120: (self.SEI, self.IMP, 2), 121: (self.ADC, self.ABY, 4), 122: (self.NOP, self.IMP, 2), 123: (self.XXX, self.IMP, 7), 124: (self.NOP, self.IMP, 4), 125: (self.ADC, self.ABX, 4), 126: (self.ROR, self.ABX, 7), 127: (self.XXX, self.IMP, 7),
                  128: (self.NOP, self.IMP, 2), 129: (self.STA, self.IZX, 6), 130: (self.NOP, self.IMP, 2), 131: (self.XXX, self.IMP, 6), 132: (self.STY, self.ZP0, 3), 133: (self.STA, self.ZP0, 3), 134: (self.STX, self.ZP0, 3), 135: (self.XXX, self.IMP, 3), 136: (self.DEY, self.IMP, 2), 137: (self.NOP, self.IMP, 2), 138: (self.TXA, self.IMP, 2), 139: (self.XXX, self.IMP, 2), 140: (self.STY, self.ABS, 4), 141: (self.STA, self.ABS, 4), 142: (self.STX, self.ABS, 4), 143: (self.XXX, self.IMP, 4),
                  144: (self.BCC, self.REL, 2), 145: (self.STA, self.IZY, 6), 146: (self.XXX, self.IMP, 2), 147: (self.XXX, self.IMP, 6), 148: (self.STY, self.ZPX, 4), 149: (self.STA, self.ZPX, 4), 150: (self.STX, self.ZPY, 4), 151: (self.XXX, self.IMP, 4), 152: (self.TYA, self.IMP, 2), 153: (self.STA, self.ABY, 5), 154: (self.TXS, self.IMP, 2), 155: (self.XXX, self.IMP, 5), 156: (self.NOP, self.IMP, 5), 157: (self.STA, self.ABX, 5), 158: (self.XXX, self.IMP, 5), 159: (self.XXX, self.IMP, 5),
                  160: (self.LDY, self.IMM, 2), 161: (self.LDA, self.IZX, 6), 162: (self.LDX, self.IMM, 2), 163: (self.XXX, self.IMP, 6), 164: (self.LDY, self.ZP0, 3), 165: (self.LDA, self.ZP0, 3), 166: (self.LDX, self.ZP0, 3), 167: (self.XXX, self.IMP, 3), 168: (self.TAY, self.IMP, 2), 169: (self.LDA, self.IMM, 2), 170: (self.TAX, self.IMP, 2), 171: (self.XXX, self.IMP, 2), 172: (self.LDY, self.ABS, 4), 173: (self.LDA, self.ABS, 4), 174: (self.LDX, self.ABS, 4), 175: (self.XXX, self.IMP, 4),
                  176: (self.BCS, self.REL, 2), 177: (self.LDA, self.IZY, 5), 178: (self.XXX, self.IMP, 2), 179: (self.XXX, self.IMP, 5), 180: (self.LDY, self.ZPX, 4), 181: (self.LDA, self.ZPX, 4), 182: (self.LDX, self.ZPY, 4), 183: (self.XXX, self.IMP, 4), 184: (self.CLV, self.IMP, 2), 185: (self.LDA, self.ABY, 4), 186: (self.TSX, self.IMP, 2), 187: (self.XXX, self.IMP, 4), 188: (self.LDY, self.ABX, 4), 189: (self.LDA, self.ABX, 4), 190: (self.LDX, self.ABY, 4), 191: (self.XXX, self.IMP, 4),
                  192: (self.CPY, self.IMM, 2), 193: (self.CMP, self.IZX, 6), 194: (self.NOP, self.IMP, 2), 195: (self.XXX, self.IMP, 8), 196: (self.CPY, self.ZP0, 3), 197: (self.CMP, self.ZP0, 3), 198: (self.DEC, self.ZP0, 5), 199: (self.XXX, self.IMP, 5), 200: (self.INY, self.IMP, 2), 201: (self.CMP, self.IMM, 2), 202: (self.DEX, self.IMP, 2), 203: (self.XXX, self.IMP, 2), 204: (self.CPY, self.ABS, 4), 205: (self.CMP, self.ABS, 4), 206: (self.DEC, self.ABS, 6), 207: (self.XXX, self.IMP, 6),
                  208: (self.BNE, self.REL, 2), 209: (self.CMP, self.IZY, 5), 210: (self.XXX, self.IMP, 2), 211: (self.XXX, self.IMP, 8), 212: (self.NOP, self.IMP, 4), 213: (self.CMP, self.ZPX, 4), 214: (self.DEC, self.ZPX, 6), 215: (self.XXX, self.IMP, 6), 216: (self.CLD, self.IMP, 2), 217: (self.CMP, self.ABY, 4), 218: (self.NOP, self.IMP, 2), 219: (self.XXX, self.IMP, 7), 220: (self.NOP, self.IMP, 4), 221: (self.CMP, self.ABX, 4), 222: (self.DEC, self.ABX, 7), 223: (self.XXX, self.IMP, 7),
                  224: (self.CPX, self.IMM, 2), 225: (self.SBC, self.IZX, 6), 226: (self.NOP, self.IMP, 2), 227: (self.XXX, self.IMP, 8), 228: (self.CPX, self.ZP0, 3), 229: (self.SBC, self.ZP0, 3), 230: (self.INC, self.ZP0, 5), 231: (self.XXX, self.IMP, 5), 232: (self.INX, self.IMP, 2), 233: (self.SBC, self.IMM, 2), 234: (self.NOP, self.IMP, 2), 235: (self.SBC, self.IMP, 2), 236: (self.CPX, self.ABS, 4), 237: (self.SBC, self.ABS, 4), 238: (self.INC, self.ABS, 6), 239: (self.XXX, self.IMP, 6),
                  240: (self.BEQ, self.REL, 2), 241: (self.SBC, self.IZY, 5), 242: (self.XXX, self.IMP, 2), 243: (self.XXX, self.IMP, 8), 244: (self.NOP, self.IMP, 4), 245: (self.SBC, self.ZPX, 4), 246: (self.INC, self.ZPX, 6), 247: (self.XXX, self.IMP, 6), 248: (self.SED, self.IMP, 2), 249: (self.SBC, self.ABY, 4), 250: (self.NOP, self.IMP, 2), 251: (self.XXX, self.IMP, 7), 252: (self.NOP, self.IMP, 4), 253: (self.SBC, self.ABX, 4), 254: (self.INC, self.ABX, 7), 255: (self.XXX, self.IMP, 7)
                 }

        self.flagC = 0 # 1 << 0
        self.flagZ = 0 # 1 << 1 #Zero
        self.flagI = 0 # 1 << 2 #Disable interrupts
        self.flagD = 0 # 1 << 3 #Decimal mode
        self.flagB = 0 # 1 << 4 #Break
        self.flagU = 0 # 1 << 5 #Unused
        self.flagV = 0 # 1 << 6 #Overflow
        self.flagN = 0 # 1 << 7 #Negative

    def write(self, addr, data):
        self.bus.cpuWrite(addr, data)
    def read(self, addr, readOnly = False):
        return self.bus.cpuRead(addr, readOnly)
    def clock(self):
        if not self.cycles:
            self.opcode = self.read(self.pc)
            self.pc += 1
            self.cycles = self.lookup[self.opcode][2]
            self.addressmode = self.lookup[self.opcode][1]
            self.additional_cycle1 = self.addressmode()
            self.additional_cycle2 = self.lookup[self.opcode][0]()
            if self.additional_cycle1 and self.additional_cycle2:
                self.cycles += 1
        self.cycles -= 1
    def reset(self):
        self.addr_abs = 0xFFFC
        self.pc = (self.read(0xFFFD) << 8) | self.read(0xFFFC)
        self.a = self.x = self.y = 0
        self.stkp = 0xFD
        self.status = 1 << 5
        self.flagC = 0
        self.flagZ = 0
        self.flagI = 0
        self.flagD = 0
        self.flagB = 0
        self.flagU = 1
        self.flagV = 0
        self.flagN = 0
        self.addr_rel = self.addr_abs = self.fetched = 0
        self.cycles = 8
    def irq(self):
        if not self.flagI:
            self.tempaddr = 0x0100 + self.stkp
            self.write(self.tempaddr, self.pc >> 8)
            self.write(self.tempaddr - 1, self.pc)
            self.status = self.flagC | (self.flagZ << 1) | (self.flagI << 2) | (self.flagD << 3) | (self.flagB << 4) | (self.flagU << 5) | (self.flagV << 6) | (self.flagN << 7)
            self.write(self.tempaddr - 2, self.status)
            self.stkp -= 3
            self.flagB = 0
            self.flagU = 1
            self.flagI = 1
            self.addr_abs = 0xFFFE
            self.pc = (self.read(0xFFFF) << 8) | self.read(0xFFFE)
            self.cycles = 7
    def nmi(self):
        self.tempaddr = 0x0100 + self.stkp
        self.write(self.tempaddr, self.pc >> 8)
        self.write(self.tempaddr - 1, self.pc)
        self.flagB = 0
        self.flagU = 1
        self.flagI = 1
        self.status = self.flagC | (self.flagZ << 1) | (self.flagI << 2) | (self.flagD << 3) | (self.flagB << 4) | (self.flagU << 5) | (self.flagV << 6) | (self.flagN << 7)
        self.write(self.tempaddr - 2, self.status)
        self.stkp -= 3
        self.addr_abs = 0xFFFA
        self.pc = (self.read(0xFFFB) << 8) | self.read(0xFFFA)
        self.cycles = 8
