import unittest

from catsVSdogs import Stat


class StatClassTestCase(unittest.TestCase):

    def test_new_instance(self):
        stat = Stat()
        self.assertEqual(stat.time, 0)
        self.assertEqual(stat.files_saved, 0)
        self.assertEqual(stat.error, None)
        self.assertEqual(stat.files_downloaded, 0)
        self.assertEqual(stat.cats_downloaded, 0)
        self.assertEqual(stat.errors_num, 0)
        self.assertEqual(stat.bytes_downloaded, 0)
        self.assertEqual(stat.dogs_downloaded, 0)
        self.assertEqual(stat.accumulated_time, 0)

    def test_accumulate(self):
        total_stat = Stat()
        stat = Stat()
        stat.error = Exception()
        stat.files_saved = 4
        stat.files_downloaded = 10
        stat.cats_downloaded = 6
        stat.errors_num = 1
        stat.bytes_downloaded = 1024
        stat.dogs_downloaded = 4
        stat.stop()
        self.assertNotEqual(stat.time, 0)
        total_stat.accumulate(stat)
        self.assertEqual(total_stat.accumulated_time, stat.time)
        self.assertEqual(total_stat.error, None)
        self.assertEqual(total_stat.files_saved, stat.files_saved)
        self.assertEqual(total_stat.files_downloaded, stat.files_downloaded)
        self.assertEqual(total_stat.cats_downloaded, stat.cats_downloaded)
        self.assertEqual(total_stat.errors_num, stat.errors_num)
        self.assertEqual(total_stat.bytes_downloaded, stat.bytes_downloaded)
        self.assertEqual(total_stat.dogs_downloaded, stat.dogs_downloaded)

    def test_stop_time(self):
        stat = Stat()
        stat.stop()
        self.assertGreater(stat.time, 0)


if __name__ == '__main__':
    unittest.main()
