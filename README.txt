pyquiz README
============

About
-----

pyquiz is a pyramid based Web Application that will allow teachers to create tests and assign them to students.

Setup
-----

to install pyquiz clone the branch from the repositories in git hub

	$ git clone git@github.com:jboisture/pyquiz.git buildout

make sure setuptools is installed

	$ sudo apt-get install python-setuptools

run bootstrap.py

	$cd buildout
	$python bootstrap.py

run bin/buildout

	$bin/buildout

install the app in development mode

	$cd pyquiz
	$python ../setup.py -develop
	$cd ..

start the app

	$make run

pyquiz should now be serving at http://localhost:6543/


