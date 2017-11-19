#!/usr/bin/env python3
import argparse
import bs4 as bsoup
import requests
from collections import defaultdict, OrderedDict
import shutil
import os
import re
import concurrent.futures
from urllib.parse import urlparse, urljoin
from urllib3.exceptions import InsecureRequestWarning
from zipfile import ZipFile, ZIP_DEFLATED
from random import shuffle, uniform
from time import sleep
from copy import deepcopy
import img2pdf


class Comic:
    """Comic class. Contains chapters."""

    def __init__(self, comic_url, program_args, verify_https):
        """Init function. Creates chapters for the given comic."""
        self.url = comic_url
        self.name = comic_url.split('/')[-1] \
            if comic_url.split('/')[-1] else comic_url.split('/')[-2]
        # Set download location
        self.download_location = os.path.abspath(
            os.path.join(program_args.location, self.name))
        if not os.path.exists(self.download_location):
            os.makedirs(self.download_location)
        # Set threads and retry values
        self.chapter_threads = program_args.chapterthreads
        self.page_threads = program_args.pagethreads
        self.wait_time = program_args.waittime
        self.max_retries = program_args.retries
        self.file_format = program_args.format
        # Set verify mode
        self.verify_https = verify_https
        # Get all chapters and mode of download
        self.all_chapters = self.get_chapters()

    def get_chapters(self):
        """Get list of chapters."""
        if 'mangafox' in self.url:
            self.mode = ['manga', 'mangafox']
            chapters = self.manga_extract_chapters()
        elif 'mangahere' in self.url:
            self.mode = ['manga', 'mangahere']
            chapters = self.manga_extract_chapters()
        elif 'readcomics' in self.url:
            self.mode = ['comic']
            chapters = self.comic_extract_chapters()
        else:
            raise ValueError('The scraper currently only supports mangafox, ',
                             'mangahere and readcomics.tv ',
                             '%s not supported' % (self.url))
        return chapters

    def set_download_chapters(self, potential_keys=None):
        """Set chapters to download."""
        if potential_keys:
            keys = list(set(potential_keys) & set(self.all_chapters.keys()))
        else:
            keys = list(self.all_chapters.keys())

        # Sort keys to make it ascending order and make it a new dict
        unsorted_chapters = {key: self.all_chapters[key]
                             for key in keys}
        self.chapters_to_download = OrderedDict(
            sorted(unsorted_chapters.items(), key=lambda t: t[0]))
        # Print downloading chapters
        print("Downloading the below chapters:")
        print(sorted(keys))

    def download_comic(self):
        """Begin download the chapters in the comic."""
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.chapter_threads) as executor:
            future_to_chapter = {
                executor.submit(chapter.download_chapter): chapter_num
                for chapter_num, chapter in self.chapters_to_download.items()}

            for future in concurrent.futures.as_completed(future_to_chapter):
                chapter_num = future_to_chapter[future]
                try:
                    future.result()
                except Exception as exc:
                    print('Chapter-%g generated an exception: %s'
                          % (chapter_num, exc))
                else:
                    print('Downloaded: Chapter-%g' % (chapter_num))

    def manga_extract_chapters(self):
        """Extract chapters if the comic is a manga."""
        comic_name = self.name
        url = self.url
        urlscheme = urlparse(url)

        # Get chapters
        r = requests.get(url, verify=self.verify_https)
        soup = bsoup.BeautifulSoup(r.text, 'html.parser')

        chapters = defaultdict(Chapter)
        links = [link.get('href')
                 for link in soup.find_all('a')
                 if link.get('href') and
                 (comic_name in link.get('href')) and
                 ('manga' in link.get('href'))]

        for link in links:
            chapter_link = urljoin(urlscheme.scheme + "://" + urlscheme.netloc,
                                   '/'.join(link.split('/')[:-1]))
            matched_groups = re.search('v(\d*)/c([\d \.]*)', chapter_link)
            if matched_groups:
                volume_num = int(matched_groups.group(1))
                chapter_num = float(matched_groups.group(2))
                if chapter_num in chapters:
                    continue
                else:
                    chapters[chapter_num] = Chapter(
                        self, chapter_num, volume_num, chapter_link)

        if (not chapters) and links:
            # Maybe the manga has no volume (try this out)
            for link in links:
                chapter_link = urljoin(urlscheme.scheme
                                       + "://" + urlscheme.netloc,
                                       '/'.join(link.split('/')[:-1]))
                matched_groups = re.search('c([\d \.]+)', chapter_link)
                if matched_groups:
                    volume_num = 1
                    chapter_num = float(matched_groups.group(1))
                    if chapter_num in chapters:
                        continue
                    else:
                        chapters[chapter_num] = Chapter(
                            self, chapter_num, volume_num, chapter_link)

        return chapters

    def comic_extract_chapters(self):
        """Extract chapters if it is a comic."""
        url = self.url
        comic = url.split('/')[-1]
        r = requests.get(url, verify=self.verify_https)
        soup = bsoup.BeautifulSoup(r.text, 'html.parser')
        volume_num = 1

        chapters = defaultdict(Chapter)
        for link in soup.find_all('a'):
            if (comic in link.get('href')) and ('chapter' in link.get('href')):
                chapter = link.get('href')
                chapter_match = re.search('chapter-([\d -]*)', chapter)
                chapter_string = chapter_match.group(1)
                chapter_num = float('.'.join(chapter_string.split('-')))
                if chapter_num in chapters:
                    continue
                else:
                    chapters[chapter_num] = Chapter(
                        self, chapter_num, volume_num, chapter + '/full')

        return chapters


