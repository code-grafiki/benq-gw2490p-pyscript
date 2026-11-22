# BenQ Eye-CareU Monitor Brightness Control

Standalone DDC/CI monitor brightness helper for the **BenQ GW2490P**.

This script is intended as a Linux replacement for the official BenQ Eye-CareU software,
which is not available on Linux.

This repository keeps only the portable control script and its documentation.
Everything else (reverse-engineering notes, decompiled snippets, integrations, etc.)
is ignored by Git.

## File

- `monitor_control.py` — minimal DDC/CI monitor control helper.

Tested on: BenQ GW2490P (MCCS 2.2, DDC/CI over I2C/HDMI).

Note: this script has only been tested on the BenQ GW2490P. Other BenQ models may
support different VCP codes or value ranges; verify with `ddcutil capabilities`
before using `--set`.

## Requirements

### Linux

- Python 3
- `ddcutil`

Install `ddcutil` with your distro package manager, for example:

```bash
sudo pacman -S ddcutil        # Arch/CachyOS
sudo apt install ddcutil      # Debian/Ubuntu
sudo dnf install ddcutil      # Fedora
```

You may also need I2C permissions:

```bash
sudo modprobe i2c-dev
sudo usermod -aG i2c $USER
```

Then log out and back in.

### Windows

- Python 3
- No extra packages; uses built-in DXVA2 APIs.

## Usage

```bash
python3 monitor_control.py --list
python3 monitor_control.py --get CODE
python3 monitor_control.py --set CODE VALUE
python3 monitor_control.py --get CODE --monitor N
```

### List monitors

```bash
python3 monitor_control.py --list
```

### Read a value

```bash
python3 monitor_control.py --get brightness
python3 monitor_control.py --get 0x10
```

### Set a value

```bash
python3 monitor_control.py --set brightness 75
python3 monitor_control.py --set 0x10 75
```

### Use a specific monitor

```bash
python3 monitor_control.py --get brightness --monitor 1
python3 monitor_control.py --set contrast 50 --monitor 1
```

## Supported codes

`CODE` can be:

- a name:
  - `brightness`
  - `contrast`
  - `volume`
  - `input_source`
  - `power_mode`
  - `vcp_version`
  - `gamma`
  - `sharpness`
  - `display_mode`
  - `manufacturer_specific_f1`, etc.
- hex: `0x10`
- decimal: `16`

## Safety notes

- Start with `--get` before `--set`.
- Prefer standard VCP codes from `ddcutil capabilities`.
- Treat unknown BenQ-specific codes as experimental.
- Avoid rapid repeated writes.
- If behavior becomes strange, power-cycle the monitor or reset via its OSD.

## Example

```bash
python3 monitor_control.py --list
python3 monitor_control.py --get brightness
python3 monitor_control.py --set brightness 40
python3 monitor_control.py --get brightness
```

## AI usage disclosure

Generative AI was used to assist in creating this script and documentation. The
resulting code was reviewed and tested by a human before use.