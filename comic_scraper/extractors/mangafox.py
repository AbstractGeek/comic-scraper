"""Extractor for mangafox.me."""

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


class MangaFoxComic(BaseComic):
    """Base comic class."""

    def extract_chapters(self):
        """Extract chapters function (backbone)."""
        comic_name = self.name
        url = self.url
        urlscheme = urlparse(url)

        # Get chapters
        r = requests.get(url, verify=self.verify_https)
        soup = bsoup.BeautifulSoup(r.text, 'html.parser')

        chapters = defaultdict(MangaFoxChapter)
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
                    chapters[chapter_num] = MangaFoxChapter(
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
                        chapters[chapter_num] = MangaFoxChapter(
                            self, chapter_num, volume_num, chapter_link)

        return chapters


class MangaFoxChapter(BaseChapter):
    """Base chapter class."""

    def get_pages(self):
        """Obtain list of pages in a manga chapter."""
        # Get base url
        base_url = self.chapter_url + '/1.html'
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

    def download_page(self, page):
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
