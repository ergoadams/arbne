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
while bus.ppu.running:
	bus.clock()
	clockcycles += 1
