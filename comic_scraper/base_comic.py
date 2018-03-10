"""Base Comic class."""
import os
from collections import OrderedDict
import concurrent.futures
import shutil
import requests
from zipfile import ZipFile, ZIP_DEFLATED
import img2pdf


class BaseComic:
    """Base Comic class. Contains chapters."""

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
        self.all_chapters = self.extract_chapters()

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
        """Begin download of chapters in the comic."""
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

    def extract_chapters(self):
        """Extract chapters function (backbone)."""
        pass


class BaseChapter:
    """Base Chapter class. Contains pages."""

    def __init__(self, comic, chapter_num, chapter_url):
        """Initialize constants required for download."""
        # Extract necessary information from the comic object
        self.comic_name = comic.name
        self.comic_download_location = comic.download_location
        # Create chapter specific variables
        self.chapter_num = chapter_num
        self.chapter_url = chapter_url
        # Threads and retry time
        self.page_threads = comic.page_threads
        self.wait_time = comic.wait_time
        self.max_retries = comic.max_retries
        self.comic_file_format = comic.file_format
        # Set verify mode
        self.verify_https = comic.verify_https
        # Get download chapter location
        self.chapter_location = os.path.join(
            self.comic_download_location, 'chapter-' + str(self.chapter_num))

    def download_chapter(self):
        """Download and convert it into a cbz file."""
        init_status, pages = self.get_pages()
        download_func = self.download_page

        if not init_status:
            raise RuntimeError('Unable to obtain pages in the chapter')

        # Create chapter location (if it doesn't exist)
        if not os.path.exists(self.chapter_location):
            os.makedirs(self.chapter_location)

        # Download individual pages in parallel
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.page_threads) as executor:
            executor.map(download_func, pages)

        # Convert the folder to a comic book zip filename
        chapter_name = os.path.join(
            self.comic_download_location, '%s-%g'
            % (self.comic_name, self.chapter_num))

        if self.comic_file_format == 'pdf':
            pdfdir(self.chapter_location, chapter_name + ".pdf")
        elif self.comic_file_format == 'cbz':
            zipdir(self.chapter_location, chapter_name + ".cbz")
        shutil.rmtree(self.chapter_location)

    def get_pages(self):
        """Get pages function (backbone)."""
        return False, 0

    def download_page(self):
        """Download page (backbone)."""
        pass

    def download_image(self, url, filename):
        """Download image (url) and save (filename)."""
        response = requests.get(url, stream=True, verify=self.verify_https)
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
