#!/usr/bin/env python3
"""Minimal DDC/CI monitor control helper.

Windows: uses DXVA2 physical-monitor APIs.
Linux: delegates to ddcutil when available.

Examples:
  python monitor_control.py --list
  python monitor_control.py --get brightness
  python monitor_control.py --set 0x10 50
  python monitor_control.py --set brightness 50 --monitor 1
"""

import argparse
import ctypes
import shutil
import subprocess
import sys

VCP_NAMES = {
    "brightness": 0x10,
    "contrast": 0x12,
    "color_preset": 0x14,
    "video_black_level": 0x16,
    "volume": 0x62,
    "input_source": 0x60,
    "power_mode": 0xD6,
    "vcp_version": 0xDF,
    "new_control_value": 0x02,
    "restore_factory_defaults": 0x04,
    "active_control": 0x52,
    "gamma": 0x72,
    "sharpness": 0x87,
    "screen_orientation": 0xAA,
    "asset_tag": 0xD2,
    "display_mode": 0xDC,
    "manufacturer_specific_e1": 0xE1,
    "manufacturer_specific_ee": 0xEE,
    "manufacturer_specific_f0": 0xF0,
    "manufacturer_specific_f1": 0xF1,
    "manufacturer_specific_f6": 0xF6,
    "manufacturer_specific_f8": 0xF8,
    "manufacturer_specific_fd": 0xFD,
    "manufacturer_specific_fe": 0xFE,
    "manufacturer_specific_ff": 0xFF,
}


def parse_code(value):
    value = value.strip().lower()
    if value in VCP_NAMES:
        return VCP_NAMES[value]
    if value.startswith("0x"):
        return int(value, 16)
    return int(value, 0)


class PhysicalMonitor(ctypes.Structure):
    _fields_ = [
        ("hPhysicalMonitor", ctypes.c_void_p),
        ("szPhysicalMonitorDescription", ctypes.c_wchar * 128),
    ]


def windows_monitors():
    if sys.platform != "win32":
        raise RuntimeError("Windows monitor enumeration is only available on Windows")
    user32 = ctypes.windll.user32
    dxva2 = ctypes.windll.dxva2

    monitors = []

    @ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p,
                        ctypes.POINTER(ctypes.wintypes.RECT), ctypes.c_void_p)
    def callback(hmonitor, hdc, rect, data):
        count = ctypes.c_uint32()
        if not dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(hmonitor, ctypes.byref(count)):
            return 1
        arr = (PhysicalMonitor * count.value)()
        if not dxva2.GetPhysicalMonitorsFromHMONITOR(hmonitor, count, arr):
            return 1
        for item in arr:
            monitors.append(item)
        return 1

    user32.EnumDisplayMonitors(None, None, callback, 0)
    return monitors


def windows_list():
    for i, mon in enumerate(windows_monitors()):
        print(f"{i}: {mon.szPhysicalMonitorDescription}")


def windows_get(code, index):
    monitors = windows_monitors()
    if index >= len(monitors):
        raise SystemExit(f"monitor index {index} out of range (found {len(monitors)})")
    mon = monitors[index]
    current = ctypes.c_uint32()
    maximum = ctypes.c_uint32()
    ok = ctypes.windll.dxva2.GetVCPFeatureAndVCPFeatureReply(
        mon.hPhysicalMonitor, code, None, ctypes.byref(current), ctypes.byref(maximum))
    if not ok:
        raise SystemExit("GetVCPFeatureAndVCPFeatureReply failed")
    print(f"monitor {index}: VCP 0x{code:02X} current={current.value} max={maximum.value}")


def windows_set(code, value, index):
    monitors = windows_monitors()
    if index >= len(monitors):
        raise SystemExit(f"monitor index {index} out of range (found {len(monitors)})")
    mon = monitors[index]
    ok = ctypes.windll.dxva2.SetVCPFeature(mon.hPhysicalMonitor, code, value)
    if not ok:
        raise SystemExit("SetVCPFeature failed")
    print(f"monitor {index}: set VCP 0x{code:02X} to {value}")


def linux_run(args):
    if shutil.which("ddcutil") is None:
        raise SystemExit("ddcutil is not installed; install it or run on Windows")
    if args.list:
        subprocess.run(["ddcutil", "detect"], check=False)
        return
    if args.get:
        code = parse_code(args.get)
        subprocess.run(["ddcutil", "getvcp", hex(code)], check=False)
        return
    if args.set:
        code = parse_code(args.set[0])
        value = int(args.set[1], 0)
        subprocess.run(["ddcutil", "setvcp", hex(code), str(value), "--noverify"], check=False)
        return


def main():
    parser = argparse.ArgumentParser(description="Minimal DDC/CI monitor control helper")
    parser.add_argument("--list", action="store_true", help="list monitors")
    parser.add_argument("--get", metavar="CODE", help="read a VCP code")
    parser.add_argument("--set", nargs=2, metavar=("CODE", "VALUE"), help="write a VCP code")
    parser.add_argument("--monitor", type=int, default=0, help="monitor index")
    args = parser.parse_args()

    if sys.platform != "win32":
        linux_run(args)
        return

    if args.list:
        windows_list()
    elif args.get:
        windows_get(parse_code(args.get), args.monitor)
    elif args.set:
        windows_set(parse_code(args.set[0]), int(args.set[1], 0), args.monitor)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()