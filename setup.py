from setuptools import setup

setup(name='ledger',
      version='1.00',
      description='Ledger Payments App',
      url='https://github.com/dbca-wa/ledger',
      author='Department of Parks and Wildlife',
      author_email='asi@dbca.wa.gov.au',
      license='BSD',
      packages=['ledger','ledger.*',],
      install_requires=[],
      zip_safe=False)
