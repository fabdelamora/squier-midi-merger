# MIDI channel merger — hardware (Pico)

Acronyms and terms (UART, DIN, BOM, …): see [docs/GLOSSARY.md](docs/GLOSSARY.md).  
Firmware (MicroPython, `main.py`, flashing): see [docs/SOFTWARE.md](docs/SOFTWARE.md).  
**Wiring diagram (ASCII + Mermaid):** [docs/WIRING.md](docs/WIRING.md).

Goal: **one MIDI IN (DIN)**, **one MIDI OUT (DIN)**, merge **channels 1–6 → one channel** for the Squier / RB3 Pro Guitar.

## Brain

| Part | Why |
|------|-----|
| **Raspberry Pi Pico** (original or Pico H) | Two UARTs, 3.3 V, ~$4–5, MicroPython |

Cheaper clones (RP2040 with same pinout) usually work if UART pins match.

## BOM (minimal)

| Qty | Type | Part | Notes |
|-----|------|------|--------|
| 1 | Microcontroller board | Raspberry Pi Pico | RP2040; two UARTs; 3.3 V logic |
| 2 | Connector | MIDI DIN 5-pin female (panel / PCB mount) | MIDI IN + MIDI OUT jacks |
| 1 | Optocoupler (IC) | 6N138 **or** 6N137 **or** PC900 | MIDI IN galvanic isolation |
| 1 | Diode | 1N914 or 1N4148 | Across opto LED (reverse protection) — optional |
| 1 | Resistor | 220 Ω | MIDI IN: current limit into opto LED |
| 1 | Resistor | 10 kΩ | Pull-up on opto output to 3.3 V |
| 2 | Resistor | 220 Ω | MIDI OUT: series on pin 5 and pin 4 path (see below) |
| 1 | Potentiometer | 10 kΩ linear (B10K) | Output MIDI channel 1–16; wiper to **GP26** (see below) |
| 1 | Capacitor (optional) | 100 nF ceramic | Wiper to GND — reduces ADC jitter |
| 1 | Prototyping / substrate | Breadboard, perfboard, or small PCB | |
| 1 | Cable | USB cable (Micro-USB or USB-C, match your Pico) | Power only; from charger or power bank |

**Pico is 3.3 V.** MIDI current-loop input is fine with 3.3 V pull-up on the transistor side of the opto (standard hobby approach).

## DIN pinout (looking at **sockets**, pins on rear)

- **Pin 2**: ground / shield (tie to circuit GND)
- **Pin 4**: MIDI source current return (IN from guitar: to opto cathode side)
- **Pin 5**: MIDI “hot” (IN: through 220 Ω to opto LED anode; OUT: from Pico via resistor)

Always double-check your jack’s datasheet — pin numbering on the plastic can differ; continuity wins.

## MIDI IN (guitar → Pico)

Classic circuit:

- **DIN pin 5** → **220 Ω** → opto **LED anode**
- **DIN pin 4** → opto **LED cathode**
- Optional: diode **cathode to pin 5, anode to pin 4** (reverse protection on LED)
- Opto output (e.g. 6N138 pin 6 or typical TTL out): to **GP1** (Pico **UART0 RX**)
- **10 kΩ** from that line to **+3.3 V**
- Opto GND ↔ Pico GND; opto VCC per datasheet (many use 3.3 V on logic side)

Result: UART0 RX on **GP1** @ **31250** baud.

## MIDI OUT (Pico → Mother-32)

- **GP8** = **UART1 TX** (31250 baud)
- **220 Ω** from GP8 → **DIN pin 5**
- **DIN pin 4** → **220 Ω** → **+3.3 V** (lazy output; works with most modern gear)
- **DIN pin 2** → GND

Some builds use a proper driver transistor for OUT; for short cable to a Mother-32, this resistor-only output is usually enough.

## Output channel pot (optional but recommended)

Firmware maps the ADC reading to **MIDI channels 1–16** in equal zones. A **stepped / detented** pot feels nicer than a smooth turn between “almost 3” and “almost 4,” but a normal linear pot works; enable **`USE_CHANNEL_POT`** in `firmware/main.py` (default on).

- One end of pot → **GND**
- Other end → **+3.3 V** (Pico **3V3** out)
- Wiper → **GP26** (ADC0)
- Optional **100 nF** from wiper to GND

If the pot is **not** wired yet, set **`USE_CHANNEL_POT = False`** in `main.py` so the pin is not left floating (random channels).

## Pin summary (matches `firmware/main.py`)

| Signal | Pico pin |
|--------|-----------|
| MIDI IN (from opto) | **GP1** (UART0 RX) |
| MIDI OUT | **GP8** (UART1 TX) |
| Channel select pot wiper | **GP26** (ADC0) |
| GND | GND |

Power Pico via USB (no need to send 5 V on MIDI pins).

## Firmware

Short version: install **MicroPython**, save `firmware/main.py` on the Pico as **`main.py`**, set `TARGET_CHANNEL` to match your synth, power-cycle.

Full steps, parser behavior, and tools (Thonny / mpremote): **[docs/SOFTWARE.md](docs/SOFTWARE.md)**.

## Testing

- MIDI monitor on PC (if you add a USB–MIDI interface in the chain) or observe Mother-32 responding on all strings after merge.
- If notes stick, use guitar **Start + Back** panic (per Squier manual) or power-cycle.

## 3D-printed case (later)

Leave strain relief for USB, jack nuts accessible, and keep opto + Pico away from the DIN shells to avoid shorts.
