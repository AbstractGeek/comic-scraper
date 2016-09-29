# Comic-Scrapper (Comic Downloader)
Downloads comics from various websites and creates cbz files from them.
Currently supports just readcomics.tv

## Requirements
The script is written in python3. It requires the following packages:
1. BeautifulSoup4
2. requests
3. futures (concurrent.futures)

These can simply be installed by:
```
pip install -r requirements.txt
```

## Usage
Find your comic of interest in readcomics.tv. Copy the url of the comic page.
For example, If I wanted to download spider-man-2016, I need to copy this url:
http://www.readcomics.tv/comic/spider-man-2016

To download all the chapters of the comic, simply call the script and input the url.
```
python comic-scrapper http://www.readcomics.tv/comic/spider-man-2016
```

If you want to set a custom location, add -l and input the location
```
python comic-scrapper -l ~/Comics/ http://www.readcomics.tv/comic/spider-man-2016
```

If you want to download a select few chapters, add -c and input the chapter numbers.
For example, if I want to download chapters 10-20, I use the following command
```
python comic-scrapper -l ~/Comics/ -c 10:20 http://www.readcomics.tv/comic/spider-man-2016
```
Note: Only individual chapters or sequential chunks (start:stop) can currently be downloaded.

You can also make the comic-scrapper script an executable and call it directly
```
chmod +x comic-scrapper
./comic-scrapper -l ~/Comics/ http://www.readcomics.tv/comic/spider-man-2016
```
