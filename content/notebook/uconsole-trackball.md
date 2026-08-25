---
title: Fixing the uConsole trackball with custom QMK firmware
date: 2026-06-06
tags:
- uconsole
- trackball
- qmk
- firmware
- labwc
aliases:
- uConsole trackball
- uConsole pointer
description: 'Custom QMK firmware for the ClockworkPi uConsole trackball: the slow-after-reboot
  quirk and its fix, scroll and precision modes, and how to recover a bad flash.'
publish: true
---

# uConsole — Trackball & Pointer

Part of uConsole.

## The problem (stock)
Out of the box the trackball felt **slow, insensitive, intermittent**, and had **no horizontal scroll**. This is a well-known stock-firmware issue, not a hardware defect — the keyboard/trackball is an STM32-based QMK device, and the stock firmware polls the sensor poorly. Measured raw events showed ~50 Hz with frequent dropouts.

## Fix 1 — Custom QMK firmware (j1n6)
Flashed **[j1n6/qmk-uconsole](https://github.com/j1n6/qmk-uconsole) v1.8.0**. The trackball/keyboard is an **independent USB device** (`feed:0000` after flashing; was `1eaf:0024` on stock) — if it ever breaks, the rest of the uConsole is unaffected.

- Everything staged at **`~/uconsole-qmk/`**:
  - `qmk-uconsole/` — the repo (README has the full guide)
  - `uconsole_keyboard_flash/` — ClockworkPi's stock package: `maple_upload`, `flash.sh` (recovery), stock firmware `uconsole_keyboard.ino.bin`, and the QMK `.bin`
- **First flash (from stock)** uses `maple_upload` (triggers the Maple DFU bootloader over the serial port `/dev/ttyACM0` — no key combo needed):
  ```
  cd ~/uconsole-qmk/uconsole_keyboard_flash
  sudo ./maple_upload ttyACM0 2 1EAF:0003 clockworkpi_uconsole_default.bin
  ```
  (The `maple_upload` delays were bumped 750→1500 ms per the README for reliability.)
- **Re-flash / update QMK** (already on QMK): enter bootloader with **Left-Alt + Right-Alt + Start**, then
  ```
  sudo dfu-util -w -d 1eaf:0003 -a 2 -D clockworkpi_uconsole_default.bin -R
  ```
- **Recovery / unbrick:** short the **S1 pin** on the keyboard PCB (green LED flashes), then `sudo ./flash.sh` to restore stock. May take several tries.

### New QMK key behaviors
- **Scroll:** hold **Select** + roll trackball — up/down = vertical, left/right = horizontal (the firmware now advertises the horizontal-wheel bit; stock didn't).
- **Precision cursor mode:** hold **Select** + click trackball **middle button** to toggle reduced-movement fine control. (If the cursor ever feels deliberately slow, check you didn't toggle this on.)
- **Tap-hold** keys: toggle with **Fn+T**. **Factory reset:** **Fn+C**.

## Fix 2 — libinput speed (labwc)
Stock libinput defaults felt sluggish, so `~/.config/labwc/rc.xml` has a `<libinput>` block: **`pointerSpeed 1.0`, `accelProfile flat`**. Reload with `pkill -HUP -x labwc`.

## ⚠️ The "slow trackball after every reboot" quirk — IMPORTANT
**labwc applies the `<libinput>` config on *reconfigure*, but NOT at a fresh boot** — so after each restart the trackball silently reverts to libinput's slow default until a reload.

- **Confirmed it's not the firmware:** raw device output is strong (avg step ~5.7, max 127, plenty of events). The OS just wasn't scaling it.
- **Permanent fix:** `~/.config/labwc/autostart` re-applies the config a few seconds into each login:
  ```sh
  ( sleep 4; pkill -HUP -x labwc ) &
  ```
- **Manual fix anytime:** `pkill -HUP -x labwc`.

## Residual hardware limit
Even on custom firmware the sensor tops out ~50 Hz with occasional dropouts (the "intermittent" feel; community-confirmed). Firmware roughly halved dropouts. The remaining lever is **mechanical**: a printable **TPU trackball shim** (from the j1n6 repo) that tightens the module fit. Optional.
