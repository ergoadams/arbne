from bus import bus
import time

bus = bus()
bus.insertCartridge("tests/nestest.nes")
bus.reset()

#Should get stuck at ~C28F LDA CMP

while True:
	bus.clock()
	#time.sleep(0.1)
