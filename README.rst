myproject
======

.. image:: https://travis-ci.org/mapbox/myproject.svg
   :target: https://travis-ci.org/mapbox/myproject

.. image:: https://coveralls.io/repos/mapbox/myproject/badge.png
   :target: https://coveralls.io/r/mapbox/myproject

A skeleton of a Python package with CLI and test suite included.
   
.. image:: https://farm4.staticflickr.com/3951/15672691531_3037819613_o_d.png

Customization quick start
-------------------------

To use myproject as the start of a new project, do the following, preferably in
a virtual environment. Clone the repo.

.. code-block:: console

    git clone https://github.com/mapbox/myproject myproject
    cd myproject

Replace all occurrences of 'myproject' with the name of your own project.
(Note: the commands below require bash, find, and sed and are yet tested only on OS X.)

.. code-block:: console

    if [ -d myproject ]; then find . -not -path './.git*' -type f -exec sed -i '' -e 's/myproject/myproject/g' {} + ; fi
    mv myproject myproject

Then install in locally editable (``-e``) mode and run the tests.

.. code-block:: console

    pip install -e .[test]
    py.test

Finally, give the command line program a try.

.. code-block:: console

    myproject --help
    myproject 4

To help prevent uncustomized forks of myproject from being uploaded to PyPI,
I've configured the setup's upload command to dry run. Make sure to remove
this configuration from
`setup.cfg <https://docs.python.org/2/install/index.html#inst-config-syntax>`__
when you customize myproject.

Please also note that the Travis-CI and Coveralls badge URLs and links in the README
contain the string 'mapbox.' You'll need to change this to your own user or organization
name and turn on the webhooks for your new project.

A post on the Mapbox blog has more information about this project:
https://www.mapbox.com/blog/myproject/.

See also
--------

Here are a few other tools for initializing Python projects.

- Paste Script's `paster create <http://pythonpaste.org/script/#paster-create>`__ is
  one that I've used for a long time.
- `cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__ is
  a Cookiecutter template for a Python package. Cookiecutter supports many languages,
  includes Travis configuration and much more.

