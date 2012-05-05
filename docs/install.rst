.. _install:

Installation
============
Nautilus Image Manipulator is written in `Python`_ and uses `GTK+ version 3`_.

Prebuilt Packages
-----------------
The preferred way to install Nautilus Image Manipulator is to get it from your
distribution's software repository. Nautilus Image Manipulator is currently
packaged in the following Linux distributions:

* `Debian`_: Testing and Unstable

* `Ubuntu`_: starting from 11.10 Oneiric Ocelot 

* `Arch`_

On Debian-based distributions, execute the following command to install Nautilus
Image Manipulator::

    sudo apt-get install nautilus-image-manipulator

Installing From Source
----------------------

Dependencies
^^^^^^^^^^^^
You will need the following software in order to run Nautilus Image Manipulator:

* Python 2 (2.6 or later)

* GTK+3

* Nautilus

* Nautilus-Python (most often packaged as python-nautilus)

* Python Imaging Library (python-imaging)

* Python binding to exiv2 (python-pyexiv2) (optional)

Note: you can use Nautilus Image Manipulator without Nautilus, but without the
one feature that makes is interesting, i.e. the Nautilus extension...

Retrieving the source code
^^^^^^^^^^^^^^^^^^^^^^^^^^
You can get the source in two ways:

* from a `release tarball`_

* from the `Bazaar source code repository`_::

    bzr branch lp:nautilus-image-manipulator

Install the Nautilus extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In order for Nautilus to display the option to use Nautilus Image Manipulator
when right-clicking one or more images, you need to place the Nautilus
extension file
``nautilus_image_manipulator/nautilus-image-manipulator-extension.py`` in one
of these 2 directories:

* ``/usr/share/nautilus-python/extensions`` (for all users of the system)

* ``~/.local/share/nautilus-python/extensions/`` (only for your current user)

You can do this by creating a symbolic link like this::

    ln -s nautilus_image_manipulator/nautilus-image-manipulator-extension.py ~/.local/share/nautilus-python/extensions

Don't forget to restart Nautilus for the new extension to be visible. You can do
that by restarting your session, or by executing these commands::

    killall nautilus; nautilus --no-desktop

Running it without the Nautilus extension
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The script to run is ``./bin/nautilus-image-manipulator``. You will have to pass
one or more images files using the ``-f`` parameter. Example::

    ./bin/nautilus-image-manipulator -f ~/Images/733.jpg -f ~/Images/hyperion3_cassini_1024.jpg

Hint: add the ``-v`` parameter to display debug information. Can be useful when
trying to determine what is going on.


.. _Python: http://python.org/
.. _GTK+ version 3: http://www.gtk.org/

.. _Debian: http://packages.qa.debian.org/n/nautilus-image-manipulator.html
.. _Ubuntu: https://launchpad.net/nautilus-image-manipulator/+packages
.. _Arch: http://aur.archlinux.org/packages.php?ID=56144

.. _release tarball: https://launchpad.net/nautilus-image-manipulator/+download
.. _Bazaar source code repository: https://code.launchpad.net/nautilus-image-manipulator

