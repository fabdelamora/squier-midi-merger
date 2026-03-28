"""
Squier / RB3-style MIDI channel merger for Raspberry Pi Pico (MicroPython).

Merges MIDI channels 1–6 (Rock Band Pro Guitar per-string channels) onto one
output channel. DIN IN -> UART RX, DIN OUT <- UART TX. See ../HARDWARE.md.

Optional pot on an ADC pin selects output channel 1–16. Upload as main.py.
"""

import time

import machine
from machine import ADC, Pin, UART

# --- User settings ---
TARGET_CHANNEL = 1  # 1–16: used when USE_CHANNEL_POT is False, and as power-on default
MERGE_CHANNELS = (1, 2, 3, 4, 5, 6)  # inbound channels to remap
PASS_THROUGH_OTHER_CHANNELS = True  # False = drop traffic not on MERGE_CHANNELS

# Output channel from pot: 10 kΩ linear between 3V3 and GND, wiper -> GP26
USE_CHANNEL_POT = True
CHANNEL_POT_PIN = 26  # ADC0; set USE_CHANNEL_POT = False for fixed TARGET_CHANNEL only
ADC_POLL_MS = 25  # how often to read the pot
POT_DEBOUNCE_READS = 4  # same zone this many times before applying (reduces jitter)

# Wiring: GP1 = MIDI IN (from optocoupler), GP8 = MIDI OUT
UART_IN_ID = 0
UART_IN_RX_PIN = 1
UART_OUT_ID = 1
UART_OUT_TX_PIN = 8
BAUD = 31250

_MERGE_NIBBLES = frozenset(c - 1 for c in MERGE_CHANNELS)  # 0–15 -> 0–5 for ch 1–6


def _voice_data_len(status: int) -> int:
    h = status & 0xF0
    if h in (0xC0, 0xD0):
        return 1
    if h in (0x80, 0x90, 0xA0, 0xB0, 0xE0):
        return 2
    return 0


def _channel_from_adc_u16(raw: int) -> int:
    """Map 0..65535 to MIDI channels 1..16 (sixteen equal zones)."""
    ch = 1 + (raw * 16 // 65536)
    return 16 if ch > 16 else ch


class _MidiRemap:
    """MIDI stream parser with running status; remaps selected channels on voice messages."""

    def __init__(self, initial_channel: int = 1) -> None:
        self._running = 0  # voice running status (0x80–0xEF); 0 = none
        self._sysex = False
        self._collect = bytearray()
        self._sys_common = 0  # pending F1 / F2 / F3
        self._target_nibble = (max(1, min(16, initial_channel)) - 1) & 0x0F

    def set_output_channel(self, channel: int) -> None:
        ch = max(1, min(16, channel))
        self._target_nibble = (ch - 1) & 0x0F

    def _emit_voice(self, status: int, data: bytes) -> bytes:
        ch = status & 0x0F
        if ch in _MERGE_NIBBLES:
            status = (status & 0xF0) | self._target_nibble
            return bytes([status]) + data
        if PASS_THROUGH_OTHER_CHANNELS:
            return bytes([status]) + data
        return b""

    def feed(self, b: int) -> bytes:
        # System real-time: does not cancel running status
        if b >= 0xF8:
            return bytes([b])

        if self._sysex:
            out = bytes([b])
            if b == 0xF7:
                self._sysex = False
                self._running = 0
            return out

        if self._sys_common:
            self._collect.append(b)
            need = 2 if self._sys_common == 0xF2 else 1
            if len(self._collect) < need:
                return b""
            msg = bytes([self._sys_common]) + bytes(self._collect)
            self._collect.clear()
            self._sys_common = 0
            return msg

        # Data byte (voice continuation or stray)
        if b < 0x80:
            if self._running == 0:
                return b""
            self._collect.append(b)
            need = _voice_data_len(self._running)
            if len(self._collect) < need:
                return b""
            data = bytes(self._collect)
            self._collect.clear()
            return self._emit_voice(self._running, data)

        # Status byte
        self._collect.clear()

        if b == 0xF0:
            self._sysex = True
            self._running = 0
            return bytes([b])

        if b == 0xF2:
            self._sys_common = 0xF2
            self._running = 0
            return b""

        if b in (0xF1, 0xF3):
            self._sys_common = b
            self._running = 0
            return b""

        if b in (0xF4, 0xF5):
            self._running = 0
            return bytes([b])

        if b in (0xF6, 0xF7):
            self._running = 0
            return bytes([b])

        if 0x80 <= b <= 0xEF:
            self._running = b
            if _voice_data_len(b) == 0:
                return b""
            return b""

        self._running = 0
        return bytes([b])


def main() -> None:
    uart_in = UART(
        UART_IN_ID,
        BAUD,
        bits=8,
        parity=None,
        stop=1,
        tx=None,
        rx=Pin(UART_IN_RX_PIN),
    )
    uart_out = UART(
        UART_OUT_ID,
        BAUD,
        bits=8,
        parity=None,
        stop=1,
        tx=Pin(UART_OUT_TX_PIN),
        rx=None,
    )

    merger = _MidiRemap(TARGET_CHANNEL)
    adc = ADC(Pin(CHANNEL_POT_PIN)) if USE_CHANNEL_POT else None
    last_adc_tick = time.ticks_ms()
    pot_zone = -1
    pot_stable = 0
    last_applied_ch = TARGET_CHANNEL

    buf = bytearray(1)

    while True:
        if adc is not None:
            now = time.ticks_ms()
            if time.ticks_diff(now, last_adc_tick) >= ADC_POLL_MS:
                last_adc_tick = now
                ch_read = _channel_from_adc_u16(adc.read_u16())
                if ch_read == pot_zone:
                    pot_stable += 1
                else:
                    pot_zone = ch_read
                    pot_stable = 1
                if pot_stable >= POT_DEBOUNCE_READS and ch_read != last_applied_ch:
                    last_applied_ch = ch_read
                    merger.set_output_channel(ch_read)

        n = uart_in.readinto(buf)
        if not n:
            continue
        out = merger.feed(buf[0])
        if out:
            uart_out.write(out)


if __name__ == "__main__":
    main()
