# Squier / RB3 MIDI channel merger

**Language / Idioma:** **English** (this page) · [Español →](docs/README_ES.md)

---

Standalone **Raspberry Pi Pico** + **MicroPython**: merges **MIDI channels 1–6** (Rock Band 3 **Squier** / Pro Guitar, one channel per string) onto **one output channel** so mono-channel synths (e.g. **Moog Mother-32**) respond to **all strings**. **5-pin DIN in** and **DIN out**, optional **pot** on **GP26** to pick output channel **1–16**.

---

## Table of contents

1. [Shopping list](#1-shopping-list)  
2. [Connection diagram & pins](#2-connection-diagram--pins)  
3. [Assembly order](#3-assembly-order-suggested)  
4. [Software on the Pico](#4-software-on-the-pico)  
5. [Configuration](#5-configuration)  
6. [First test](#6-first-test)  
7. [More documentation](#7-more-documentation)  
8. [License](#license)

---

## 1. Shopping list

Use as a checklist when ordering parts (e.g. AliExpress, local shop).

| ☐ | Qty | Item |
|---|-----|------|
| ☐ | 1 | **Raspberry Pi Pico** (or RP2040 board with same pinout) |
| ☐ | 2 | **MIDI DIN 5-pin female** jack (panel or PCB mount) — IN + OUT |
| ☐ | 1 | **Optocoupler** — 6N138 *or* 6N137 *or* PC900 (DIP is easy to breadboard) |
| ☐ | 1 | **Diode** 1N4148 or 1N914 *(optional)* — reverse protection on opto LED |
| ☐ | 3 | **Resistor 220 Ω** (¼ W) — 1× MIDI IN, 2× MIDI OUT |
| ☐ | 1 | **Resistor 10 kΩ** — pull-up on opto output → 3.3 V |
| ☐ | 1 | **Potentiometer 10 kΩ linear (B10K)** — output MIDI channel |
| ☐ | 1 | **Capacitor 100 nF ceramic** *(optional)* — wiper → GND, quieter ADC |
| ☐ | 1 | **Breadboard / perfboard / small PCB** |
| ☐ | 1 | **USB cable** — match your Pico (**Micro-USB** or **USB-C**) for power |
| ☐ | — | **MIDI cable(s)** — guitar → box, box → synth (if you don’t have them) |

**Notes**

- Pico logic is **3.3 V** only; do not drive 5 V into GPIO pins.  
- Full BOM with component types: **[HARDWARE.md](HARDWARE.md)**.

---

## 2. Connection diagram & pins

**Full ASCII + Mermaid wiring:** **[docs/WIRING.md](docs/WIRING.md)** — use that when soldering (includes MIDI IN opto circuit, MIDI OUT resistors, pot, and 6N138 pin hints).

**Pico pin summary** (must match [`firmware/main.py`](firmware/main.py)):

| Signal | Pico pin |
|--------|----------|
| MIDI IN (from optocoupler output) | **GP1** (UART0 RX) |
| MIDI OUT (to DIN) | **GP8** (UART1 TX) |
| Channel pot wiper | **GP26** (ADC) |
| GND | Common ground for jacks, pot, opto, Pico |

**DIN jack** (confirm pin numbers on *your* jack’s datasheet — rear / solder side):

- **Pin 2** — ground / shield  
- **Pin 4** — return (IN from guitar; lazy OUT to 3.3 V via 220 Ω)  
- **Pin 5** — hot (IN via 220 Ω to opto LED; OUT from GP8 via 220 Ω)

---

## 3. Assembly order (suggested)

1. **Power & Pico:** fit Pico on breadboard; USB only for power (no need to connect 5 V to MIDI).  
2. **MIDI IN:** DIN → 220 Ω → opto **LED** (pins per **[docs/WIRING.md](docs/WIRING.md)** and **your opto datasheet**).  
3. **Opto logic side:** open-collector output + **10 kΩ** pull-up to **3V3** → **GP1**; opto GND and VCC per datasheet (usually **3.3 V**).  
4. **MIDI OUT:** **GP8** → 220 Ω → OUT jack pin **5**; **3V3** → 220 Ω → pin **4**; **GND** → pin **2**.  
5. **Pot:** ends to **GND** and **3V3**, wiper to **GP26**; optional **100 nF** wiper → GND.  
6. **If the pot is not wired yet:** set `USE_CHANNEL_POT = False` in `main.py` before first boot (floating ADC = random channels).

---

## 4. Software on the Pico

### 4.1 Install MicroPython (once)

1. Download the **.uf2** for your board from **[MicroPython — Raspberry Pi Pico](https://micropython.org/download/RPI_PICO/)** (use **RPI_PICO_W** if you have a Pico W).  
2. Unplug the Pico, hold **BOOTSEL**, plug in USB — it appears as a drive **RPI-RP2**.  
3. Drag the **.uf2** onto that drive; the board reboots running MicroPython.

### 4.2 Copy the firmware

The merger code is **[`firmware/main.py`](firmware/main.py)**. On the Pico it must be named **`main.py`** so it runs on boot.

**Option A — Thonny (GUI)**  

1. Install [Thonny](https://thonny.org/).  
2. Bottom-right → interpreter **MicroPython (Raspberry Pi Pico)**.  
3. Open `firmware/main.py` from this repo → **File → Save as…** → **Raspberry Pi Pico** → save as **`main.py`**.

**Option B — mpremote (terminal)**  

```bash
cd /path/to/squier-midi-merger
pip install mpremote   # if needed
mpremote cp firmware/main.py :main.py
```

### 4.3 Restart

Unplug/replug USB (or press **Stop/Restart** in Thonny). The merger runs automatically; the PC is only needed for **power** in normal use.

More detail: **[docs/SOFTWARE.md](docs/SOFTWARE.md)**.

---

## 5. Configuration

Edit the top of **`main.py`** on the Pico (Thonny or mpremote):

| Setting | Purpose |
|---------|---------|
| `TARGET_CHANNEL` | Used if `USE_CHANNEL_POT` is `False`, and as initial channel until the pot stabilises. |
| `USE_CHANNEL_POT` | `True` = read **GP26** for output channel **1–16**. `False` = fixed `TARGET_CHANNEL` only. |
| `MERGE_CHANNELS` | Default `(1,…,6)` for Squier / RB3 string channels. |
| `PASS_THROUGH_OTHER_CHANNELS` | `True` = forward other MIDI channels unchanged; `False` = drop them. |

Set your **synth’s MIDI receive channel** to match the merger output (many devices default to **channel 1**).

---

## 6. First test

1. **Squier** (or guitar) **MIDI OUT** → this box **MIDI IN**.  
2. This box **MIDI OUT** → **synth MIDI IN**.  
3. **USB** → charger or power bank (Pico).  
4. Play each string — the synth should track **all** strings on **one** channel.  
5. Stuck notes: **Start + Back** on the Squier (MIDI panic) or power-cycle.

---

## 7. More documentation

| Doc | Contents |
|-----|----------|
| [HARDWARE.md](HARDWARE.md) | BOM table, DIN notes, build tips |
| [docs/WIRING.md](docs/WIRING.md) | Full connection diagrams (ASCII + Mermaid) |
| [docs/SOFTWARE.md](docs/SOFTWARE.md) | Parser behaviour, UART pins, limits |
| [docs/GLOSSARY.md](docs/GLOSSARY.md) | Terms (UART, optocoupler, ADC, …) |

---

## License

Hardware and firmware in this repo: use at your own risk for personal projects. Third-party trademarks (Fender, Squier, Rock Band, Moog, Raspberry Pi, etc.) belong to their owners.
