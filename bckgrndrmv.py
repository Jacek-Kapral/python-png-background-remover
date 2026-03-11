"""
Usuwa czarną ramkę i czarne tło z PNG – zamienia je na przezroczystość.
Piksele uznane za czerń (R,G,B poniżej progu) dostają alpha=0.
"""

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Wymagana biblioteka Pillow: pip install Pillow")

# Próg: max(R,G,B) <= BLACK_THRESHOLD → uznaj za czerń i ustaw alpha=0 (podbij przy „ciemnej” ramce)
BLACK_THRESHOLD = 80


def _pixel_stats(input_path: str | Path) -> None:
    """Wypisuje statystyki max(R,G,B) w obrazie – do doboru progu."""
    img = Image.open(input_path).convert("RGBA")
    pixels = list(img.getdata())
    values = [max(r, g, b) for r, g, b, _ in pixels]
    values.sort()
    n = len(values)
    p = lambda q: values[int((n - 1) * q / 100)] if n else 0
    print(f"max(R,G,B) w obrazie: min={values[0]}, 5%={p(5)}, 25%={p(25)}, 50%={p(50)}, 75%={p(75)}, 95%={p(95)}, max={values[-1]}")
    print("Ustaw próg między wartościami 'tła' a 'ramki/grafiki', np. python bckgrndrmv.py 006.png '' 50")


def remove_black_as_transparent(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    black_threshold: int = BLACK_THRESHOLD,
) -> Path:
    """
    Wczytuje PNG, zamienia piksele czarne (i ciemne) na przezroczyste, zapisuje PNG.

    @param input_path Ścieżka do pliku PNG
    @param output_path Ścieżka wynikowa (domyślnie: a{nazwa}.png obok wejścia, np. 006.png → a006.png)
    @param black_threshold Piksele z max(R,G,B) <= tej wartości stają się przezroczyste
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
    pixels = list(img.getdata())

    new_data = []
    for r, g, b, a in pixels:
        if max(r, g, b) <= black_threshold:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)
    img.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    import sys

    if "--stats" in sys.argv:
        inp = next((Path(a) for a in sys.argv[1:] if a != "--stats" and a.strip()), Path(__file__).parent / "006.png")
        _pixel_stats(inp)
        sys.exit(0)

    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "006.png"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].strip() else None
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else BLACK_THRESHOLD
    result = remove_black_as_transparent(inp, out, black_threshold=threshold)
    print(result)
