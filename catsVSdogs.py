"""the task can be found there https://github.com/GA239/CatVSDog
fork the repo and implement the solution."""
import argparse

from util import Loader, SizeAndFormatConverter, Classifier, global_stats


def read_args():
    """Read args and validate from the parameters of application's running.

    :return: list of args
    """
    parser = argparse.ArgumentParser(description='Download and process cats and dogs pictures with multithreading')
    parser.add_argument('urllist', help='url list with cats and dogs pictures')
    parser.add_argument('--threads', type=int, default=1,
                        help='set up number of threads for multithread downloading (default 1)')
    parser.add_argument('--elems', type=int, default=None,
                        help='Number of elements to take from list for processing')
    return parser.parse_args()


@global_stats.total_time_stats()
def process(source: str, threads: int, number: int = None):
    """Pipeline of working this application.

    :param source: filename which contains url list with images of cats and dogs
    :param threads: number of threads for multithread downloading
    :param number: number of elements to take from urllist. If None - take all the elements
    """
    image_path = 'img'

    loader = Loader(source=source, threads=threads)
    source_files = loader.download_images(image_path=image_path, image_format='JPEG', number=number)

    converter = SizeAndFormatConverter(size=(224, 224), image_format='PNG')
    png_files = converter.convert_images(source_files, image_path=image_path)

    classifier = Classifier(model_path='model')
    classifier.classify_images(png_files, image_path=image_path)


if __name__ == "__main__":
    args = read_args()
    process(source=args.urllist, threads=args.threads, number=args.elems)
    print(global_stats)

"""
Results of execution (for demo):

Downloaded files: 54
Downloaded bytes: 6208667
Download errors: 46
Total images: 54
Cats percentage: 68.52%
Dogs percentage: 31.48%
Total execution time with urllist.txt source, 1 threads and 100 elements is 70.67821097373962 seconds
--------------------------
Downloaded files: 55
Downloaded bytes: 6335708
Download errors: 45
Total images: 55
Cats percentage: 69.09%
Dogs percentage: 30.91%
Total execution time with urllist.txt source, 4 threads and 100 elements is 26.973176956176758 seconds
-------------------------
"""