class Chapter:
    """Chapter class. Contains pages."""

    def __init__(self, comic, chapter_num, volume_num, chapter_url):
        """Initialize constants required for download."""
        # Extract necessary information from the comic object
        self.comic_name = comic.name
        self.comic_download_location = comic.download_location
        self.comic_mode = comic.mode
        # Create chapter specific variables
        self.chapter_num = chapter_num
        self.volume_num = volume_num
        self.chapter_url = chapter_url
        # Threads and retry time
        self.page_threads = comic.page_threads
        self.wait_time = comic.wait_time
        self.max_retries = comic.max_retries
        self.comic_file_format = comic.file_format
        # Set verify mode
        self.verify_https = comic.verify_https

    def download_chapter(self):
        """Download and convert it into a cbz file."""
        init_status, pages, download_func = self.initialize_chapter_download()

        if not init_status:
            raise RuntimeError('Unable to obtain pages in the chapter')

        self.chapter_location = os.path.join(
            self.comic_download_location, 'chapter-' + str(self.chapter_num))
        if not os.path.exists(self.chapter_location):
            os.makedirs(self.chapter_location)

        # Download individual pages in parallel
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.page_threads) as executor:
            executor.map(download_func, pages)

        # Convert the folder to a comic book zip filename
        if self.comic_mode[0] == 'manga':
            chapter_name = os.path.join(
                self.comic_download_location, '%s-%g (v%d)'
                % (self.comic_name, self.chapter_num, self.volume_num))
        elif self.comic_mode[0] == 'comic':
            chapter_name = os.path.join(
                self.comic_download_location, '%s-%g'
                % (self.comic_name, self.chapter_num))

        if self.comic_file_format == 'pdf':
            pdfdir(self.chapter_location, chapter_name + ".pdf")
        elif self.comic_file_format == 'cbz':
            zipdir(self.chapter_location, chapter_name + ".cbz")
        shutil.rmtree(self.chapter_location)

    def initialize_chapter_download(self):
        """Obtain pages and function based on the mode."""
        if self.comic_mode[0] == 'manga':
            init_status, pages = self.manga_get_pages()
            func = self.manga_download_page
        elif self.comic_mode[0] == 'comic':
            init_status, pages = self.comic_get_pages()
            func = self.comic_download_page

        return init_status, pages, func

    def manga_get_pages(self):
        """Obtain list of pages in a manga chapter."""
        # Get base url
        if (self.comic_mode[1] == 'mangafox'):
            base_url = self.chapter_url + '/1.html'
        elif (self.comic_mode[1] == 'mangahere'):
            base_url = self.chapter_url

        max_retries = deepcopy(self.max_retries)
        wait_retry_time = deepcopy(self.wait_time)

        while True:
            # Get javascript blocks
            r = requests.get(base_url, verify=self.verify_https)
            soup = bsoup.BeautifulSoup(r.text, 'html.parser')
            scripts = [script for script in soup.find_all(
                'script', attrs={'type': 'text/javascript'})]

            if scripts:
                # Get total pages
                for script in scripts:
                    if script.contents:
                        matched_groups = re.search(
                            'var total_pages\s?=\s?(\d*)\s?;',
                            script.contents[0])
                        if matched_groups:
                            total_pages = int(matched_groups.group(1))
                            break
                # Get page urls
                page_urls = ["%s/%d.html" % (self.chapter_url, i + 1)
                             for i in range(total_pages)]
                page_num = [i + 1 for i in range(total_pages)]
                pages = list(zip(page_urls, page_num))
                shuffle(pages)

                return True, pages

            elif (max_retries > 0):
                # Idea from manga_downloader (which in turn was from wget)
                sleep(uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                max_retries -= 1
            else:
                return False, None

    def comic_get_pages(self):
        """Obtain list of pages in a comic chapter."""
        url = self.chapter_url
        r = requests.get(url, verify=self.verify_https)
        soup = bsoup.BeautifulSoup(r.text, 'html.parser')
        images = [image.get('src') for image in soup.find_all(
            'img', attrs={'class': "chapter_img"})]
        page_num = [i + 1 for i in range(len(images))]
        pages = list(zip(images, page_num))
        shuffle(pages)

        return True, pages

    def manga_download_page(self, page):
        """Download individual pages in a manga."""
        page_url, page_num = page
        filename = os.path.join(self.chapter_location,
                                '%0.3d.jpg' % (page_num))

        max_retries = deepcopy(self.max_retries)
        wait_retry_time = deepcopy(self.wait_time)

        while True:
            r = requests.get(page_url, verify=self.verify_https)
            soup = bsoup.BeautifulSoup(r.text, 'html.parser')
            img = soup.find_all('img', attrs={'id': 'image'})
            if img:
                image = img[0].get('src')
                download_image(image, filename, self.verify_https)
                return True
            elif (max_retries > 0):
                # Idea from manga_downloader (which in turn was from wget)
                sleep(uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                max_retries -= 1
            else:
                print("Failed download: Chapter-%g, page-%d"
                      % (self.chapter_num, page_num))
                shutil.copyfile(
                    os.path.join(os.path.dirname(
                        os.path.realpath(__file__)), 'no_image_available.png'),
                    filename)
                return False

    def comic_download_page(self, page):
        """Download individual pages in a comic."""
        image, page_num = page
        filename = os.path.join(self.chapter_location,
                                '%0.3d.jpg' % (page_num))

        download_image(image, filename)
        return True


def download_image(url, filename, verify_https):
    """Download image (url) and save (filename)."""
    response = requests.get(url, stream=True, verify=verify_https)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def zipdir(folder, filename):
    """Zip folder."""
    assert os.path.isdir(folder)
    zipf = ZipFile(filename, 'w', ZIP_DEFLATED)
    for root, dirs, files in os.walk(folder):
        # note: ignore empty directories
        for fn in sorted(files):
            zipf.write(
                os.path.join(root, fn),
                os.path.relpath(os.path.join(root, fn), folder))
    zipf.close()


def pdfdir(folder, filename):
    """Create PDF of images in the folder."""
    assert os.path.isdir(folder)
    with open(filename, "wb") as f:
        for root, dirs, files in os.walk(folder):
            # Convert images to pdf
            f.write(img2pdf.convert(
                [os.path.join(root, fn) for fn in sorted(files)]))


def main():
    """Parse input and download comic(s)."""
    parser = argparse.ArgumentParser(
        description=(
            'Downloads all manga chapters from'
            'the given url (currently works with mangafox.me and mangahere.co'
            '). Example - A url input '
            ' http://mangafox.me/manga/kingdom looks '
            'for the kingdom manga chapters in the url, downloads them all, '
            'and makes cbz files of all chapters.'))

    parser.add_argument('urls', metavar='url', nargs='+',
                        help='Comic urls to download')
    parser.add_argument(
        "-l", "--location", default=os.getcwd(), help="set download location")
    parser.add_argument(
        "-c", "--chapters", default=False,
        help="Specify chapters to download separated by : (10:20).")
    parser.add_argument(
        "-ct", "--chapterthreads", default=5,
        help="Number of parallel chapters downloads.")
    parser.add_argument(
        "-pt", "--pagethreads", default=10,
        help="Number of parallel chapter pages downloads (per chapter).")
    parser.add_argument(
        "-wt", "--waittime", default=15,
        help="Wait time before retry if encountered with an error")
    parser.add_argument(
        "-rt", "--retries", default=10,
        help="Number of retries before giving up")
    parser.add_argument(
        "-f", "--format", default='pdf',
        help="File format of the downloaded file, supported 'pdf' and 'cbz'")

    args = parser.parse_args()

    for url in args.urls:
        # If https, check before using verify False
        urlscheme = urlparse(url)
        verify_https = False
        if urlscheme.scheme == 'https':
            try:
                requests.get(url)
                verify_https = True
            except requests.exceptions.SSLError:
                verify_https = False
                print('Could not validate https certificate for url:' +
                      '%s. Proceeding with Insecure certificate.' % (url))
                requests.packages.urllib3.disable_warnings(
                    category=InsecureRequestWarning)

        comic = Comic(url, args, verify_https)
        print('Downloading comic: ' + comic.name)

        # Get chapters to download
        if args.chapters:
            try:
                start_stop = args.chapters.split(':')
                if len(start_stop) == 1:
                    potential_keys = [float(start_stop[0])]
                elif len(start_stop) == 2:
                    potential_keys = [
                        i * 0.5 for i in range(2 * int(start_stop[0]),
                                               2 * int(start_stop[1]) + 1)]
                else:
                    raise SyntaxError(
                        "Chapter inputs should be separated by ':'")
            except TypeError:
                raise SyntaxError("Chapter inputs should be separated by ':'")
                exit()

            comic.set_download_chapters(potential_keys)
        else:
            comic.set_download_chapters()

        comic.download_comic()
        print('Downloaded comic:' + url.split('/')[-1])


if __name__ == '__main__':
    main()
