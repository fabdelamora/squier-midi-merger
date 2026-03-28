# Glossary

Short definitions for terms and acronyms used in this MIDI merger project.

| Term | Meaning |
|------|---------|
| **BOM** | Bill of materials — the parts list (what to buy and how many). |
| **CC** | Control change — a MIDI message type (e.g. knobs, pedals, switches); status range `0xB0`–`0xBF` per channel. |
| **DIN** | Deutsches Institut für Normung — here it means the **round 5-pin MIDI connector** everyone calls a “MIDI plug.” |
| **DAW** | Digital audio workstation — software like Ableton, Logic, Reaper used to record and route MIDI/audio. |
| **GND** | Ground — the 0 V reference; all devices in a MIDI setup share a common ground on the cable shield / pin 2. |
| **GP** | GPIO pin — a **general-purpose** pin on the Pico (e.g. **GP1**, **GP8**) used for UART RX/TX. |
| **MIDI** | Musical Instrument Digital Interface — a serial protocol (31,250 baud) for note, timing, and controller data. |
| **Mother-32** | Moog semi-modular synth; in this project it’s the example **destination** that listens on **one MIDI channel**. |
| **Note On / Note Off** | MIDI messages that start or stop a note (`0x9n` / `0x8n`, where `n` is the channel nibble). |
| **Opto / optocoupler** | See **Optocoupler** below — short for the part used on **MIDI IN**. |

### Optocoupler (detailed)

An **optocoupler** (also **optoisolator**) is a small chip that contains an **internal LED** and a **light detector** (usually a phototransistor) in one package. The sender’s circuit turns the LED on and off; the detector sees the light and switches its output — so the **MIDI signal crosses as light**, not as a direct electrical path between the guitar and the Pico.

**Why MIDI IN uses one:** The MIDI specification calls for **galvanic isolation** on inputs. That way different devices’ grounds and voltages don’t fight each other (**ground loops**), and a fault or weird voltage on the cable is less likely to damage your microcontroller. Common parts: **6N138**, **6N137**, **PC900**.

**MIDI OUT** on this project does **not** need an optocoupler — isolation is required on the **receiver’s** input; our box only drives the next device’s input through resistors, as in `HARDWARE.md`.
| **Pico** | **Raspberry Pi Pico** — the small microcontroller board (RP2040 chip) running the merger firmware. |
| **Program change** | MIDI message to select a patch/sound (`0xCn` + program number). |
| **Pro Guitar** | Rock Band 3 **Pro** mode guitar controllers (Mustang or Squier) that send **per-string** MIDI. |
| **RB3** | **Rock Band 3** — the game the Squier Strat was built for. |
| **RP2040** | The microcontroller **chip** on the Pico (designed by Raspberry Pi). |
| **Running status** | MIDI optimization: after a full status byte, repeated messages can omit the status byte until a new one appears. The merger **must** understand this when reading the input stream. |
| **Squier** | **Squier by Fender** — budget Fender line; here the **Squier Stratocaster Guitar and Controller** for RB3 with MIDI out. |
| **SysEx** | System exclusive — manufacturer-specific MIDI messages wrapped in `0xF0` … `0xF7`. |
| **ADC** | Analog-to-digital converter — on the Pico, **GP26–GP28** can read a voltage (e.g. a **pot** wiper) to choose the output MIDI channel in software. |
| **UART** | Universal asynchronous receiver-transmitter — **hardware serial port** on the Pico (one wire in, one out) used for MIDI at 31,250 baud. |
| **USB** | Universal Serial Bus — how the Pico gets **power** from a charger or computer in this design. |

### MIDI channels (quick)

- MIDI has **16 channels** (numbered **1–16** in user interfaces; in the wire protocol they are **0–15**).
- The Squier / RB3 layout uses **six channels** (often **1–6**) so **each string** is separate; a Mother-32 usually listens on **one** channel — hence the need to **merge** channels into one.

### File / firmware names

| Name | Meaning |
|------|---------|
| **`main.py`** | MicroPython **boot script** on the Pico — our merger code. |
| **`HARDWARE.md`** | Wiring, BOM, and pin list. |
| **`firmware/`** | Folder containing `main.py` for the device. |

If you want a term added, drop it in and we can extend this file.
