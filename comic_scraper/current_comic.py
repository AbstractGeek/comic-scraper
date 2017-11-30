"""Define current comic class based on url."""

from extractors.mangafox import MangaFoxComic


def comic(comic_url, args, verify_https):
    """Send the approriate class."""
    if 'mangafox' in comic_url:
        return MangaFoxComic(comic_url, args, verify_https)
