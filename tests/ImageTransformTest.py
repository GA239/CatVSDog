import unittest

from PIL import Image

from catsVSdogs import create_pil_image


class ImageTransformTestCase(unittest.TestCase):
    def test_create_pil_image(self):
        with Image.open("data/dog.jpeg") as image:
            w, h = image.size
            self.assertNotEqual(w, 224, "Source width is not equal to 224")
            self.assertNotEqual(h, 224, "Source height is not equal to 224")
        with open("data/dog.jpeg", "rb") as file:
            image = create_pil_image(file.read())
            w, h = image.size
            self.assertEqual(w, 224, "Source width is equal to 224")
            self.assertEqual(h, 224, "Source height is equal to 224")


if __name__ == '__main__':
    unittest.main()
