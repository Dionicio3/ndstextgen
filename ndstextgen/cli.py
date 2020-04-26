import codecs
import os
import click
from PIL import Image
from hacktools import common, nitro
__version__ = "1.3.0"


@common.cli.command(context_settings=dict(show_default=True))
@click.argument("font")
@click.argument("text")
@click.option("--out",     default="text.png",    help="Output file.")
@click.option("--vert",    default=2,             help="Vertical spacing between lines.")
@click.option("--fw",      default=0,             help="Use a fixed width instead of the VWF values in the font.")
@click.option("--color",   default="black",       help="Color to apply to the font.")
@click.option("--bg",      default="transparent", help="Background color.")
@click.option("--width",   default=256,           help="Set width for the generated image.")
@click.option("--height",  default=256,           help="Set height for the generated image.")
@click.option("--no-crop", is_flag=True,          help="Don't crop the image before saving it.")
def gen(font, text, out, vert, fw, color, bg, width, height, no_crop):
    """FONT is the font file, .NFTR extension can be omitted.

    TEXT is the text to write. "\\n" can be used for a line break. Can be the name of a UTF-8 file to read the text from."""
    if not os.path.isfile(font):
        if not font.lower().endswith(".nftr"):
            font = font + ".NFTR"
        if not os.path.isfile(font):
            common.logMessage("[ERROR] Font", font, "not found")
            return
    if os.path.isfile(text):
        with codecs.open(text, "r", "utf-8") as f:
            text = f.read().replace("\r\n", "\\n").replace("\n", "\\n")
    text = text.replace("\\n", "\n")
    # Read the font data
    nftr = nitro.readNFTR(font, True)
    # Create the empty image
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    # Generate the text
    currentx = 0
    currenty = 0
    for i in range(len(text)):
        c = text[i]
        if c == "\n":
            currentx = 0
            currenty += nftr.height + vert
            continue
        if c not in nftr.glyphs:
            common.logMessage("[WARNING] Glyph", hex(ord(c)), "not found.")
            c = " "
        glyph = nftr.glyphs[c]
        glyphdata = nftr.plgc[glyph.index]
        img.paste(glyphdata, (currentx + glyph.start, currenty))
        if fw > 0:
            currentx += fw
        else:
            currentx += glyph.length
    # Tint the image
    if color != "black":
        alpha = img.getchannel("A")
        img = Image.new("RGBA", (img.width, img.height), color)
        img.putalpha(alpha)
    # Crop and save the image
    if not no_crop:
        bbox = img.getbbox()
        img = img.crop(bbox)
    if bg == "transparent":
        final = img
    else:
        final = Image.new("RGBA", (img.width, img.height), bg if bg != "transparent" else (0, 0, 0, 0))
        final.paste(img, (0, 0), img)
    final.save(out, "PNG")


def main():
    click.echo("ndstextgen version " + __version__)
    gen()
