from collections.abc import Callable
from dataclasses import dataclass
from multiprocessing import Process
import psMat

@dataclass
class FontGenInput:
    stroke_width: float
    weight_value: float
    weight_name: str
    regular_glyph_widths: dict[str, int]
    italic: bool = False

    def __init__(
        self, stroke_width: float, weight_value: float, weight_name: str
    ):
        self.stroke_width = stroke_width
        self.weight_value = weight_value
        self.weight_name = weight_name
        self.regular_glyph_widths = dict()

# 100 Thin
# 200 Extra-Light
# 300 Light
# 400 Regular
# 500 Medium
# 600 Semi-Bold
# 700 Bold
# 800 Extra-Bold
# 900 Black

# 3: 75% Condensed
# 4: 87.5% Semi-Condensed
# 5: 100% Medium

# SCALE_X = 0.825
SCALE_X = 0.75
OS2_WIDTH = 3

# otherwise looks too thin
SCALE_X_ITALIC = 0.85

weights = [
    FontGenInput(20, 400, "Regular"),
    FontGenInput(33.333, 500, "Medium"),
    FontGenInput(46.666, 600, "Semi-Bold"),
    FontGenInput(60, 700, "Bold"),
]

ALT_FONT_STROKE_WIDTH_ADDITION = -15

# below are in ranges (both ends inclusive)

glyphs_from_alt_font = [
    (0x2713, 0x2717),  # check marks and crosses
    (0x2500, 0x25ff),  # box drawing, blocks and others
    (0x2800, 0x28ff),  # braille 
    0x20ac  # euro symbol
]

glyphs_ignore_weight = [
    0x2a,  # asterisk
    # from alt font
    (0x2500, 0x25ff),  # box drawing, blocks and others
    # kek bold braille characters
]

def for_each_glyph_range_array(
    glyph_range_array: list[int | tuple[int, int]] | list[tuple[int, int]],
    glyph_func: Callable[[int], bool],
):
    for glyph_range in glyph_range_array:
        if isinstance(glyph_range, int):
            if not glyph_func(glyph_range):
                return
        else:
            for unicode in range(glyph_range[0], glyph_range[1] + 1):
                if not glyph_func(unicode):
                    return

def should_ignore_weight(needle_unicode: int) -> bool:
    should_ignore = False

    def check_glyph(unicode: int) -> bool:
        if needle_unicode == unicode:
            nonlocal should_ignore
            should_ignore = True
            return False
        return True

    for_each_glyph_range_array(glyphs_ignore_weight, check_glyph)
    return should_ignore

def should_copy_from_alt_font(needle_unicode: int) -> bool:
    should_copy = False

    def check_glyph(unicode: int) -> bool:
        if needle_unicode == unicode:
            nonlocal should_copy
            should_copy = True
            return False
        return True

    for_each_glyph_range_array(glyphs_from_alt_font, check_glyph)
    return should_copy

# https://fontforge.org/docs/scripting/python/fontforge.html

def generateFont(i: FontGenInput):
    import fontforge  # cause we're doing copy and paste in parallel

    alt_font = fontforge.open("alt/IosevkaSlab-Regular.ttc")

    font = fontforge.open("libertinus/sources/LibertinusMono-Regular.sfd")

    font.weight = i.weight_name
    font.os2_weight = i.weight_value

    font.os2_width = OS2_WIDTH

    font.familyname = "Maki Libertinus Mono"

    font.fontname = "MakiLibertinusMono-" + i.weight_name
    font.fullname = "Maki Libertinus Mono " + i.weight_name
    filename = "MakiLibertinusMono-" + i.weight_name.replace("-", "")

    if i.italic:
        font.fontname += " Italic"
        font.fullname += " Italic"
        filename += "Italic"

    if font.copyright != None:
        print("Copyright not empty: " + font.copyright)
        exit(1)

    font.copyright = "Edited by https://maki.cafe"

    # copy from other font

    font_glyph_width = font["a"].width
    alt_font_glyph_width = alt_font["a"].width

    def copy_glyph_from_alt_font(unicode: int) -> bool:
        alt_font.selection.select(unicode)
        alt_font.copy()
        alt_font.selection.none()

        font.selection.select(unicode)
        font.paste()
        font.selection.none()

        glyph = font[unicode]

        # glyph is bigger than standard character. probably twice as big
        if glyph.width > alt_font_glyph_width:
            # crop by 75%
            shift_x_float = -(glyph.width - alt_font_glyph_width) * 0.25
            shift_x = int(shift_x_float)
            if shift_x != shift_x_float:
                raise Exception(
                    "glyph cropping doesn't round evenly. %d != %f" %
                    (shift_x, shift_x_float)
                )
            glyph.transform(psMat.translate(shift_x, 0), ("partialRefs"))
            glyph.width += int(shift_x)

        # scale to fit our monospace font
        glyph_scale = font_glyph_width / glyph.width
        glyph.transform(psMat.scale(glyph_scale, 1), ("partialRefs"))

        return True

    for_each_glyph_range_array(glyphs_from_alt_font, copy_glyph_from_alt_font)

    # scale first
    if i.italic:
        scale_matrix = psMat.scale(SCALE_X_ITALIC, 1)
    else:
        scale_matrix = psMat.scale(SCALE_X, 1)

    for glyph in font.glyphs():
        glyph.transform(scale_matrix, ("partialRefs"))

        if not i.italic:
            i.regular_glyph_widths[glyph.glyphname] = glyph.width

    # italicize
    if i.italic:
        font.selection.none()
        for glyph in font.glyphs():
            font.selection.select(glyph)
            font.italicize(-15)
            font.selection.none()
            glyph.width = i.regular_glyph_widths[glyph.glyphname]

    # apply weight
    for glyph in font.glyphs():
        if should_ignore_weight(glyph.unicode):
            continue

        stroke_width = i.stroke_width
        if should_copy_from_alt_font(glyph.unicode):
            stroke_width += ALT_FONT_STROKE_WIDTH_ADDITION

        if stroke_width > 0:
            glyph.changeWeight(stroke_width, "CJK")

    font.save("fonts/" + filename + ".sfd")

    font.generate("fonts/" + filename + ".otf")
    font.generate("fonts/" + filename + ".ttf")
    font.generate("fonts/" + filename + ".woff2")

def processWeight(weight: FontGenInput):
    generateFont(weight)
    weight.italic = True
    generateFont(weight)

procs: list[Process] = []

for weight in weights:
    p = Process(target=processWeight, args=[weight])
    p.start()
    procs.append(p)

for p in procs:
    p.join()
