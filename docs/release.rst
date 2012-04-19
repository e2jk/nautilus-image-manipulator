.. _release:

Releasing Nautilus Image Manipulator
====================================
These are the different steps to perform when releasing a new version of
Nautilus Image Manipulator:

Update the version number
-------------------------
Change the version number in 2 places:

* ``./setup.py`` as "version" argument of "DistUtilsExtra.auto.setup"

* ``./bin/nautilus-image-manipulator`` as argument of "optparse.OptionParser"

Update the CHANGELOG
--------------------
Make sure the CHANGELOG file mentions the changes since the last release.

Create the release tarball
--------------------------
Place yourself in the root of the project and execute::

   python setup.py sdist

This will create a tarball of the source code
``./dist/nautilus-image-manipulator-<VERSION>.tar.gz``

Publish the new release on Launchpad
------------------------------------
The previously created file should be uploaded to Launchpad as the source
package of this new release:

* Go to https://launchpad.net/nautilus-image-manipulator/trunk/+addrelease

* Click on "Create milestone", enter the version number (for instance
  "|version|") as the name

* Enter today's date in "Date released"

* Add that release's text from the ``CHANGELOG`` in the "Changelog" section

* Click on "Create Release"

* Click on "Add download file"

* Enter "Source tarball" in "Description", select the tarball created in the
  previous step, and select "Code Release Tarball" as "File content type"

* Upload the new release!

* Go to https://launchpad.net/nautilus-image-manipulator/+announce and make an
  announcement!

Update the Debian package
-------------------------
Follow the `Debian New Maintainers' Guide`_, starting with chapter
`9. Updating the package`_.

.. _Debian New Maintainers' Guide: http://www.debian.org/doc/manuals/maint-guide/index.en.html
.. _9. Updating the package: http://www.debian.org/doc/manuals/maint-guide/update.en.html#newupstream
