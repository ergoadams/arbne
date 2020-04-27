from bus import bus
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

bus = bus()
bus.insertCartridge(args.filename)
bus.reset()
clockcycles = 0
starttime = time.perf_counter()
running = True
while bus.ppu.running and running:
	bus.clock()
	clockcycles += 1
	if time.perf_counter() - starttime > 20:
		running = False
print("\n")
print(bus.ppu.framecount)
