#!/usr/bin/env python3
import argparse
import requests
import os
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning
import current_comic


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

        comic = current_comic.comic(url, args, verify_https)
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

            comic.set_download_chapters(potential_keys)
        else:
            comic.set_download_chapters()

        comic.download_comic()
        print('Downloaded comic:' + url.split('/')[-1])


if __name__ == '__main__':
    main()
