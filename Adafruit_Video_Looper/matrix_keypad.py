# Copyright 2025 Adafruit Industries.
# License: GNU GPLv2, see LICENSE.txt

"""3x4 matrix keypad scanner for pay-phone style control."""

import time

import digitalio

from .gpio_pins import board_pin_to_blinka, parse_board_pin_list, parse_keypad_pins

# Standard telephone keypad layout (4 rows x 3 columns).
KEY_MAP = [
    ["1", "2", "3"],
    ["4", "5", "6"],
    ["7", "8", "9"],
    ["star", "0", "hash"],
]


class MatrixKeypad:
    """Scan a 3x4 matrix keypad wired with 4 row and 3 column GPIO lines."""

    def __init__(self, row_pins, col_pins, debounce_ms=200, scan_interval_ms=10):
        if len(row_pins) != 4:
            raise ValueError("Matrix keypad requires exactly 4 row pins")
        if len(col_pins) != 3:
            raise ValueError("Matrix keypad requires exactly 3 column pins")

        self._debounce_ms = debounce_ms / 1000.0
        self._scan_interval_ms = scan_interval_ms / 1000.0

        self._rows = []
        for pin in row_pins:
            row = digitalio.DigitalInOut(board_pin_to_blinka(pin))
            row.direction = digitalio.Direction.OUTPUT
            row.value = True
            self._rows.append(row)

        self._cols = []
        for pin in col_pins:
            col = digitalio.DigitalInOut(board_pin_to_blinka(pin))
            col.direction = digitalio.Direction.INPUT
            col.pull = digitalio.Pull.UP
            self._cols.append(col)

        self._last_key = None
        self._last_press_time = 0.0

    def _scan_raw(self):
        """Return the key currently held down, or None if nothing is pressed."""
        for row_idx, row in enumerate(self._rows):
            row.value = False
            time.sleep(0.001)
            for col_idx, col in enumerate(self._cols):
                if not col.value:
                    key = KEY_MAP[row_idx][col_idx]
                    row.value = True
                    return key
            row.value = True
        return None

    def get_key(self):
        """Return a debounced key press, or None."""
        key = self._scan_raw()
        now = time.monotonic()

        if key is None:
            self._last_key = None
            return None

        if key == self._last_key and (now - self._last_press_time) < self._debounce_ms:
            return None

        self._last_key = key
        self._last_press_time = now
        return key

    def wait_scan_interval(self):
        """Sleep for the configured scan interval."""
        time.sleep(self._scan_interval_ms)


def create_keypad(config):
    """Create a MatrixKeypad from the [keypad] config section."""
    debounce_ms = config.getint("keypad", "debounce_ms", fallback=200)
    scan_interval_ms = config.getint("keypad", "scan_interval_ms", fallback=10)

    if config.has_option("keypad", "pins"):
        row_pins, col_pins = parse_keypad_pins(config.get("keypad", "pins"))
    elif config.has_option("keypad", "row_pins") and config.has_option("keypad", "col_pins"):
        row_pins = parse_board_pin_list(config.get("keypad", "row_pins"))
        col_pins = parse_board_pin_list(config.get("keypad", "col_pins"))
    else:
        raise ValueError("keypad requires 'pins' or both 'row_pins' and 'col_pins'")

    return MatrixKeypad(row_pins, col_pins, debounce_ms, scan_interval_ms)
