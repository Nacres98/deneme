"""House style: palette, fonts, sizes. Every component reads from here so a channel restyle is one file."""
from pathlib import Path
from functools import lru_cache
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "assets" / "fonts"

WHITE = (255, 255, 255)
GREEN = (0x43, 0xE3, 0x4E)
RED = (0xF0, 0x44, 0x4B)
OUTLINE = (0x17, 0x17, 0x17)
YELLOW = (0xFF, 0xD4, 0x2A)
PANEL = (18, 18, 22)

COLORS = {"w": WHITE, "g": GREEN, "r": RED, "y": YELLOW}

# sizes are for a 1080-wide canvas; components multiply by canvas scale
CAPTION_SIZE = 66
CAPTION_STROKE = 6
CAPTION_MAX_W = 620          # narrow column like the reference
CAPTION_Y = 0.64             # centre of caption block, fraction of height
HEADING_SIZE = 74
HEADING_Y = 0.115


@lru_cache(maxsize=64)
def font(size, italic=True, weight="ExtraBold"):
    f = ImageFont.truetype(str(FONTS / ("Montserrat-Italic.ttf" if italic else "Montserrat.ttf")), size)
    f.set_variation_by_name(weight if not italic else f"{weight} Italic")
    return f
