from dataclasses import dataclass
import fontforge
import psMat

@dataclass
class FontGenInput:
    stroke_width: float
    weight_value: float
    weight_name: str
    italic: bool = False

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

weights = [
    FontGenInput(20, 400, "Regular"),
    FontGenInput(33.333, 500, "Medium"),
    FontGenInput(46.666, 600, "Semi-Bold"),
    FontGenInput(60, 700, "Bold"),
]

glyphs_ignore_weight = ["asterisk"]

def generateFont(i: FontGenInput):
    font = fontforge.open("LibertinusMono-Regular.sfd")

    font.weight = i.weight_name
    font.os2_weight = i.weight_value

    font.os2_width = OS2_WIDTH

    font.familyname = "Maki Libertinus Mono"

    font.fontname = "MakiLibertinusMono-" + i.weight_name
    font.fullname = "Maki Libertinus Mono " + i.weight_name
    filename = "MakiLibertinusMono-" + i.weight_name.replace("-", "")

    if (i.italic):
        font.fontname += " Italic"
        font.fullname += " Italic"
        filename += "Italic"

    if (font.copyright != None):
        print("Copyright not empty: " + font.copyright)
        exit(1)

    font.copyright = "Edited by https://maki.cafe"

    SCALE_MATRIX = psMat.scale(SCALE_X, 1)

    # scale first
    for glyph in font.glyphs():
        glyph.transform(SCALE_MATRIX, ("partialRefs"))

    # italicize
    if (i.italic):
        font.selection.all()
        font.italicize(-15)
        font.selection.none()

    # apply weight
    for glyph in font.glyphs():
        can_change_weight = glyph.glyphname not in glyphs_ignore_weight
        if i.stroke_width > 0 and can_change_weight:
            glyph.changeWeight(i.stroke_width, "CJK")

    font.save("fonts/" + filename + ".sfd")

    font.generate("fonts/" + filename + ".otf")
    font.generate("fonts/" + filename + ".ttf")
    font.generate("fonts/" + filename + ".woff2")

for weight in weights:
    generateFont(weight)
    weight.italic = True
    generateFont(weight)
