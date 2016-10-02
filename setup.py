from setuptools import setup

setup(name='comic-scraper',
      version='0.1',
      description='Scraps comics and creates cbz files',
      url='https://github.com/AbstractGeek/comic-scraper',
      download_url='https://github.com/AbstractGeek/comic-scraper/tarball/0.1',
      author='Dinesh Natesan',
      author_email='abstractgeek@outlook.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Games/Entertainment',
      ],
      keywords='comics scraper',
      packages=['comic_scraper'],
      install_requires=[
          'beautifulsoup4',
          'futures',
          'requests==2.9.1'
      ],
      entry_points={
        'console_scripts':
        ['comic-scraper=comic_scraper.comic_scraper:main'],
        },
      include_package_data=True,
      zip_safe=False)
