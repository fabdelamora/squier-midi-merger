# Software — MIDI channel merger

## What runs on the device

- **Runtime:** [MicroPython](https://micropython.org/) on the **Raspberry Pi Pico** (RP2040).
- **Source file:** `firmware/main.py` — copy it to the Pico as **`main.py`** so it **starts automatically** when the board powers up.

No Arduino IDE or C toolchain is required if you use MicroPython + a tool like **Thonny** or **mpremote**.

## What the program does

1. Opens **UART0** at **31,250 baud** on **GP1** (MIDI **IN** from the optocoupler).
2. Opens **UART1** at **31,250 baud** on **GP8** (MIDI **OUT** to the DIN jack).
3. Loops forever: read **one byte** from IN → run it through a small **MIDI 1.0 parser** → write any output bytes to OUT.

The parser understands **running status**, **SysEx** (pass-through), **system real-time** bytes (`0xF8`–`0xFF`), and short **system common** messages (`F1`, `F2`, `F3`). For **channel voice** messages (`0x80`–`0xEF`), it checks the **MIDI channel** (lower nibble of the status byte):

- If the channel is in **`MERGE_CHANNELS`** (default **1–6**), the status byte is rewritten so the message is sent on **`TARGET_CHANNEL`** instead.
- If the channel is **not** in that set: either **pass through** unchanged or **drop**, depending on **`PASS_THROUGH_OTHER_CHANNELS`**.

So: **Note On/Off, poly aftertouch, CC, program change, channel pressure, pitch bend** on strings 1–6 all get remapped to one channel. **Timing clock, start/stop, active sense**, etc. are forwarded as-is.

## Settings (edit at top of `main.py`)

| Name | Meaning |
|------|---------|
| `TARGET_CHANNEL` | Used when **`USE_CHANNEL_POT`** is `False`, and as the merger’s state until the pot stabilises after power-up. |
| `USE_CHANNEL_POT` | `True` = read **GP26** (ADC) and map **0–3.3 V** to output channels **1–16**. `False` = fixed `TARGET_CHANNEL` only (use if no pot wired). |
| `CHANNEL_POT_PIN` | ADC pin (default **26**). Must match wiring. |
| `ADC_POLL_MS` / `POT_DEBOUNCE_READS` | How often the pot is sampled and how many stable reads before changing channel (reduces jitter). |
| `MERGE_CHANNELS` | Which input channels to remap (default `1`–`6` for the Squier / RB3 layout). |
| `PASS_THROUGH_OTHER_CHANNELS` | `True` = forward other channels unchanged; `False` = ignore them. |
| `UART_*_PIN` | Must match `HARDWARE.md` (GP1 IN, GP8 OUT). |

Many synths default to **MIDI channel 1**, but gear like the **Mother-32** can be set to another channel — the pot lets you match the synth **without editing code** or re-flashing.

## Install MicroPython (once)

1. Download the **Pico** UF2 from [micropython.org](https://micropython.org/download/RPI_PICO/) (or **RPI_PICO_W** for Pico W).
2. Hold **BOOTSEL**, plug USB, drag the UF2 onto the drive; it reboots with MicroPython.

## Put `main.py` on the Pico

**Thonny:** Select interpreter → **MicroPython (Raspberry Pi Pico)** → open `main.py` → **File → Save as** → **Raspberry Pi Pico** → name **`main.py`**.

**mpremote (CLI):** `mpremote cp firmware/main.py :main.py`

After save, **reset** the Pico (unplug/replug or Thonny Stop/Run). The merger runs without a PC once USB power is applied.

## Change settings later

Edit `main.py` on the Pico (Thonny or mpremote), save, reset. No separate “build” step.

## Limits / notes

- **Latency:** One-byte-at-a-time processing; fine for live playing on a 31.25 kbps link.
- **MIDI merge from multiple DIN inputs:** not supported — **one** MIDI IN only.
- **USB MIDI from the guitar:** this box expects **5-pin DIN** from the Squier; if you only have USB, you need a different interface.

## Related docs

- Wiring and BOM: [HARDWARE.md](../HARDWARE.md)
- Terms: [GLOSSARY.md](GLOSSARY.md)
