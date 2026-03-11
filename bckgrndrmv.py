"""
Usuwa od czarnej okrągłej ramki na zewnątrz – wszystko na zewnątrz wewnętrznej
krawędzi tej ramki (w tym ramka i szare tło) staje się przezroczyste.
Środek (logo na białym) zostaje.
"""

import math
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Wymagana biblioteka Pillow: pip install Pillow")

# Próg: max(R,G,B) < RING_THRESHOLD uznajemy za czarną ramkę (wykrywanie krawędzi)
RING_THRESHOLD = 40
# O ile pikseli zmniejszyć promień względem wykrytej krawędzi (usuwa szary/ramkę przy ostrej krawędzi)
SHRINK_PX = 10
# Kątów do próbkowania promienia
ANGLE_STEPS = 360


def _find_inner_radius(
    img: Image.Image, cx: float, cy: float, black_threshold: int, shrink_px: float = 1.0
) -> float:
    """Wykrywa wewnętrzny promień czarnej ramki: dla każdego kąta szuka pierwszego czarnego piksela wzdłuż promienia od środka. shrink_px odejmowane od promienia."""
    w, h = img.size
    pix = img.load()
    max_r = math.ceil(math.hypot(w, h) / 2)
    radii = []

    for i in range(ANGLE_STEPS):
        angle = 2 * math.pi * i / ANGLE_STEPS
        dx, dy = math.cos(angle), math.sin(angle)
        for r in range(1, max_r + 1):
            x = int(cx + r * dx)
            y = int(cy + r * dy)
            if 0 <= x < w and 0 <= y < h:
                p = pix[x, y]
                if max(p[0], p[1], p[2]) < black_threshold:
                    radii.append(r)
                    break
        else:
            radii.append(max_r)
    return max(0.0, median(radii) - shrink_px)


def median(values: list[float]) -> float:
    n = len(values)
    if not n:
        return 0.0
    s = sorted(values)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def remove_outside_ring_as_transparent(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    ring_threshold: int = RING_THRESHOLD,
    shrink_px: float = SHRINK_PX,
) -> Path:
    """
    Wykrywa wewnętrzną krawędź czarnej okrągłej ramki, wszystko na zewnątrz (ramka + tło)
    ustawia na przezroczystość. W środku zostaje logo (białe + grafika).

    @param input_path Ścieżka do pliku PNG
    @param output_path Ścieżka wynikowa (domyślnie: a{nazwa}.png)
    @param ring_threshold max(R,G,B) < ta wartość = piksel czarnej ramki (do wykrywania okręgu)
    @param shrink_px o ile pikseli zmniejszyć promień (więcej = mniejszy okrąg, mniej szarego wokół)
    @returns Ścieżka do zapisanego pliku
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {input_path}")
    if output_path and str(output_path).strip() and Path(output_path) != Path("."):
        output_path = Path(output_path)
    else:
        output_path = input_path.parent / f"a{input_path.stem}.png"

    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    radius = _find_inner_radius(img, cx, cy, ring_threshold, shrink_px)
    pix = img.load()
    pixels = list(img.getdata())

    new_data = []
    for y in range(h):
        for x in range(w):
            dist = math.hypot(x - cx, y - cy)
            if dist <= radius:
                idx = y * w + x
                new_data.append(pixels[idx])
            else:
                new_data.append((0, 0, 0, 0))

    img.putdata(new_data)
    img.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    import sys

    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "006.png"
    out = None
    threshold = RING_THRESHOLD
    shrink = SHRINK_PX
    if len(sys.argv) > 2 and sys.argv[2].strip():
        if sys.argv[2].strip().isdigit():
            threshold = int(sys.argv[2])
            if len(sys.argv) > 3 and sys.argv[3].strip().isdigit():
                shrink = int(sys.argv[3])
        else:
            out = Path(sys.argv[2])
            if len(sys.argv) > 3 and sys.argv[3].strip().isdigit():
                threshold = int(sys.argv[3])
            if len(sys.argv) > 4 and sys.argv[4].strip().isdigit():
                shrink = int(sys.argv[4])
    result = remove_outside_ring_as_transparent(inp, out, ring_threshold=threshold, shrink_px=shrink)
    print(result)
