from bus import bus
import time

bus = bus()
bus.insertCartridge("nestest.nes")
bus.reset()

while True:
	bus.clock()
	time.sleep(0.1)
