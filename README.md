# GCD Survey Chart Utils

## What is this?

This project is basically just me learning Google Charts and kinda-sorta
attempting to write JavaScript for the first time in years.  Which is why
most of the processing code is in Python.

While parts are general, much of it is specific to survey data for a recent
Grand Comics Database.  It is likely not of general use- in particular, I am
no doubt still missing things about Google Charts, some of which may make some
of the code unnecessary.

If you somehow landed here looking for generic tools, or for sophisticated
Google Charts-related code, you probably want to look somewhere else.

## How does it work?

``process.py`` takes a tab-separated value file on stdin, discards the first
line (assuming it is a header line) and using the ``Line`` class in
``support.py`` to parse each of the remaining lines.

It then uses the classes and functions in ``charts.py`` to create a number
of ``gviz_api.DataTable`` instances.  These are grouped together in a data
structure with enough information for the code in ``survey.js`` to figure out
how to render them all automatically.  Additionally, it makes a big
``DataTable`` with the complete processed data.

All of these ``DataTables`` (the ones grouped in the larger dictionary and the
single complete data one) are written to stdout.  ``index.html`` expects the
resulting file to be called ``data.js``.  The code in ``survey.js`` knows the
variable names used and will reference each one exactly once to minimize the
global variable ickiness.
