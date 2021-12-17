#!/bin/bash

rm -rf photos
echo "non parallel processing:"
python catsVSdogs.py urls.txt --threads 1
echo

rm -rf photos
echo "parallel processing with 4 threads:"
python catsVSdogs.py urls.txt --threads 4
echo

rm -rf photos
echo "parallel processing with 6 threads:"
python catsVSdogs.py urls.txt --threads 8


