# Copyright 2025 Adafruit Industries.
# License: GNU GPLv2, see LICENSE.txt

"""Helpers for resolving Raspberry Pi BOARD (physical) pin numbers to Blinka pins."""

import board

# Physical (BOARD) pin number -> Blinka attribute name (BCM GPIO).
BOARD_TO_BLINKA = {
    3: "D2",
    5: "D3",
    7: "D4",
    8: "D14",
    10: "D15",
    11: "D17",
    12: "D18",
    13: "D27",
    15: "D22",
    16: "D23",
    18: "D24",
    19: "D10",
    21: "D9",
    22: "D25",
    23: "D11",
    24: "D8",
    26: "D7",
    29: "D5",
    31: "D6",
    32: "D12",
    33: "D13",
    35: "D19",
    36: "D16",
    37: "D26",
    38: "D20",
    40: "D21",
}


def parse_board_pin_list(pin_list_string):
    """Parse a comma-separated list of BOARD pin numbers."""
    pins = []
    for part in pin_list_string.split(","):
        part = part.strip()
        if not part:
            continue
        pins.append(parse_pin_token(part))
    return pins


def parse_pin_token(token):
    """Parse a BOARD pin number, optionally prefixed with a label (e.g. r4:16)."""
    token = token.strip()
    if not token:
        raise ValueError("Empty pin token")

    if ":" in token:
        token = token.split(":", 1)[1].strip()

    token_lower = token.lower()
    if token_lower.startswith("r") or token_lower.startswith("c"):
        raise ValueError(
            f"Pin label '{token}' has no BOARD number — use r4:16 or just 16"
        )

    try:
        return int(token)
    except ValueError as err:
        raise ValueError(f"Invalid pin token: {token}") from err


def parse_keypad_pins(pins_string):
    """Parse keypad wiring in order r4,r3,r2,r1,c3,c2,c1.

    Each entry may be a BOARD pin number or a labeled pin such as r4:16.
    Column entries are listed right-to-left (c3,c2,c1) to match typical
    keypad silkscreen; they are reversed internally for left-to-right scanning.
    """
    tokens = [part.strip() for part in pins_string.split(",") if part.strip()]
    if len(tokens) != 7:
        raise ValueError(
            "keypad pins must list exactly 7 entries in order: r4,r3,r2,r1,c3,c2,c1"
        )

    pins = [parse_pin_token(token) for token in tokens]
    row_pins = pins[0:4]
    col_pins = list(reversed(pins[4:7]))
    return row_pins, col_pins


def board_pin_to_blinka(board_pin):
    """Return the Blinka board pin object for a physical BOARD pin number."""
    blinka_name = BOARD_TO_BLINKA.get(int(board_pin))
    if blinka_name is None:
        raise ValueError(f"Unsupported BOARD pin number: {board_pin}")
    return getattr(board, blinka_name)
