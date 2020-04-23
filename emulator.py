from bus import bus
import time
import argparse, sys

parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

bus = bus()
bus.insertCartridge(args.filename)
bus.reset()
starttime = 0
clockcycles = 0
while True:
	if clockcycles % 1000 == 0:
		print("1000 clockcycles took (seconds):", round(time.perf_counter() - starttime, 5), "              ", '\x1b[2K\r', end="")
		starttime = time.perf_counter()
	bus.clock()
	clockcycles += 1
	#time.sleep(0.1)
