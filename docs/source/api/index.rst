API Reference
============================

.. automodule:: dykes

.. warning::

   The API documentation is a complete description of all modules and members.
   If you're using dykes to build a piece of software, this page describes the
   public API. Other pages under this heading contain information aimed at those
   developing dykes itself.

.. autofunction:: dykes.processing.parse_args

.. autofunction:: dykes.processing.build_parser

.. automodule:: dykes.options
   :members:

.. py:type:: Count
   :canonical: typing.Annotated[int, Action.COUNT]

   A type alias for the :class:`~dykes.Action.COUNT` action.

   Use like:

   .. code:: python

      @dataclass
      class Counter:
          count: dykes.Count


.. py:type:: StoreFalse
   :canonical: typing.Annotated[bool, Action.STORE_FALSE]

   A type alias for using the :class:`~dykes.Action.STORE_FALSE` action.

   Use like:

   .. code:: python

      @dataclass
      class CommitOptional:
          commit: StoreFalse


.. py:type:: StoreTrue
   :canonical: typing.Annotated[bool, Action.STORE_TRUE]

   A type alias for using the :class:`~dykes.Action.STORE_TRUE` action.

   Use like:

   .. code:: python

      @dataclass
      class DryRun:
          dry_run: StoreTrue

.. toctree::
   processing
   internal
   utils
