"""
Usuwa czarną ramkę i czarne tło z PNG – zamienia je na przezroczystość.
Piksele uznane za czerń (R,G,B poniżej progu) dostają alpha=0.
"""

from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Wymagana biblioteka Pillow: pip install Pillow")

# Próg: max(R,G,B) <= BLACK_THRESHOLD → uznaj za czerń i ustaw alpha=0
BLACK_THRESHOLD = 30


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
    output_path = Path(output_path) if output_path else input_path.parent / f"a{input_path.stem}.png"

    img = Image.open(input_path).convert("RGBA")
    data = img.getdata()

    new_data = []
    for item in data:
        r, g, b, a = item
        if r <= black_threshold and g <= black_threshold and b <= black_threshold:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    import sys

    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "006.png"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    result = remove_black_as_transparent(inp, out)
    print(result)
