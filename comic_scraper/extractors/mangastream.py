"""Extractor for mangastream.com."""

from base_comic import BaseComic, BaseChapter
from urllib.parse import urlparse, urljoin
import requests
import bs4 as bsoup
from collections import defaultdict
import re
import os
import shutil
from random import shuffle, uniform
from copy import deepcopy
from time import sleep


class MangaStreamComic(BaseComic):
    """Base comic class."""

    def extract_chapters(self):
        """Extract chapters function (backbone)."""
        url = self.url
        urlscheme = urlparse(url)

        # Get chapters
        r = requests.get(url, verify=self.verify_https)
        soup = bsoup.BeautifulSoup(r.text, 'html.parser')

        chapters = defaultdict(MangaStreamChapter)

        # Find all entries in the table (mangastream)
        entries = soup.table.find_all('a')
        for entry in entries:
            chapter_link = urljoin(urlscheme.scheme
                                   + "://" + urlscheme.netloc,
                                   entry.get('href'))
            matched_groups = re.search('([\d\.]+)', entry.string)
            if matched_groups:
                chapter_num = float(matched_groups.group(1))
                if chapter_num in chapters:
                    continue
                else:
                    chapters[chapter_num] = MangaStreamChapter(
                        self, chapter_num, chapter_link)

        return chapters


class MangaStreamChapter(BaseChapter):
    """Base chapter class."""

    def get_pages(self):
        """Obtain list of pages in a manga chapter."""
        # Get base url
        base_url = self.chapter_url
        max_retries = deepcopy(self.max_retries)
        wait_retry_time = deepcopy(self.wait_time)
        # Obtain match url
        urlscheme = urlparse(base_url)

        while True:
            # Get javascript blocks
            r = requests.get(base_url, verify=self.verify_https)
            soup = bsoup.BeautifulSoup(r.text, 'html.parser')

            drop_down_menus = soup.find_all('ul')

            for ddm in drop_down_menus:
                if ddm.li.a:
                    if urlscheme.path in ddm.li.a.get('href'):
                        page_list = ddm.find_all('a')
                        break

            pages = []
            for page in page_list:
                curr_url = page.get('href')
                page_num = float(curr_url.split('/')[-1])
                page_url = urljoin(urlscheme.scheme
                                   + "://" + urlscheme.netloc, curr_url)
                pages.append((page_url, page_num))

            if pages:
                shuffle(pages)
                return True, pages

            elif (max_retries > 0):
                # Idea from manga_downloader (which in turn was from wget)
                sleep(uniform(0.5 * wait_retry_time, 1.5 * wait_retry_time))
                max_retries -= 1
            else:
                return False, None

    def download_page(self, page):
        """Download individual pages in a manga."""
        page_url, page_num = page
        urlscheme = urlparse(page_url)
        filename = os.path.join(self.chapter_location,
                                '%0.3d.jpg' % (page_num))

        max_retries = deepcopy(self.max_retries)
        wait_retry_time = deepcopy(self.wait_time)

        while True:
            r = requests.get(page_url, verify=self.verify_https)
            soup = bsoup.BeautifulSoup(r.text, 'html.parser')
            for div in soup.find_all('div'):
                if div.get('class'):
                    if div.get('class')[0] == 'page':
                        img = div.find_all('img')
                        break

            if img:
                image = urljoin(urlscheme.scheme
                                + "://" + urlscheme.netloc,
                                img[0].get('src'))
                self.download_image(image, filename)
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
