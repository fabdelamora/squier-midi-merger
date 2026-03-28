# Merger MIDI Squier / RB3

**Idioma:** [English →](../README.md) · **Español** (esta página)

---

Caja con **Raspberry Pi Pico** + **MicroPython**: junta los **canales MIDI 1–6** (guitarra **Squier** / Pro Guitar de Rock Band 3, un canal por cuerda) en **un solo canal de salida** para que sintes que solo escuchan un canal (p. ej. **Moog Mother-32**) respondan a **todas las cuerdas**. Entrada y salida **DIN de 5 pines**, **potenciómetro** opcional en **GP26** para elegir canal de salida **1–16**.

---

## Tabla de contenidos

1. [Lista de compras](#1-lista-de-compras)  
2. [Diagrama de conexiones y pines](#2-diagrama-de-conexiones-y-pines)  
3. [Orden de montaje](#3-orden-de-montaje-sugerido)  
4. [Software en el Pico](#4-software-en-el-pico)  
5. [Configuración](#5-configuración)  
6. [Primera prueba](#6-primera-prueba)  
7. [Más documentación](#7-más-documentación)  
8. [Licencia](#licencia)

---

## 1. Lista de compras

Úsala como checklist al pedir piezas (AliExpress, tienda local, etc.).

| ☐ | Cant. | Artículo |
|---|-------|----------|
| ☐ | 1 | **Raspberry Pi Pico** (o placa RP2040 con el mismo pinout) |
| ☐ | 2 | **Jack hembra MIDI DIN 5 pines** (chasis o PCB) — IN + OUT |
| ☐ | 1 | **Optoacoplador** — 6N138 *o* 6N137 *o* PC900 (DIP cómodo en protoboard) |
| ☐ | 1 | **Diodo** 1N4148 o 1N914 *(opcional)* — protección inversa del LED del opto |
| ☐ | 3 | **Resistencia 220 Ω** (¼ W) — × MIDI IN, 2× MIDI OUT |
| ☐ | 1 | **Resistencia 10 kΩ** — pull-up salida opto → 3,3 V |
| ☐ | 1 | **Potenciómetro 10 kΩ lineal (B10K)** — canal MIDI de salida |
| ☐ | 1 | **Condensador cerámico 100 nF** *(opcional)* — cursor → GND, ADC más estable |
| ☐ | 1 | **Protoboard / placa perforada / PCB pequeño** |
| ☐ | 1 | **Cable USB** — el que lleve tu Pico (**Micro-USB** o **USB-C**) para alimentación |
| ☐ | — | **Cables MIDI** — guitarra → caja, caja → sinte (si no los tienes) |

**Notas**

- La lógica del Pico es solo **3,3 V**; no metas 5 V en los GPIO.  
- BOM detallado por tipo de componente: **[HARDWARE.md](../HARDWARE.md)** (en inglés).

---

## 2. Diagrama de conexiones y pines

**Diagrama completo ASCII + Mermaid:** **[WIRING.md](WIRING.md)** — úsalo al soldar (circuito MIDI IN con opto, resistencias MIDI OUT, pot, pistas del 6N138).

**Resumen de pines del Pico** (debe coincidir con [`firmware/main.py`](../firmware/main.py)):

| Señal | Pin Pico |
|-------|----------|
| MIDI IN (salida del optoacoplador) | **GP1** (UART0 RX) |
| MIDI OUT (hacia DIN) | **GP8** (UART1 TX) |
| Cursor del pot de canal | **GP26** (ADC) |
| GND | Masa común jacks, pot, opto, Pico |

**Jack DIN** (confirma numeración en el **datasheet de tu jack** — cara de soldadura):

- **Pin 2** — masa / blindaje  
- **Pin 4** — retorno (IN desde guitarra; OUT “lazy” a 3,3 V vía 220 Ω)  
- **Pin 5** — caliente (IN vía 220 Ω al LED del opto; OUT desde GP8 vía 220 Ω)

---

## 3. Orden de montaje (sugerido)

1. **Alimentación y Pico:** monta el Pico en protoboard; solo USB para alimentar (no hace falta 5 V en MIDI).  
2. **MIDI IN:** DIN → 220 Ω → **LED** del opto (pines según **[WIRING.md](WIRING.md)** y **tu hoja de datos del opto**).  
3. **Lado lógico del opto:** salida colector abierto + **10 kΩ** pull-up a **3V3** → **GP1**; GND y VCC del opto según datasheet (suele ser **3,3 V**).  
4. **MIDI OUT:** **GP8** → 220 Ω → pin **5** del jack OUT; **3V3** → 220 Ω → pin **4**; **GND** → pin **2**.  
5. **Pot:** extremos a **GND** y **3V3**, cursor a **GP26**; opcional **100 nF** cursor → GND.  
6. **Si aún no tienes el pot cableado:** pon `USE_CHANNEL_POT = False` en `main.py` antes del primer arranque (ADC al aire = canales aleatorios).

---

## 4. Software en el Pico

### 4.1 Instalar MicroPython (una vez)

1. Descarga el **.uf2** para tu placa en **[MicroPython — Raspberry Pi Pico](https://micropython.org/download/RPI_PICO/)** (usa **RPI_PICO_W** si tienes Pico W).  
2. Desconecta el Pico, mantén **BOOTSEL**, conecta USB — aparece la unidad **RPI-RP2**.  
3. Arrastra el **.uf2** a esa unidad; el Pico reinicia con MicroPython.

### 4.2 Copiar el firmware

El código del merger está en **[`firmware/main.py`](../firmware/main.py)**. En el Pico debe llamarse **`main.py`** para que arranque solo.

**Opción A — Thonny (interfaz gráfica)**  

1. Instala [Thonny](https://thonny.org/).  
2. Abajo a la derecha → intérprete **MicroPython (Raspberry Pi Pico)**.  
3. Abre `firmware/main.py` del repo → **Archivo → Guardar como…** → **Raspberry Pi Pico** → guarda como **`main.py`**.

**Opción B — mpremote (terminal)**  

```bash
cd /ruta/a/squier-midi-merger
pip install mpremote   # si hace falta
mpremote cp firmware/main.py :main.py
```

### 4.3 Reiniciar

Desconecta y vuelve a conectar USB (o **Detener/Reiniciar** en Thonny). El merger corre solo; el PC solo hace falta para **alimentar** en uso normal.

Más detalle: **[SOFTWARE.md](SOFTWARE.md)** (en inglés).

---

## 5. Configuración

Edita la parte superior de **`main.py`** en el Pico (Thonny o mpremote):

| Ajuste | Función |
|--------|---------|
| `TARGET_CHANNEL` | Se usa si `USE_CHANNEL_POT` es `False`, y como canal inicial hasta que el pot se estabilice. |
| `USE_CHANNEL_POT` | `True` = lee **GP26** para canal de salida **1–16**. `False` = solo `TARGET_CHANNEL` fijo. |
| `MERGE_CHANNELS` | Por defecto `(1,…,6)` para canales de cuerdas Squier / RB3. |
| `PASS_THROUGH_OTHER_CHANNELS` | `True` = reenvía otros canales MIDI sin cambiar; `False` = los ignora. |

Configura el **canal MIDI de recepción** del sinte para que coincida con la salida del merger (muchos aparatos usan por defecto el **canal 1**).

---

## 6. Primera prueba

1. **MIDI OUT** de la **Squier** (o guitarra) → **MIDI IN** de la caja.  
2. **MIDI OUT** de la caja → **MIDI IN** del sinte.  
3. **USB** → cargador o power bank (Pico).  
4. Toca cada cuerda — el sinte debería seguir **todas** las cuerdas en **un** canal.  
5. Notas colgadas: **Start + Back** en la Squier (pánico MIDI) o corta y vuelve a dar alimentación.

---

## 7. Más documentación

| Documento | Contenido |
|-----------|-----------|
| [README (English)](../README.md) | Guía principal en inglés |
| [HARDWARE.md](../HARDWARE.md) | BOM, notas DIN, consejos de montaje |
| [WIRING.md](WIRING.md) | Diagramas de cableado completos |
| [SOFTWARE.md](SOFTWARE.md) | Comportamiento del parser, UART, límites |
| [GLOSSARY.md](GLOSSARY.md) | Términos (UART, optoacoplador, ADC, …) |

---

## Licencia

Hardware y firmware de este repositorio: úsalos bajo tu responsabilidad en proyectos personales. Las marcas registradas de terceros (Fender, Squier, Rock Band, Moog, Raspberry Pi, etc.) son de sus propietarios.
