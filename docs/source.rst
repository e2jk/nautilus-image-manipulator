.. _source:

Working with the source code
============================
Nautilus Image Manipulator is written in `Python`_ and uses `GTK+ version 3`_.

Retrieving the source code
--------------------------
The code is hosted on `Launchpad`_ and is versioned using `Bazaar`_. Execute the
following command to get your copy of the main branch::

   bzr branch lp:nautilus-image-manipulator

You can also `browse the code`_ if you'd just like to look at it online.

Running the software from source
--------------------------------
The steps to install from source are `explained here`_.

Modifying the GUI
-----------------
The GUI is created using `Glade`_. Open it up by running this command::

   ./extra/design.py

Updating the translation template
---------------------------------
Whenever you have made changes in the GUI or the Python source code to
user-facing strings, you should run the following command to update the
translation template ``po/nautilus-image-manipulator.pot``::

   ./extra/update_i18n.py

Updating the translations from Launchpad
----------------------------------------
The translation template ``po/nautilus-image-manipulator.pot`` is automatically
read after each commit that is pushed to the main branch, and the strings are
made available for `translation on Launchpad`_. After strings have been
translated, follow this process to update the translations in your branch:

   * `Request a download`_ of all translated ``.mo`` files on Launchpad.

   * You will receive an email from Launchpad containing a link to a
     tarball containing all the translated files, download it.

   * Put the downloaded ``launchpad-export.tar.gz`` file in the ``./po``
     folder

   * Run the command ``./extra/update_i18n.py`` to unpack the files and
     compile them locally.

Note that aside from updating the ``.mo`` files that are already present in the
branch, this process will also add new files for languages that are not yet
versionned. These files are for languages where the number of translated
strings are not yet sufficient to justify adding them to a new release. It's
unlikely that a new language will be added before it has reached a translation
rate of 80%-90%...

.. _Python: http://python.org/
.. _GTK+ version 3: http://www.gtk.org/
.. _Launchpad: https://code.launchpad.net/nautilus-image-manipulator
.. _Bazaar: http://bazaar.canonical.com/en/
.. _browse the code: http://bazaar.launchpad.net/~emilien-klein/nautilus-image-manipulator/trunk/files
.. _explained here: install.html#installing-from-source
.. _Glade: http://glade.gnome.org/
.. _translation on Launchpad: https://translations.launchpad.net/nautilus-image-manipulator/trunk/+pots/nautilus-image-manipulator
.. _Request a download: https://translations.launchpad.net/nautilus-image-manipulator/trunk/+pots/nautilus-image-manipulator/+export

