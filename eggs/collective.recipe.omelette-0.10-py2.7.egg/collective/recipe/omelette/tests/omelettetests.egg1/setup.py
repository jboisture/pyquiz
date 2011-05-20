from setuptools import setup, find_packages

setup(name='egg.with.name.different.from.contents',
      packages=find_packages(),
      namespace_packages=['omelettetests', 'omelettetests.chicken'],
      install_requires=['setuptools'],
      )
