from setuptools import setup

setup(name='ledger',
      version='1.01',
      description='Ledger Payments App',
      url='https://github.com/dbca-wa/ledger',
      author='Department of Parks and Wildlife',
      author_email='asi@dbca.wa.gov.au',
      license='BSD',
      packages=['ledger','ledger.accounts','ledger.address','ledger.basket','ledget.catalogue','ledger.checkout','ledger.dashboard'],
      install_requires=[],
      zip_safe=False)
