# VitalTrack

First-year hardware project: a portable heart rate (HR) and heart rate variability (HRV) monitor using Raspberry Pi Pico and MicroPython.

## Features
- Heart rate display
- 30s measurement session
- HRV metrics (e.g., SDNN, RMSSD)
- OLED UI + button/rotary input (depending on build)

## Hardware
- Raspberry Pi Pico (RP2040)
- SSD1306 OLED (I2C)
- Pulse sensor (e.g., Crowtail Pulse Sensor)
- Input: button / rotary encoder

## Repo structure
- `src/main.py` – MicroPython application
- `docs/report.pdf` – project report
- `docs/images/` – photos / wiring

## How to run
1. Flash MicroPython to the Pico
2. Copy `src/main.py` to the Pico as `main.py`
3. Reset Pico and start measurement from the UI
