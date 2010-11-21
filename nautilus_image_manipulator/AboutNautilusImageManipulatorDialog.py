# -*- coding: utf-8 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

import gtk

from nautilus_image_manipulator.helpers import get_builder

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class AboutNautilusImageManipulatorDialog(gtk.AboutDialog):
    __gtype_name__ = "AboutNautilusImageManipulatorDialog"

    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated AboutNautilusImageManipulatorDialog object.
        """
        builder = get_builder('AboutNautilusImageManipulatorDialog')
        new_object = builder.get_object("about_nautilus_image_manipulator_dialog")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initalizing should be called after parsing the ui definition
        and creating a AboutNautilusImageManipulatorDialog object with it in order to
        finish initializing the start of the new AboutNautilusImageManipulatorDialog
        instance.
        
        Put your initialization code in here and leave __init__ undefined.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.builder.connect_signals(self)

        # Code for other initialization actions should be added here.


if __name__ == "__main__":
    dialog = AboutNautilusImageManipulatorDialog()
    dialog.show()
    gtk.main()
