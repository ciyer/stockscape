from setuptools import setup

setup(name='stockscape',
      version='0.9.0',
      description='Perform CAPE analysis of stock prices.',
      url='https://github.com/ciyer/stockscape',
      author='Chandrasekhar Ramakrishnan',
      author_email='ciyer@illposed.com',
      license='BSD',
      packages=['stockscape'],
      install_requires=[
          'numpy',
          'scipy',
          'pandas',
          'matplotlib',
          'pytest',
          'xlrd',
          'pyyaml',
          'pytz',
          'future',
          'six'
      ],
      zip_safe=True)
