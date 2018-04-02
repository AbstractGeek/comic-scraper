"""Define current comic class based on url."""

from extractors.mangafox import MangaFoxComic
from extractors.mangahere import MangaHereComic
from extractors.mangastream import MangaStreamComic
from extractors.mangareader import MangaReaderComic


def comic(comic_url, args, verify_https):
    """Send the approriate class."""
    if 'mangafox' in comic_url:
        return MangaFoxComic(comic_url, args, verify_https)
    elif 'mangahere' in comic_url:
        return MangaHereComic(comic_url, args, verify_https)
    elif ('mangstream' in comic_url) or ('readms' in comic_url):
        return MangaStreamComic(comic_url, args, verify_https)
    elif ('mangareader' in comic_url):
        return MangaReaderComic(comic_url, args, verify_https)
