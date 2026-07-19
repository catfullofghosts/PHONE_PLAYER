"""Raw matrix keypad diagnostic.

Scans the keypad and prints the raw row/column GPIO that each press activates,
independent of the looper's key mapping. Run it, press keys, read the output.
"""

import time

import board
import digitalio

ROWS = [("r1", "D26"), ("r2", "D19"), ("r3", "D12"), ("r4", "D27")]
COLS = [("c1", "D21"), ("c2", "D13"), ("c3", "D22")]

KEY_MAP = {
    ("r1", "c1"): "1", ("r1", "c2"): "2", ("r1", "c3"): "3",
    ("r2", "c1"): "4", ("r2", "c2"): "5", ("r2", "c3"): "6",
    ("r3", "c1"): "7", ("r3", "c2"): "8", ("r3", "c3"): "9",
    ("r4", "c1"): "*", ("r4", "c2"): "0", ("r4", "c3"): "#",
}

row_ios = []
for name, pin in ROWS:
    io = digitalio.DigitalInOut(getattr(board, pin))
    io.direction = digitalio.Direction.OUTPUT
    io.value = True
    row_ios.append((name, pin, io))

col_ios = []
for name, pin in COLS:
    io = digitalio.DigitalInOut(getattr(board, pin))
    io.direction = digitalio.Direction.INPUT
    io.pull = digitalio.Pull.UP
    col_ios.append((name, pin, io))

print("Diagnostic running for up to 180s. Press keys now (one at a time, hold ~1s).")
print("Reporting: row label/GPIO + every column GPIO that reads LOW.")

last_report = None
end = time.monotonic() + 180
while time.monotonic() < end:
    for row_name, row_pin, row_io in row_ios:
        row_io.value = False
        time.sleep(0.001)
        low_cols = [(cn, cp) for cn, cp, cio in col_ios if not cio.value]
        row_io.value = True
        if low_cols:
            report = (row_name, tuple(cn for cn, _ in low_cols))
            if report != last_report:
                last_report = report
                cols_txt = ", ".join(f"{cn} ({cp})" for cn, cp in low_cols)
                keys = "/".join(KEY_MAP.get((row_name, cn), "?") for cn, _ in low_cols)
                print(f"ROW {row_name} ({row_pin}) -> LOW cols: {cols_txt}  => key(s): {keys}", flush=True)
            break
    else:
        last_report = None
    time.sleep(0.01)

print("Diagnostic finished.")
