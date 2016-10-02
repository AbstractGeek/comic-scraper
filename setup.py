from setuptools import setup

setup(name='comic_scrapper',
      version='0.1',
      description='Scraps comics and creates cbz files',
      url='https://github.com/AbstractGeek/comic-scrapper',
      download_url='https://github.com/AbstractGeek/comic-scrapper',
      author='Dinesh Natesan',
      author_email='abstractgeek@outlook.com',
      license='MIT',
      packages=['comic_scrapper'],
      install_requires=[
          'beautifulsoup4',
          'futures',
          'requests==2.9.1'
      ],
      entry_points={
        'console_scripts':
        ['comic-scrapper=comic_scrapper.comic_scrapper:main'],
        },
      include_package_data=True,
      zip_safe=False)
