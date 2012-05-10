.. _usage:

Usage
=====
Once Nautilus Image Manipulator is installed on your system, you'll most
probably want to use it... Right?

Launching Nautilus Image Manipulator
------------------------------------
Open Nautilus (the file manager in Gnome) and browse to a folder containing
images. Select one or more, and right-click one. In the menu that appears, you
will see a line that says "Resize images...":

.. figure:: /images/NautilusImageManipulatorExtension.png
   :alt: The Nautilus plugin in action
   :align: center
   
   Right-clicking on images gives you the option to "Resize images..."

When clicking on that menu option, Nautilus Image Manipulator will open and
allow you to resize the selected images, and send them to friends and family if
you so wish. This is how it looks like the first time that it's run:

.. figure:: /images/InitialWindow.png
   :alt: Nautilus Image Manipulator as seen on first launch
   :align: center
   
   How Nautilus Image Manipulator looks like the first time it's launched

Working with profiles
---------------------
Resizing and sending images with Nautilus Image Manipulator is done using
profiles. Those represent a set of parameters that will be applied to all the
images being worked on.

Nautilus Image Manipulator comes with 4 default profiles to get you started:

* Send small images to 1fichier.com

   This profile will create images that are maximum 640 pixels wide and 640
   pixels high, and the quality of the images is set to 90%. Those images are
   then zipped together in a file that will be sent to the file locker website
   http://www.1fichier.com.

* Create small images in the "resized" folder

   The images produced by this profile will be of the same size (640x640) and
   quality (90%) as the previous profile, but will be put inside the
   ``./resized`` folder instead of being sent on the Internet.

* Send large images to 1fichier.com

   This profile will create images that are maximum 1280 pixels wide and 1280
   pixels high, and the quality of the images is set to 95%. Those images are
   then zipped together in a file that will be sent to the file locker website
   http://www.1fichier.com.
   
* Create large images in the "resized" folder

   The images produced by this profile will be of the same size (1280x1280)
   and quality (95%) as the previous profile, but will be put inside the
   ``./resized`` folder instead of being sent on the Internet.


Custom settings
---------------

TODO

Managing profiles
-----------------

Adding a profile
^^^^^^^^^^^^^^^^
TODO

Removing a profile
^^^^^^^^^^^^^^^^^^
TODO
