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
- [ ] Seperate PPU from the bus, to have the ability to run the emulation without picture
- [x] Debug mode
- [x] Illegal opcodes (well I mean there are some weird ones, but the ones in nestest pass)

## Things to optimize (data is based on the emulator running for 20 seconds, originally about 11 frames)
Biggest problems right now are bus cpuWrite, cpu ABS, LDA, CMP, REL, ZP0, fetch and ppu ppuRead  
We got to 1 fps! Now need to get it only 60 times faster...    
May 7th update: average of 2 fps reached! Only need to get it 30 times faster now. 


Remade table, moved work to Ubuntu..

| Function                   | original cumulative time | optimized time? | number of calls | calls to time ratio |
| -------------------------- | ------------------------ | --------------- | --------------- | ------------------- |
| bus cpuWrite               | 0.046                    | 0.046           | 6789            | 6.776               |
| bus cpuRead                | 1.354                    | 1.354           | 611892          | 2.213               |
| cartridge cpuRead          | 0.959                    | 0.959           | 611892          | 1.567               |
| cartridge ppuRead          | 0.769                    | 0.769           | 842967          | 0.912               |
| cpu BEQ                    | 0.157                    | 0.157           | 103213          | 1.521               |
| cpu CMP                    | 0.432                    | 0.432           | 102796          | 4.202               |
| cpu ZP0                    | 0.317                    | 0.317           | 102784          | 3.084               |
| cpu LDA                    | 0.043                    | 0.043           | 9948            | 4.322               |
| cpu REL                    | 0.500                    | 0.500           | 118443          | 4.221               |
| cpu ABS                    | 0.082                    | 0.082           | 14793           | 5.543               |
| cpu fetch                  | 0.302                    | 0.302           | 113456          | 2.662               |
| mapper cpuMapRead          | 0.421                    | 0.421           | 611892          | 0.688               |
| mapper ppuMapRead          | 0.313                    | 0.313           | 842967          | 0.371               |
| ppu ppuRead                | 1.994                    | 1.994           | 842967          | 2.365               |
| ppu loadBackgroundShifters | 0.268                    | 0.268           | 217459          | 1.232               |
| ppu updateShifters         | 0.677                    | 0.677           | 1649079         | 0.411               |
| ppu getColorFromPaletteRam | 2.147                    | 2.147           | 1546400         | 1.388               |
| time perf_counter          | 0.212                    | 0.212           | 2238867         | 0.094               |
