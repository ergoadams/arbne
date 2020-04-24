# nes
A Python based NES emulator attempt.

#TODO
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
