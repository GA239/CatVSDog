import argparse
import io
import os.path
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
from urllib import request
from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np

from PIL import Image

cats_dir = os.path.join("photos", "cats")
dogs_dir = os.path.join("photos", "dogs")


def main(urls_file, threads_num):
    urls = read_file(urls_file)
    total_stat = Stat()
    if len(urls) == 0:
        print("There are no lines in the file")
        return
    create_dirs()
    model = load_tf_model("model")
    with ThreadPoolExecutor(max_workers=threads_num) as pool:
        jobs = [pool.submit(task, urls[ndx], ndx, model) for ndx in range(len(urls))]
        for job in as_completed(jobs):
            line_num, stat = job.result()
            print(f"Url #{line_num} have been processed (error={stat.error}, "
                  f"bytes downloaded={stat.bytes_downloaded}, time={stat.time})")
            total_stat.accumulate(stat)
    total_stat.stop()
    print(total_stat)
    print()


def create_dirs():
    os.makedirs(os.path.normpath(cats_dir), exist_ok=True)
    os.makedirs(os.path.normpath(dogs_dir), exist_ok=True)


def task(image_url, line_num, model):
    stat = Stat()
    try:
        image_data = get_image(image_url)
        stat.files_downloaded = 1
        stat.bytes_downloaded = len(image_data)
        pil_image = create_pil_image(image_data)
        if is_cat(model, pil_image):
            stat.cats_downloaded = 1
            save_dir = cats_dir
        else:
            stat.dogs_downloaded = 1
            save_dir = dogs_dir
        pil_image.save(os.path.join(save_dir, str(line_num).zfill(5) + ".png"), "PNG")
        stat.files_saved = 1
    except Exception as exception:
        stat.errors_num = 1
        stat.error = exception
    finally:
        stat.stop()
        return line_num, stat


def get_image(url):
    with request.urlopen(url) as conn:
        return conn.read()


def create_pil_image(image_data):
    return Image.open(io.BytesIO(image_data)).resize((224, 224), Image.ANTIALIAS)


def read_file(file):
    try:
        with open(file, "r") as file_obj:
            return file_obj.readlines()
    except FileNotFoundError as e:
        print(e)
        raise e


def load_tf_model(path: str) -> keras.Model:
    """
    Load serialized keras model from the directory `path`

    :param path: directory with serialized keras model
    :return: serialized keras model
    """
    print(f"Loading keras model from {path}")
    return keras.models.load_model(path)


def is_cat(model: keras.Model, img: Image) -> bool:
    """
    Returns True if Cat on the picture, Dog otherwise

    :param model: Loaded model for CatVSDog classification
    :param img: PIL PNG image with size 224x224
        example:
        >>> print(img)
        <PIL.PngImagePlugin.PngImageFile image mode=RGB size=224x224 at ...>
    :return:
    """
    img_array = tf.cast(img_to_array(img), tf.float32) / 255.0
    img_expended = np.expand_dims(img_array, axis=0)
    return model.predict(img_expended)[0][0] < 0.5


class Stat:
    def __init__(self):
        self.start_time = time()
        self.files_downloaded = 0
        self.bytes_downloaded = 0
        self.files_saved = 0
        self.cats_downloaded = 0
        self.dogs_downloaded = 0
        self.errors_num = 0
        self.error = None
        self.time = 0
        self.accumulated_time = 0

    def __str__(self):
        return f"""Total time: {self.time}
Total accumulated time: {self.accumulated_time}
Total files downloaded: {self.files_downloaded}
Total bytes downloaded: {self.bytes_downloaded}
Total errors: {self.errors_num}
Total files saved: {self.files_saved}
Cats: {self.cats_downloaded / self.files_saved * 100}%
Dogs: {self.dogs_downloaded / self.files_saved * 100}%"""

    def stop(self):
        self.time = time() - self.start_time

    def accumulate(self, stat):
        self.files_downloaded += stat.files_downloaded
        self.bytes_downloaded += stat.bytes_downloaded
        self.files_saved += stat.files_saved
        self.cats_downloaded += stat.cats_downloaded
        self.dogs_downloaded += stat.dogs_downloaded
        self.errors_num += stat.errors_num
        self.accumulated_time += stat.time


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process cats and dogs.')
    parser.add_argument('urls_file', type=str,
                        help='file with list of images URLs')
    parser.add_argument('--threads', dest='threads',
                        type=int, default=1,
                        help='number of threads used to download images (default: 1)')

    args = parser.parse_args()
    # args = parser.parse_args(["urls.txt", "--threads", "1"])

    main(args.urls_file, args.threads)
