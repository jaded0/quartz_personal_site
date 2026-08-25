---
title: ESP32 sensor lab
publish: true
description: 'Hub note for the ESP32 MicroPython sensor experiments. Repo: esp/ (GitHub:
  esp32-sensor-lab).'
---

# ESP32 Sensor Lab

Hub note for the ESP32 MicroPython sensor experiments. Repo: `esp/` (GitHub: `esp32-sensor-lab`).

Two boards, each auto-running one OLED program on boot:
- **CO₂ monitor** (`air_monitor.py`, bedroom) — SCD41 CO₂/T/RH with a CO₂ trend
  graph; temp/RH calibrated against the SHT41 (see [Calibration](#calibration)).
- **Radar** (`main.py`, office) — LD2410C presence/distance/energy with a distance
  graph, plus an ambient temp/RH readout from the SHT41.

See also: ESP32 Sensor Lab - Wiring & Pinout

## Boards

Two physical ESP32-D0WD-V3 dev boards (4 MB flash), distinguished by MAC:

| Role | MAC | Current firmware |
| ---- | --- | ---------------- |
| CO₂ monitor (bedroom) | `8c:4f:00:36:4d:a8` | MicroPython 1.28.0 + `air_monitor.py` |
| Radar + SHT41 (office) | `8c:4f:00:36:3b:10` | MicroPython 1.28.0 + radar `main.py` |

> The `/dev/ttyUSB*` numbers are **not stable** — they swap on replug depending on
> enumeration order. A board's MAC is burned into eFuse and never changes, so
> `uvx esptool --port <port> chip-id` is the reliable way to tell which board is which.

## Toolchain (NixOS)

Nothing installed globally; everything via `uvx`:

```sh
uvx esptool --port /dev/ttyUSB0 erase-flash
uvx esptool --port /dev/ttyUSB0 --baud 460800 write-flash -z 0x1000 ESP32_GENERIC-*.bin
uvx mpremote connect /dev/ttyUSB0 mip install ssd1306   # OLED driver onto board
uvx mpremote connect /dev/ttyUSB0 fs cp main.py :main.py
uvx mpremote connect /dev/ttyUSB0 reset
uvx mpremote connect /dev/ttyUSB0                        # REPL
```

Firmware: MicroPython `ESP32_GENERIC` v1.28.0 (`20260406`) from
<https://micropython.org/download/ESP32_GENERIC/>.

## The two programs

### CO₂ monitor — `air_monitor.py` (bedroom)
- SCD41 (`0x62`) + SSD1306 (`0x3C`) on the I²C bus — SCD41 standalone now.
- Top line: CO₂ + an at-a-glance quality label (GOOD <800, OK <1200, POOR <2000, BAD! ≥2000 ppm).
- Second line: calibrated temp (°F) + humidity (`T:…F H:…%`).
- Bottom half: scrolling CO₂ graph, autoscaled (≈10 min window at one sample / 5 s).
- Temp comes corrected from the chip (persisted offset); humidity gets a software
  `RH_OFFSET` correction. See [Calibration](#calibration).

![CO2 monitor display](air-monitor-display.png)

### Radar — `main.py` (office)
- LD2410C over UART (256000 baud), OUT pin on GPIO13; SHT41 (`0x44`) on I²C.
- Top line: state — CLEAR / MOVING / STILL / BOTH — with `*` when OUT is HIGH, and
  the SHT41 ambient temp/RH right-aligned (`…F …%`).
- Moving + stationary target distance (cm) and signal energy (0–100).
- Bottom half: scrolling detection-distance graph (~20 s window; 0 cm = clear at bottom).
- It detects a *stationary* person via the micro-motion of breathing.

![Radar display](radar-display.png)

## Calibration

The two sensors were logged side-by-side (`tools/calibrate_offset.py`) to dial in
the SCD41 for standalone use; `tools/apply_offset.py` writes the offset to its EEPROM.

- **Temperature: slow to settle + airflow-dependent.** Self-heat decays from 7+ °C
  right after power-on to ~**4.2 °C** over **~15–20 min**, reading high until then.
  It also depends on the mount (~3.5 °C on an open, ventilated breadboard) and
  jitters ~±0.5 °C with ambient drift even when settled. Persisted offset is
  **4.2 °C** (settled desk condition). A short calibration run catches the sensor
  still cooling and under-estimates the offset — the first attempt did exactly that
  and landed at 3.49 °C, then a 10-min run still over-shot at 4.99 °C; 4.2 is the
  fully-equilibrated value. Recalibrate in the actual resting spot, and let
  `calibrate_offset.py` run its full window.
- **Humidity has no chip offset.** The SCD41 reads high on RH vs the SHT41 (SCD4x
  ±6–9 %RH vs SHT41 ±1.8 %RH, so the SHT41 is the reference). `air_monitor.py`
  subtracts a software `RH_OFFSET`, but treat it as approximate — RH also wanders
  with the sensor's thermal state.

> **Bottom line:** trust the SCD41 for **CO₂**; its T/RH are secondary and swing
> ~1–2 °C / several %RH with placement and warm-up. The SHT41 is the reference for
> ambient T/RH.

## Gotchas & lessons learned

- **Wrong/unresponsive board:** if `mpremote` can't get a REPL but `esptool` still
  detects the chip, the board has no/halted firmware. Check the MAC with esptool —
  a different MAC means it's literally a different board (this bit us once). Reflash.
- **LD2410C TX/RX is reversed from the silkscreen labels.** Working wiring: sensor
  TX → ESP32 GPIO27, sensor RX → ESP32 GPIO14. Code uses `UART(2, rx=27, tx=14)`.
- The LD2410C **streams basic data unprompted** — you only need its TX → ESP32 RX to
  read presence + distance. Sending commands (engineering mode) needs the TX line too.
- **Voltage:** I²C sensors + OLED on 3V3; the LD2410C wants **5V** (VIN), though its
  logic is still 3.3 V so the data lines wire straight to the ESP32.
- **MicroPython `%d` on a float can raise** (not just truncate) on some builds — cast
  to `int()` before formatting, or a display loop can crash.
- I²C bus reserved pins: SDA=21, SCL=22. Avoid GPIO 6–11 (flash), 1/3 (USB serial),
  and strapping pins 0/2/12/15 for anything finicky.

## LD2410C basic report frame

```
F4 F3 F2 F1 | len(2,LE) | 02 AA | state | mov_dist(2) mov_e | sta_dist(2) sta_e | det_dist(2) | 55 00 | F8 F7 F6 F5
```
`state`: 0 none · 1 moving · 2 stationary · 3 both. Distances in cm, energies 0–100.

## Ideas / TODO

- **Breathing-rate estimate:** the LD2410C has no respiration output, but the
  stationary energy oscillates with chest movement. Logging it and finding the
  dominant frequency in the 6–30 BPM band *might* yield a rough rate (sit still,
  ~1 m, facing the sensor). A 60 GHz vitals radar would do this properly.
- Data logging (CSV to flash or streamed) to chart SCD41-vs-SHT41 drift.
- Combine both boards / sensors into one dashboard.
