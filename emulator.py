from cpu import cpu, flags
from bus import bus
import time

'''with open('instr_test-v5/official_only.nes', 'rb') as fp:
    ram = bytearray(fp.read())'''
cpuram = bytearray(2048)
print(len(ram))

#ram = bytearray(bytes(64*1024))
cpu = cpu(cpuram)
cpu.connectBus()
cpu.reset()
while True:
	cpu.clock()
	#time.sleep(0.1)
