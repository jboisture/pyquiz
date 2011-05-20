Introduction
============

Namespace packages offer the huge benefit of being able to distribute parts of a large
system in small, self-contained pieces.  However, they can be somewhat clunky to navigate,
since you end up with a large list of eggs in your egg cache, and then a seemingly endless
series of directories you need to open to actually find the contents of your egg.

This recipe sets up a directory structure that mirrors the actual python namespaces, with
symlinks to the egg contents.  So, instead of this...::

    egg-cache/
        my.egg.one-1.0-py2.4.egg/
            my/
                egg/
                    one/
                        (contents of first egg)
        my.egg.two-1.0-py2.4.egg/
            my/
                egg/
                    two/
                        (contents of second egg)

...you get this::

    omelette/
        my/
            egg/
                one/
                    (contents of first egg)
                two/
                    (contents of second egg)


You can also include non-eggified python packages in the omelette.  This makes it simple to
get a single path that you can add to your PYTHONPATH for use with specialized python environments
like when running under mod_wsgi or PyDev.


Typical usage with Zope and Plone
=================================

For a typical Plone buildout, with a part named "instance" that uses the plone.recipe.zope2instance recipe and a
part named "zope2" that uses the plone.recipe.zope2install recipe, the following additions to buildout.cfg will
result in an omelette including all eggs and old-style Products used by the Zope instance as well as all of the
packages from Zope's lib/python. It is important that omelette come last if you want it to find everything::

    [buildout]
    parts =
        ...(other parts)...
        omelette
        
    ...
        
    [omelette]
    recipe = collective.recipe.omelette
    eggs = ${instance:eggs}
    products = ${instance:products}
    packages = ${zope2:location}/lib/python ./
    
(Note: If your instance part lacks a 'products' variable, omit it from the omelette section as well, or
the omelette will silently fail to build.)

    
Supported options
=================

The recipe supports the following options:

eggs
    List of eggs which should be included in the omelette.

location
    (optional) Override the directory in which the omelette is created (default is parts/[name of buildout part])

ignore-develop
    (optional) Ignore eggs that you are currently developing (listed in ${buildout:develop}). Default is False

ignores
    (optional) List of eggs to ignore when preparing your omelette.

packages
    List of Python packages whose contents should be included in the omelette.  Each line should be in the format
    [package_location] [target_directory], where package_location is the real location of the package, and
    target_directory is the (relative) location where the package should be inserted into the omelette (defaults
    to top level).

products
    (optional) List of old Zope 2-style products directories whose contents should be included in the omelette,
    one per line.  (For backwards-compatibility -- equivalent to using packages with Products as the target
    directory.)


Windows support
===============

Using omelette on Windows requires the junction_ utility to make links.  Junction.exe must be present in
your PATH when you run omelette.

.. _junction: http://www.microsoft.com/technet/sysinternals/fileanddisk/junction.mspx


Using omelette with eggtractor
==============================

Mustapha Benali's buildout.eggtractor_ provides a handy way for buildout to automatically find
development eggs without having to edit buildout.cfg.  However, if you use it, the omelette recipe
won't be aware of your eggs unless you a) manually add them to the omelette part's eggs option, or
b) add the name of the omelette part to the buildout part's tractor-target-parts option.

.. _buildout.eggtractor: http://pypi.python.org/pypi/buildout.eggtractor/


Using omelette with zipped eggs
===============================

Omelette doesn't currently know how to deal with eggs that are zipped.  If it encounters one, you'll
see a warning something like the following::

    omelette: Warning: (While processing egg elementtree) Egg contents not found at
    /Users/davidg/.buildout/eggs/elementtree-1.2.7_20070827_preview-py2.4.egg/elementtree.  Skipping.

You can tell buildout to unzip all eggs by setting the unzip = true flag in the [buildout] section.
(Note that this will only take effect for eggs downloaded after the flag is set.)


Running the tests
=================

Just grab the recipe from svn and run::

    python2.4 setup.py test

Known issue: The tests run buildout in a separate process, so it's currently
impossible to put a pdb breakpoint in the recipe and debug during the test.
If you need to do this, set up another buildout which installs an omelette
part and includes collective.recipe.omelette as a development egg.


Reporting bugs or asking questions
==================================

There is a shared bugtracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
