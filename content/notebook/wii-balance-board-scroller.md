---
tags:
- hardware
- linux
- bluetooth
- input
- wii
created: 2026-05-01
title: A Wii Balance Board as a Linux scrolling device
publish: true
description: Turning a Wii Balance Board into a Linux scroll input over Bluetooth
  — lean to scroll, and the uinput plumbing that makes it work.
---

# Wii Balance Board scrolling device

Local project: `/home/jaden/wbb-uinput`

GitHub: https://github.com/g-rden/wbb-uinput

Original inspiration: [Use a Wii Balance Board with Linux](https://www.mattcutts.com/blog/linux-wii-balanceboard/) by Matt Cutts, May 22, 2009.

## What I Built

I had a small Linux/uinput project that turns a Bluetooth-connected Nintendo Wii Balance Board into a virtual input device.

The core idea is simple: Linux sees the board as an input device with four corner weight sensors, then the program reads those sensor values and emits synthetic mouse or scroll events through `/dev/uinput`.

Interesting details:

- The repo is based on ideas from [WiiWeight](https://github.com/keldu/WiiWeight) and [uinput-joystick-demo](https://github.com/GrantEdwards/uinput-joystick-demo).
- `wbb-uinput.c` turns the board into a virtual relative mouse named `Virtual Mouse`.
- `move_mouse.c` is the more interesting scrolling version: it registers `REL_WHEEL` and emits wheel events from balance changes.
- The four sensors are mapped from Linux absolute axis codes: `ABS_HAT0X`, `ABS_HAT1X`, `ABS_HAT0Y`, and `ABS_HAT1Y`.
- The code computes rough lean axes from the four sensor values: `x = right - left`, `y = back - front`.
- The current local working tree has uncommitted changes that convert `move_mouse.c` from pointer movement to wheel scrolling.
- Current local branches include `main`, `scroll`, and `trackpad`; `scroll` and `trackpad` point at commit `a5463c5` (`much better`).
- The compiled binaries `move_mouse` and `wbb-uinput` are present locally and executable.

## Matt Cutts Article

Link: https://www.mattcutts.com/blog/linux-wii-balanceboard/

The article shows how to use a Wii Balance Board on Linux as a Bluetooth weight sensor and real-time controller, originally with about 200 lines of Python and the CWiid library.

Main contents:

- Install Bluetooth/CWiid build dependencies on Ubuntu, including `autoconf`, `automake`, `gcc`, `bluetooth`, `libbluetooth-dev`, GTK dev packages, Python dev headers, `flex`, `bison`, and Subversion.
- Check out and build CWiid, then apply a Balance Board patch from an old CWiid ticket.
- Run `weighdemo.py` to read the four board sensors and print their raw values, calibration data, and total weight.
- Use WiiBrew calibration information: each sensor has readings for 0 kg, 17 kg, and 34 kg, and weight is computed by interpolating between calibration points.
- Sum the four calibrated sensor values to estimate total weight.
- Use pygame and `scalesgui.py` to display a fast graphical center-of-balance dot and total weight.
- The punchline: the Balance Board is four independent calibrated weight sensors readable in real time over Bluetooth.

Relevant historical detail from the comments: someone immediately imagined using it as a giant mouse, including scrolling down a page by leaning back. That is basically what this local `move_mouse.c` experiment became.

## Reproduce Locally

1. Pair/connect the Wii Balance Board over Bluetooth.

2. Confirm Linux sees it:

```bash
grep -A10 -B2 "Nintendo Wii Remote Balance Board" /proc/bus/input/devices
```

At the time I checked, it was connected as:

```text
Nintendo Wii Remote Balance Board
Handlers=event6 js1
```

So the input path was `/dev/input/event6`.

3. Build the scrolling program if needed:

```bash
cd /home/jaden/wbb-uinput
gcc move_mouse.c -lm -o move_mouse
```

4. Run it with the board event device:

```bash
sudo /home/jaden/wbb-uinput/move_mouse /dev/input/event6
```

5. Stand on or press the board and shift weight forward/backward. The program emits virtual mouse wheel events through `/dev/uinput`.

6. If `/dev/input/event6` changes, use the handler shown in `/proc/bus/input/devices` instead.

## Notes

- The README mentions using AntiMicroX or similar tools for mapping joystick/mouse/keyboard inputs, but the current scrolling version emits wheel events directly.
- If `/dev/uinput` permission fails, see the Arch wiki note linked from the README: https://wiki.archlinux.org/title/Wiimote#Unable_to_open_uinput
- The archived Omnivore stub for the Matt Cutts article is at `archive/Omnivore/2023-11-18/Use a Wii Balance Board with Linux.md`.
