"""Wycięcie koła z PNG: środek obrazu, promień w pikselach."""

import math
from pathlib import Path

from PIL import Image

DEFAULT_RADIUS = 154.0


def crop_circle(input_path: str | Path, radius_px: float, output_path: str | Path | None = None) -> Path:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    if not output_path:
        output_path = input_path.parent / f"a{input_path.stem}.png"
    else:
        output_path = Path(output_path)

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    pixels = list(img.getdata())

    new_data = []
    for y in range(h):
        for x in range(w):
            if math.hypot(x - cx, y - cy) <= radius_px:
                new_data.append(pixels[y * w + x])
            else:
                new_data.append((0, 0, 0, 0))

    img.putdata(new_data)
    img.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]
    path = Path(args[0]) if args else Path.cwd()
    radius = float(args[1]) if len(args) > 1 else DEFAULT_RADIUS

    if path.is_dir():
        for f in sorted(path.glob("*.png")):
            if f.stem.startswith("a"):
                continue
            out = crop_circle(f, radius)
            print(f"{f.name} → {out.name}")
    else:
        inp = path if path.is_file() else Path(__file__).parent / "006.png"
        out = crop_circle(inp, radius)
        print(out)
