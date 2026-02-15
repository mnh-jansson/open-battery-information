# OBI-1 Standalone OLED — Makita LXT Battery Tool

**Author: Massimo Biagi**

Standalone version of the [Open Battery Information](https://github.com/mnh-jansson/open-battery-information) project. Runs entirely on an Arduino Nano with an OLED display and 2 buttons — no PC required.

## Features

| Menu Item     | Function                                          |
|---------------|---------------------------------------------------|
| Read Battery  | Reads model, ROM ID, charge count, state, voltages, temperatures — all in one step |
| LED ON        | LED functional test (turn on)                     |
| LED OFF       | LED functional test (turn off)                    |
| Clear Errors  | Reset BMS error flags                             |
| Reset Msg     | Reset battery message (work in progress)          |

## Hardware

- Arduino Nano (ATmega328P)
- OLED SSD1306 128x32 I2C
- 2 momentary push buttons
- OneWire circuit from original ArduinoOBI project

### Wiring

```
Arduino Nano
┌───────────────────────┐
│  D2  ◄── BTN_A ── GND   (Next / Back)
│  D3  ◄── BTN_B ── GND   (OK / Execute)
│                          
│  D7  ◄──► OneWire ──► Makita battery
│  D8  ───► Enable  ──► Battery power circuit
│                          
│  A4 (SDA) ───────► OLED SDA
│  A5 (SCL) ───────► OLED SCL
│  5V  ────────────► OLED VCC
│  GND ────────────► OLED GND + buttons
└───────────────────────┘

Pull-up resistors: 4.7kΩ on OneWire and Enable lines
(see original ArduinoOBI schematic)
```

### Button Controls

| Button | Short press | Long press (>0.8s) |
|--------|-------------|---------------------|
| **A**  | Next item / Scroll | Back to menu   |
| **B**  | OK / Execute       | —              |

## Installation

1. Install **SSD1306Ascii** by Bill Greiman from Arduino Library Manager
2. Copy `OneWire2.h`, `OneWire2.cpp`, and `util/` folder from the original project's `ArduinoOBI/lib/OneWire/` into this sketch folder
3. Open `OBI_Standalone_OLED.ino` in Arduino IDE
4. Select Board: **Arduino Nano**, Processor: **ATmega328P**
5. Upload

## Translation

All user-visible strings are grouped at the top of the `.ino` file under the **LANGUAGE / LABELS** section. To translate to another language, simply change those `#define` and `PROGMEM` strings.

## License

MIT License — see [LICENSE.md](LICENSE.md)

Copyright (c) 2026 Massimo Biagi — Standalone OLED Edition
Copyright (c) 2024 Martin Jansson — Open Battery Information

This project is based on [Open Battery Information](https://github.com/mnh-jansson/open-battery-information) by Martin Jansson, released under the MIT License. The Standalone OLED adaptation is released under the same license.

As required by the MIT License, the original copyright notice and permission notice are preserved in all copies and substantial portions of the software.
