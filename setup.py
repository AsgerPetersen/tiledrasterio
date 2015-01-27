from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    readme = f.read()


setup(name='myproject',
      version='0.0.1',
      description=u"Tiled raster io",
      long_description=readme,
      classifiers=[],
      keywords='',
      author=u"Asger Skovbo Petersen",
      author_email='asger@septima.dk',
      url='https://github.com/AsgerPetersen/tiledrasterio',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click',
          'rasterio'
      ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points="""
      [console_scripts]
      tiledrasterio=tiledrasterio.scripts.cli:cli
      """
      )
