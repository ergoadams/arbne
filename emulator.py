from cpu import cpu, flags
from bus import bus
import time

with open('instr_test-v5/official_only.nes', 'rb') as fp:
    ram = bytearray(fp.read())
print(len(ram))
#ram[65532] = 0 #reset?
#ram[65533] = 128

#ram = bytearray(bytes(64*1024))
cpu = cpu(ram)
cpu.connectBus()
#cpu.reset()
while True:
	cpu.clock()
	#time.sleep(0.01)
