from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen
from typing import List, Tuple
from tensorflow import keras
from PIL import Image
from tensorflow.keras.preprocessing.image import img_to_array
import tensorflow as tf
import numpy as np
import os

from statistics import Stats


"""Global variable for saving statistics."""
global_stats = Stats()


class Loader:
    """Class for downloading images."""
    def __init__(self, source: str, threads: int):
        """Initialize list of urls and number of threads.

        :param source: the text file with list of urls
        :param threads: number of threads for multithread downloading
        """
        self.urls = Loader._get_urls(source)
        self.threads = threads

    @staticmethod
    def _get_urls(source: str, ) -> List[str]:
        """Get list of urls from the text file

        :param source: the text file with list of urls, where one line - one url
        :return: list of urls
        """
        with open(source, 'r') as file:
            result = file.readlines()
        return result

    @staticmethod
    @global_stats.download_stats()
    def download(url: str, destination: str) -> Tuple[str, int]:
        """Download image and validate file for correct status and content-type.

        :param url: url to image
        :param destination: filepath with name and extension for downloading
        :return: Tuple of filepath and number of bytes which has been downloaded
        """
        with urlopen(url, timeout=2) as response:
            if response.status != 200:
                raise Exception(f'Unsuccessfully try of downloading. Status: {response.status}. Reason: {response.reason}')
            if response.getheader('content-type') != 'image/jpeg':
                raise TypeError(f'Invalid format of the image {url}')
            data = response.read()
        with open(destination, 'wb') as file:
            file.write(data)
        return destination, len(data)

    @Stats.time_stats
    def download_images(self, image_path: str, image_format: str, number: int = None) -> List[str]:
        """Download all images with multithreading.

        :param image_path: path to the folder with all images
        :param image_format: format of the images for saving. It'll be saved to the folder and with extension
                             which called as this parameter in the lower case
        :param number: if None will be processed all the list of urls, otherwise only number elements
        :return: filenames list of downloaded images
        """
        ext = image_format.lower()
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            url_list = self.urls[:number] if number is not None and number >= 0 else self.urls
            futures = [executor.submit(Loader.download, url, os.path.join(image_path, ext, f'{i:05}.{ext}'))
                       for i, url in enumerate(url_list)]
        return [filename for filename, length in
                map(lambda future: future.result(), as_completed(futures))
                if length != 0]


class SizeAndFormatConverter:
    """Class for converting images to the only size and format."""
    def __init__(self, size: Tuple[int, int], image_format: str):
        """Initialize size and format.

        :param size: Tuple of height and width for converting images
        :param image_format: format for converting images
        """
        self.size = size
        self.format = image_format

    @staticmethod
    def change_path(source: str, image_path: str, extension: str) -> str:
        """Change folder and extension of the file.

        :param source: filepath
        :param image_path: path to the folder with images
        :param extension: the extension of in future the converted file. Set also the name of its folder

        :return: filepath of the future file
        """
        filename = os.path.split(source)[1]
        return os.path.join(image_path, extension, f'{os.path.splitext(filename)[0]}.{extension}')

    def convert(self, source: str, destination: str):
        """Convert the image file.

        :param source: source filepath before conversion
        :param destination: destination filepath after conversion
        """
        with Image.open(source) as img:
            out = img.resize(self.size)
        out.save(destination, self.format)

    @Stats.time_stats
    def convert_images(self, jpg_files: List[str], image_path: str) -> List[str]:
        """
        Convert all images with the size and the format.

        :param jpg_files: list of files for conversion
        :param image_path: path of all image files
        :return: list of converted filepaths
        """
        files = []
        extension = self.format.lower()
        for file in jpg_files:
            destination = self.change_path(file, image_path, extension)
            try:
                self.convert(file, destination)
            except Exception as ex:
                print(ex)
            else:
                files.append(destination)
                print(f'File {file} has been converted to {self.format} with {self.size} size')
        return files


class Classifier:
    """
    Class for image classification.
    """
    def __init__(self, model_path: str):
        """
        Initialize the model of the classification.

        :param model_path: path to the pretrained classification model
        """
        self.model = Classifier._load_tf_model(model_path)

    @staticmethod
    def _load_tf_model(path: str) -> keras.Model:
        """
        Load serialized keras model from the directory `path`

        :param path: directory with serialized keras model
        :return: serialized keras model
        """
        print(f"Loading keras model from {path}")
        return keras.models.load_model(path)

    @global_stats.classify_stats()
    def is_cat(self, img: Image) -> bool:
        """
        Returns True if Cat on the picture, Dog otherwise

        :param img: PIL PNG image with size 224x224
            example:
            >>> print(img)
            <PIL.PngImagePlugin.PngImageFile image mode=RGB size=224x224 at ...>
        :return: True if a cat is in the image or False if is not
        """
        img_array = tf.cast(img_to_array(img), tf.float32) / 255.0
        img_expended = np.expand_dims(img_array, axis=0)
        return self.model.predict(img_expended)[0][0] < 0.5

    @Stats.time_stats
    def classify_images(self, source_files: List[str], image_path: str):
        """
        Classify all converted images on cats and dogs.

        :param source_files: list of filepaths to converted images.
        :param image_path: path to all images.
        :return:
        """
        for file in source_files:
            filename = os.path.split(file)[1]
            with Image.open(file) as img:
                res = self.is_cat(img)
                folder = 'cats' if res else 'dogs'
                img.save(os.path.join(image_path, folder, filename))
            print(f'File {file} has been classified into {folder} folder')
