"""
Mechaniczne wycięcie okręgu: środek = środek obrazu, promień = podany (px).
Wszystko poza kołem → przezroczystość. Bez wykrywania kolorów ani alpha.
"""

import math
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Wymagana biblioteka Pillow: pip install Pillow")

# Domyślny promień (px) dla 218x217
DEFAULT_RADIUS = 154


def crop_circle(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    radius_px: float = DEFAULT_RADIUS,
    center_x: float | None = None,
    center_y: float | None = None,
) -> Path:
    """
    Wszystko w odległości > radius_px od środka ustawia na przezroczystość.
    Środek domyślnie = środek obrazu (width/2, height/2).
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_path}")
    if not output_path or not str(output_path).strip() or Path(output_path) == Path("."):
        output_path = input_path.parent / f"a{input_path.stem}.png"
    else:
        output_path = Path(output_path)

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx = (w - 1) / 2.0 if center_x is None else center_x
    cy = (h - 1) / 2.0 if center_y is None else center_y
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

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    out = None
    radius: float | None = None

    if len(sys.argv) > 2 and sys.argv[2].strip():
        a2 = sys.argv[2].strip()
        if a2.replace(".", "", 1).isdigit():
            radius = float(a2)
        else:
            out = Path(a2)
            if len(sys.argv) > 3 and sys.argv[3].strip().replace(".", "", 1).isdigit():
                radius = float(sys.argv[3])

    if radius is None:
        try:
            user = input(f"Promień koła w pikselach [domyślnie {DEFAULT_RADIUS}]: ").strip()
            if user and user.replace(".", "", 1).isdigit():
                radius = float(user)
            else:
                radius = DEFAULT_RADIUS
        except EOFError:
            radius = DEFAULT_RADIUS

    if path.is_dir():
        for f in sorted(path.glob("*.png")):
            if f.stem.startswith("a"):
                continue
            crop_circle(f, None, radius_px=radius)
            print(f"{f.name} → a{f.stem}.png")
    else:
        inp = path if path.is_file() else Path(__file__).parent / "006.png"
        print(crop_circle(inp, out, radius_px=radius))
