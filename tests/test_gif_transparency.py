from io import BytesIO
import unittest

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_palette_gif_with_transparent_background():
    img = Image.new("P", (40, 40), 0)
    palette = [0, 0, 0] + [0, 0, 255] + [0, 0, 0] * 254
    img.putpalette(palette)
    for x in range(10, 30):
        for y in range(10, 30):
            img.putpixel((x, y), 1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


class GifTransparencyTestCase(unittest.TestCase):
    def resize_to_gif(self, buffer):
        config = Config(PILLOW_PRESERVE_INDEXED_MODE=True, ALLOW_ANIMATED_GIFS=False)
        engine = Engine(Context(config=config))
        engine.extension = ".gif"
        engine.image = engine.create_image(buffer)
        engine.resize(20, 20)
        return engine.read(".gif")

    def test_resized_gif_keeps_transparent_background(self):
        source = make_palette_gif_with_transparent_background()
        result = self.resize_to_gif(source)
        image = Image.open(BytesIO(result))

        self.assertIsNotNone(
            image.info.get("transparency"),
            "resized GIF lost its transparency index",
        )
        rgba = image.convert("RGBA")
        self.assertEqual(
            rgba.getpixel((0, 0))[3],
            0,
            "corner that was transparent in the source is now opaque",
        )
        self.assertEqual(
            rgba.getpixel((10, 10))[3],
            255,
            "blue disc should stay opaque",
        )

    def test_opaque_palette_gif_stays_opaque(self):
        img = Image.new("P", (40, 40), 1)
        img.putpalette([0, 0, 0, 0, 0, 255] + [0, 0, 0] * 254)
        buffer = BytesIO()
        img.save(buffer, "GIF")
        result = self.resize_to_gif(buffer.getvalue())
        image = Image.open(BytesIO(result))

        self.assertIsNone(image.info.get("transparency"))
