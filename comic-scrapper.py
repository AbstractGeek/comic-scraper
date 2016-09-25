#!/usr/bin/env python3
import argparse
import bs4 as bsoup
import requests
from collections import defaultdict
# from pprint import pprint
import shutil
import os
import concurrent.futures
import subprocess


def download_image(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def readcomics_extract_chapters(url):
    comic = url.split('/')[-1]
    r = requests.get(url)
    soup = bsoup.BeautifulSoup(r.text, 'html.parser')

    chapters = defaultdict(str)
    for link in soup.find_all('a'):
        if (comic in link.get('href')) and ('chapter' in link.get('href')):
            chapter = link.get('href')
            chapter_num = int(chapter.split('-')[-1])
            if chapter_num in chapters:
                continue
            else:
                chapters[chapter_num] = chapter + '/full'

    return chapters


def readcomics_download_chapter(url, chapter_num, download_location):
    chapter_name = 'chapter-' + str(chapter_num)
    chapter_location = os.path.join(download_location, chapter_name)
    r = requests.get(url)
    soup = bsoup.BeautifulSoup(r.text, 'html.parser')
    images = [image.get('src') for image in soup.find_all(
        'img', attrs={'class': "chapter_img"})]
    filenames = [
        os.path.join(chapter_location, '%0.3d.jpg' % (i))
        for i in range(len(images))]
    urls = zip(images, filenames)
    # Create chapter folder
    if not os.path.exists(chapter_location):
        os.makedirs(chapter_location)
    # Start downloading the urls
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for image, filename in urls:
            executor.submit(download_image, image, filename)
    # Convert the folder to a comic book zip filename
    subprocess.check_output(
        ['zip', '-r', chapter_location + '.cbz', chapter_location],
        stderr=subprocess.STDOUT)
    shutil.rmtree(chapter_location)
    print(chapter_name + ': Downloaded')


def main():
    # parse input
    parser = argparse.ArgumentParser(
        description=(
            'Downloads all comics from'
            'the given url (currently works only with readcomics.tv).'
            ' Example - A url input'
            ' http://www.readcomics.tv/comic/spider-man-2016 looks '
            'for the spider-man-2016 comics in the url, downloads them all, '
            'and makes cbz files of all issues.'))

    parser.add_argument('urls', metavar='url', nargs='+',
                        help='Comic urls to download')
    parser.add_argument(
        "-l", "--location", default=os.getcwd(), help="set download location")

    args = parser.parse_args()

    for url in args.urls:
        comic = url.split('/')[-1]
        print('Downloading comic: ' + comic)
        if 'readcomics.tv' in url:
            chapters = readcomics_extract_chapters(url)

        if 'readcomics.tv' in url:
            for k in chapters:
                download_location = os.path.join(args.location, comic)
                if not os.path.exists(download_location):
                    os.makedirs(download_location)
                readcomics_download_chapter(chapters[k], k, download_location)

        print('Downloaded comic:' + url.split('/')[-1])


if __name__ == '__main__':
    main()
