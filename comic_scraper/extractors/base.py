"""Base class for all the extractors."""


class BaseComic:
    """Base comic class."""

    def __init__(self, comic_url, verify_https):
        """Initialize rquired parameters for chapter search."""
        self.url = comic_url
        self.name = comic_url.split('/')[-1] \
            if comic_url.split('/')[-1] else comic_url.split('/')[-2]
        # Set verify mode
        self.verify_https = verify_https

    def extract_chapters(self):
        """Extract chapters function (backbone)."""
        pass


class BaseChapter:
    """Base chapter class."""

    def __init__(self, comic_name, chapter_url, verify_https):
        """Initialize rquired parameters for page search."""
        self.comic_name = comic_name
        self.chapter_url = chapter_url
        self.verify_https = verify_https

    def get_pages(self):
        """Get pages function (backbone)."""
        pass
