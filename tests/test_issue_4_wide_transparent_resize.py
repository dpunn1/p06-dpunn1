import os
from io import BytesIO

from PIL import Image
from tornado.testing import AsyncHTTPTestCase

from thumbor.app import ThumborServiceApp
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

IMAGES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "course", "images")
)


class WideTransparentResizeTestCase(AsyncHTTPTestCase):
    def get_app(self):
        config = Config()
        config.LOADER = "thumbor.loaders.file_loader"
        config.FILE_LOADER_ROOT_PATH = IMAGES_ROOT
        config.ALLOW_UNSAFE_URL = True
        importer = Importer(config)
        importer.import_modules()
        server = ServerParameters(
            8888, "localhost", "thumbor.conf", None, "error", None
        )
        context = Context(server=server, config=config, importer=importer)
        return ThumborServiceApp(context)

    def test_wide_resize_of_transparent_png_has_visible_pixels(self):
        response = self.fetch("/unsafe/800x20/rainbow.png")
        self.assertEqual(response.code, 200)

        image = Image.open(BytesIO(response.body)).convert("RGBA")
        self.assertEqual(image.size, (800, 20))

        alphas = [pixel[3] for pixel in image.getdata()]
        self.assertTrue(
            any(alpha > 0 for alpha in alphas),
            "every pixel of the 800x20 result is fully transparent",
        )
