# Comic-Scrapper (Comic Downloader)
Downloads comics from various websites and creates cbz files from them.
Currently supports just readcomics.tv

## Installation

### Via pip
To install the comic scrapper, simply type this into your terminal (sudo might be necessary):
```
pip install comic-scrapper
```

### Via pip (local)
Clone a copy of the repository using the following command:
```
git clone git@github.com:AbstractGeek/comic-scrapper.git
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

These can simply be installed by:
```
pip install -r requirements.txt
```
That's it. Use comic_scrapper.py to download comics

## Usage
Find your comic of interest in readcomics.tv. Copy the url of the comic page.
For example, If I wanted to download spider-man-2016, I need to copy this url:
http://www.readcomics.tv/comic/spider-man-2016

To download all the chapters of the comic, simply call the script and input the url.
```
comic-scrapper http://www.readcomics.tv/comic/spider-man-2016
```

If you want to set a custom location, add -l and input the location
```
comic-scrapper -l ~/Comics/ http://www.readcomics.tv/comic/spider-man-2016
```

If you want to download a select few chapters, add -c and input the chapter numbers.
For example, if I want to download chapters 10-20, I use the following command
```
comic-scrapper -l ~/Comics/ -c 10:20 http://www.readcomics.tv/comic/spider-man-2016
```
Note: Only individual chapters or sequential chunks (start:stop) can currently be downloaded.
