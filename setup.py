from setuptools import setup

setup(name='comic-scraper',
      version='0.5.2',
      description='Scraps comics,mangas and creates cbz files for offline reading',
      url='https://github.com/AbstractGeek/comic-scraper',
      download_url='https://github.com/AbstractGeek/comic-scraper/tarball/0.5.2',
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
          'beautifulsoup4',
          'futures',
          'requests',
          'numpy'
      ],
      entry_points={
        'console_scripts':
        ['comic-scraper=comic_scraper.comic_scraper:main'],
        },
      include_package_data=True,
      zip_safe=False)
