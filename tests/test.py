import unittest
import os
from PIL import Image
from util import SizeAndFormatConverter


class TestPNGConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """Initialize the instance of converter and start path to all images"""
        cls.converter = SizeAndFormatConverter((224, 224), 'PNG')
        cls.image_path = os.path.join('..', 'img')

    def test_change_path(self):
        """Test method of changing extension and path to the file."""
        data = os.path.join(self.image_path, 'jpeg', '324lnkn45ljf.jpeg')
        result = SizeAndFormatConverter.change_path(data, self.image_path, 'png')
        expected = os.path.join(self.image_path, 'png', '324lnkn45ljf.png')
        self.assertEqual(result, expected)

    def test_convert_img_non_equal(self):
        """Test method for checking if we convert file then size and format is different."""
        data = os.path.join(self.image_path, 'jpeg', '00000.jpeg')
        destination = SizeAndFormatConverter.change_path(data, self.image_path, self.converter.format.lower())
        self.converter.convert(data, destination)
        with Image.open(destination) as img:
            result = (img.size, img.format)
        with Image.open(data) as source:
            expected = (source.size, source.format)
        self.assertNotEqual(result, expected)

    def test_convert_correct_format(self):
        """Test method for checking if the file has been converted correctly."""
        data = os.path.join(self.image_path, 'jpeg', '00000.jpeg')
        destination = SizeAndFormatConverter.change_path(data, self.image_path, self.converter.format.lower())
        self.converter.convert(data, destination)
        with Image.open(destination) as img:
            result = (img.size, img.format)
        expected = (self.converter.size, self.converter.format)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
