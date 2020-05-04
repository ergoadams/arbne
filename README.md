# A Really Bad NES Emulator (ARBNE)
A Python based NES emulator attempt.

## TODO
- [x] Finish operations
- [x] PPU, ROM, RAM, mappers
- [x] Check, if operations are working
- [ ] Fix test_cpu_exec_space_ppuio errors (test_cpu_exec_space_ppuio.nes)
- [ ] Fix sprite_ram DMA copy issues (sprite_ram.nes)
- [ ] Fix vbl flag cleared too late issue (vbl_clear_time.nes)
- [x] Fix VRAM reads should be delayed in a buffer issue (vram_access.nes)
- [ ] PPU open bus issues (ppu_open_bus.nes)
- [x] Check background rendering and zero hit (smb is not rendering correctly)
- [ ] Zerohit on the bottom (Y = 255), double height lower sprite tile should hit bottom of bg tile
- [ ] Optimize, optimize, optimize...
- [x] Lookup table

## Things to optimize (data is based on the emulator running for 20 seconds, originally about 11 frames)
Biggest problems right now are bus cpuWrite, cpu ABS, LDA, CMP, REL, ZP0, fetch and ppu ppuRead  
We got to 1 fps! Now need to get it only 60 times faster...

| Function                   | original cumulative time | optimized time? | number of calls | calls to time ratio |
| -------------------------- | ------------------------ | --------------- | --------------- | ------------------- |
| bus clock (calling others) | 18.99                    | 18.45           | 1435702         | 12.85               |
| bus cpuWrite               | 0.090                    | 0.078           | 6303            | 12.37               |
| bus cpuRead                | 0.875                    | 0.921           | 389738          | 2.363               |
| cartridge cpuRead          | 0.515                    | 0.545           | 389738          | 1.398               |
| cartridge ppuRead          | 1.265                    | 0.603           | 540710          | 1.115               |
| cpu clock (all cpu things) | 2.267                    | 2.757           | 491636          | 5.607               |
| cpu BEQ                    | 0.179                    | 0.065           | 67088           | 0.968               |
| cpu CMP                    | 0.625                    | 0.353           | 66671           | 5.294               |
| cpu ZP0                    | 0.194                    | 0.194           | 59066           | 3.284               |
| cpu LDA                    | 0.108                    | 0.059           | 9596            | 6.148               |
| cpu REL                    | 0.190                    | 0.264           | 74446           | 3.546               |
| cpu ABS                    | 0.144                    | 0.099           | 14370           | 6.889               |
| cpu read                   | 0.755                    | 1.063           | 389738          | 2.727               |
| cpu setFlag                | 0.144                    | 0               | 0               | 0                   |
| cpu fetch                  | 0.194                    | 0.264           | 69243           | 3.812               |
| mapper cpuMapRead          | 0.128                    | 0.143           | 389738          | 0.366               |
| mapper ppuMapRead          | 0.262                    | 0.216           | 540710          | 0.399               |
| ppu clock (all ppu things) | 12.27                    | 13.48           | 1435702         | 9.387               |
| ppu ppuRead (big problem)  | 4.406                    | 1.626           | 540710          | 3.007               |
| ppu loadBackgroundShifters | 0.213                    | 0.214           | 139476          | 1.534               |
| ppu updateShifters         | 0.384                    | 0.677           | 1057698         | 0.640               |
| ppu getColorFromPaletteRam | 3.058                    | 1.814           | 991841          | 1.856               |
| types.py __get__           | 0.218                    | 0               | 52              | 0                   |
| round                      | 1.160                    | 0               | 9               | 0                   |
| pygame event.get           | 1.684                    | 0               | 17              | 0                   |
| time perf_counter          | 0.563                    | 0.251           | 1435735         | 0.174               |
