from bus import bus
import time

bus = bus()
bus.insertCartridge("games/smb.nes")
bus.reset()

while True:
	bus.clock()
	#time.sleep(0.1)
