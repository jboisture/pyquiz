import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'repoze.zodbconn',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'repoze.retry',
    'ZODB3',
    'WebError',
    'Babel',
    'nose',
    'nose-cov',
    'Sphinx',
    'repoze.folder',
    'WebTest',
    'lxml',
    'deform',
    'colander',
    'peppercorn',
    'iso8601',
    ]

setup(name='pyquiz',
      version='0.0',
      description='pyquiz',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="pyquiz",
      entry_points = """\
      [paste.app_factory]
      main = pyquiz:main
      """,
      paster_plugins=['pyramid'],
      message_extractors = { 'pyquiz': [
          ('**.py',   'chameleon_python', None ),
          ('**.pt',   'chameleon_xml', None ),
          ]},
      )
