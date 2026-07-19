# Copyright 2025 Adafruit Industries.
# License: GNU GPLv2, see LICENSE.txt

"""Helpers for resolving Raspberry Pi pin numbers to Blinka pins."""

import board

# Physical (BOARD) header pin number -> BCM GPIO number.
BOARD_TO_BCM = {
    3: 2,
    5: 3,
    7: 4,
    8: 14,
    10: 15,
    11: 17,
    12: 18,
    13: 27,
    15: 22,
    16: 23,
    18: 24,
    19: 10,
    21: 9,
    22: 25,
    23: 11,
    24: 8,
    26: 7,
    27: 0,
    28: 1,
    29: 5,
    31: 6,
    32: 12,
    33: 13,
    35: 19,
    36: 16,
    37: 26,
    38: 20,
    40: 21,
}


def parse_board_pin_list(pin_list_string):
    """Parse a comma-separated pin list into BCM GPIO numbers."""
    pins = []
    for part in pin_list_string.split(","):
        part = part.strip()
        if not part:
            continue
        pins.append(parse_pin_token(part))
    return pins


def parse_pin_token(token):
    """Parse a pin into a BCM GPIO number.

    Accepted forms (optional keypad label prefix like r4:):
      gpio12 / bcm12 / D12  -> BCM 12
      32                    -> BOARD physical pin 32 -> BCM 12
      r4:gpio27             -> BCM 27
    """
    token = token.strip()
    if not token:
        raise ValueError("Empty pin token")

    if ":" in token:
        token = token.split(":", 1)[1].strip()

    token_lower = token.lower()
    if token_lower.startswith("r") or token_lower.startswith("c"):
        raise ValueError(
            f"Pin label '{token}' has no GPIO number — use r4:gpio27 or r4:13"
        )

    for prefix in ("gpio", "bcm", "d"):
        if token_lower.startswith(prefix):
            rest = token_lower[len(prefix):]
            if rest.isdigit():
                return int(rest)

    try:
        board_pin = int(token)
    except ValueError as err:
        raise ValueError(f"Invalid pin token: {token}") from err

    bcm = BOARD_TO_BCM.get(board_pin)
    if bcm is None:
        raise ValueError(f"Unsupported BOARD pin number: {board_pin}")
    return bcm


def parse_keypad_pins(pins_string):
    """Parse keypad wiring in order r4,r3,r2,r1,c3,c2,c1.

    Returns (row_pins, col_pins) as BCM numbers ordered for scanning:
    rows top-to-bottom (r1..r4), columns left-to-right (c1..c3).
    """
    tokens = [part.strip() for part in pins_string.split(",") if part.strip()]
    if len(tokens) != 7:
        raise ValueError(
            "keypad pins must list exactly 7 entries in order: r4,r3,r2,r1,c3,c2,c1"
        )

    pins = [parse_pin_token(token) for token in tokens]
    # Config order is r4..r1 and c3..c1; scanner needs r1..r4 and c1..c3.
    row_pins = list(reversed(pins[0:4]))
    col_pins = list(reversed(pins[4:7]))
    return row_pins, col_pins


def bcm_to_blinka(bcm_pin):
    """Return the Blinka board pin object for a BCM GPIO number."""
    blinka_name = f"D{int(bcm_pin)}"
    if not hasattr(board, blinka_name):
        raise ValueError(f"Unsupported BCM GPIO number: {bcm_pin}")
    return getattr(board, blinka_name)


# Backwards-compatible name used by older call sites.
def board_pin_to_blinka(pin):
    """Resolve a BCM GPIO number (preferred) to a Blinka pin object."""
    return bcm_to_blinka(pin)
