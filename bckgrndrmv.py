"""Od czarnej okrągłej ramki na zewnątrz → przezroczystość; środek (logo) zostaje."""

import math
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Wymagana biblioteka Pillow: pip install Pillow")

RING_THRESHOLD = 40
SHRINK_PX = 25


def _median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def _inner_radius(img: Image.Image, cx: float, cy: float, thresh: int, shrink: float) -> float:
    w, h = img.size
    pix = img.load()
    max_r = math.ceil(math.hypot(w, h) / 2)
    radii = []
    for i in range(360):
        angle = 2 * math.pi * i / 360
        dx, dy = math.cos(angle), math.sin(angle)
        for r in range(1, max_r + 1):
            x, y = int(cx + r * dx), int(cy + r * dy)
            if 0 <= x < w and 0 <= y < h and max(pix[x, y][0], pix[x, y][1], pix[x, y][2]) < thresh:
                radii.append(r)
                break
        else:
            radii.append(max_r)
    return max(0.0, _median(radii) - shrink)


def remove_outside_ring_as_transparent(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    ring_threshold: int = RING_THRESHOLD,
    shrink_px: float = SHRINK_PX,
) -> Path:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_path}")
    if not output_path or not str(output_path).strip() or Path(output_path) == Path("."):
        output_path = input_path.parent / f"a{input_path.stem}.png"
    else:
        output_path = Path(output_path)

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = _inner_radius(img, cx, cy, ring_threshold, shrink_px)
    pixels = list(img.getdata())

    new_data = []
    for y in range(h):
        for x in range(w):
            if math.hypot(x - cx, y - cy) <= radius:
                new_data.append(pixels[y * w + x])
            else:
                new_data.append((0, 0, 0, 0))
    img.putdata(new_data)
    img.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    import sys

    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "006.png"
    out, thresh, shrink = None, RING_THRESHOLD, SHRINK_PX
    if len(sys.argv) > 2 and sys.argv[2].strip():
        if sys.argv[2].strip().isdigit():
            thresh = int(sys.argv[2])
            if len(sys.argv) > 3 and sys.argv[3].strip().isdigit():
                shrink = int(sys.argv[3])
        else:
            out = Path(sys.argv[2])
            if len(sys.argv) > 3 and sys.argv[3].strip().isdigit():
                thresh = int(sys.argv[3])
            if len(sys.argv) > 4 and sys.argv[4].strip().isdigit():
                shrink = int(sys.argv[4])
    print(remove_outside_ring_as_transparent(inp, out, ring_threshold=thresh, shrink_px=shrink))
