from setuptools import setup

setup(name='comic-scraper',
      version='0.6.0',
      description='Scraps comics,mangas and creates cbz (/pdf) files for offline reading',
      url='https://github.com/AbstractGeek/comic-scraper',
      download_url='https://github.com/AbstractGeek/comic-scraper/tarball/0.6.0',
      author='Dinesh Natesan',
      author_email='abstractgeek@outlook.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Topic :: Games/Entertainment',
      ],
      keywords='comics manga scraper',
      packages=['comic_scraper'],
      install_requires=[
          'beautifulsoup4==4.6.0',
          'certifi==2017.7.27.1',
          'chardet==3.0.4',
          'futures==3.1.1',
          'idna==2.6',
          'img2pdf==0.2.4',
          'olefile==0.44',
          'Pillow==4.3.0',
          'requests==2.18.4',
          'urllib3==1.22'
      ],
      entry_points={
          'console_scripts':
          ['comic-scraper=comic_scraper.comic_scraper:main'],
      },
      include_package_data=True,
      zip_safe=False)
