import fontforge
import psMat

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
    [20, 400, "Regular"],
    [33.333, 500, "Medium"],
    [46.666, 600, "Semi-Bold"],
    [60, 700, "Bold"],
]

glyphs_ignore_weight = ["asterisk"]

for weight in weights:
    stroke_width = weight[0]
    weight_value = weight[1]
    weight_name = weight[2]

    font = fontforge.open("LibertinusMono-Regular.sfd")

    font.weight = weight_name
    font.os2_weight = weight_value

    font.os2_width = OS2_WIDTH

    font.fontname = "MakiLibertinusMono-" + weight_name
    font.familyname = "Maki Libertinus Mono"
    font.fullname = "Maki Libertinus Mono " + weight_name

    if (font.copyright != None):
        print("Copyright not empty: " + font.copyright)
        exit(1)

    font.copyright = "Edited by https://maki.cafe"

    SCALE_MATRIX = psMat.scale(SCALE_X, 1)

    for glyph in font.glyphs():
        # scale before applying weight

        glyph.transform(SCALE_MATRIX, ("partialRefs"))

        can_change_weight = glyph.glyphname not in glyphs_ignore_weight

        if stroke_width > 0 and can_change_weight:
            glyph.changeWeight(stroke_width, "CJK")

    filename = "MakiLibertinusMono-" + weight_name.replace("-", "")

    font.save("fonts/" + filename + ".sfd")

    font.generate("fonts/" + filename + ".otf")
    font.generate("fonts/" + filename + ".woff2")
