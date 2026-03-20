.. Dykes documentation master file, created by
   sphinx-quickstart on Thu Mar 19 14:30:57 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Dykes
===================

Do You Know Every Selection?
---------------------------------------------

:py:mod:`dykes` helps you get a handle on your tools.

Use a typed class to generate an ArgumentParser and get a nicely types instance
back.

The absolute simplest program using dykes looks like:

.. code:: python

   from dataclasses import dataclass

   import dykes

   @dataclass
   class Arguments:
       path: str

   if __name__ == "__main__":
       arguments = dykes.parse_args(Arguments)
       print(arguments)

If you'd like more details, check out the :doc:`users-guide/index`.

If you want to know how things work internally, check out :doc:`api/index`.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   users-guide/index
   api/index
