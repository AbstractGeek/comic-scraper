# Comic-scraper (Comic/Manga Downloader)
Downloads comics and manga from various websites and creates pdf or cbz files from them.
Currently supports mangafox.me and mangahere.co (more coming up soon).

## Installation

### Via pip
To install the comic scraper, simply type this into your terminal (```sudo -EH``` might be necessary):
```
pip install comic-scraper
```

### Via pip (local)
Clone a copy of the repository using the following command:
```
git clone https://github.com/AbstractGeek/comic-scraper.git
```

Open your terminal into the folder and type this into it (sudo might be necessary):
```
pip install .
```

### Manual Installation

#### Requirements
The script is written in python. It requires the following packages:
1. BeautifulSoup4
2. requests
3. futures (concurrent.futures)
4. img2pdf

These can simply be installed by:
```
pip install -r requirements.txt
```
That's it. Use comic_scraper.py to download comics and manga.

## Usage
### Manga
Find your comic of interest in mangafox/mangahere. Copy the url of the comic page (https supported).
For example, If I wanted to download kingdom manga, I need to copy this url:
https://mangafox.me/manga/kingdom/

To download all the chapters of the comic, simply call the script and input the url.
```
comic-scraper https://mangafox.me/manga/kingdom/
```

If you want to set a custom location, add -l and input the location
```
comic-scraper -l ~/Comics/ https://mangafox.me/manga/kingdom/
```

If you want to download a select few chapters, add -c and input the chapter numbers.
For example, if I want to download chapters 10-20, I use the following command
```
comic-scraper -l ~/Comics/ -c 10:20 https://mangafox.me/manga/kingdom/
```
Note: Only individual chapters or sequential chunks (start:stop) can currently be downloaded.

Download format can be specified too. The current default is pdf, but comics can be downloaded as cbz files using the following command.
```
comic-scraper -l ~/Comics/ -c 10:20 -f cbz https://mangafox.me/manga/kingdom/
```


### Comics
Coming soon...
