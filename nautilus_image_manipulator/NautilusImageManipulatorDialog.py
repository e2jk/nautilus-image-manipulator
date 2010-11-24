# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010 Emilien Klein <emilien _AT_ klein _DOT_ st>
# 
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

import gtk

from nautilus_image_manipulator.helpers import get_builder

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class NautilusImageManipulatorDialog(gtk.Dialog):
    __gtype_name__ = "NautilusImageManipulatorDialog"
    
    # To construct a new instance of this method, the following notable 
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your inialization code in finish_intializing

    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated NautilusImageManipulatorDialog object.
        """
        builder = get_builder('NautilusImageManipulatorDialog')
        new_object = builder.get_object('nautilus_image_manipulator_dialog')
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called when we're finished initializing.

        finish_initalizing should be called after parsing the ui definition
        and creating a NautilusImageManipulatorDialog object with it in order to
        finish initializing the start of the new NautilusImageManipulatorDialog
        instance.
        
        Put your initilization code in here and leave __init__ undefined.
        """
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.builder.connect_signals(self)

        # Code for other initialization actions should be added here.
        # TODO: Reuse last time's settings

    def resize(self, widget, data=None):
        """The user has elected to resize the images

        Called before the dialog returns gtk.RESONSE_OK from run().
        """

        # Determine the output filenames
        subdirectoryName = ""
        appendString = ""
        if self.builder.get_object("subdirectory_radiobutton").get_active():
            subdirectoryName = self.builder.get_object("subdirectory_name_entry").get_text()
            if not subdirectoryName:
                self.error_with_parameters(_("Please enter a value for the subdirectory."))
                return
            # TODO: Check that the value is a valid subdirectory name

        elif self.builder.get_object("append_radiobutton").get_active():
            appendString = self.builder.get_object("append_name_entry").get_text()
            if not appendString:
                self.error_with_parameters(_("Please enter some text to append to the filename."))
                return
            # TODO: Check that the value is valid to be appended to the filename

        elif self.builder.get_object("inplace_radiobutton").get_active():
            # Nothing to do
            pass

        # Determine the resizing parameters
        # Resize using default values
        if self.builder.get_object("default_size_radiobutton").get_active():
            pass

        # Resize using a custom scale value
        elif self.builder.get_object("custom_scale_radiobutton").get_active():
            # TODO: Support resizing according to a custom scale
            pass

        # Resize using custom scale values
        elif self.builder.get_object("custom_size_radiobutton").get_active():
            # TODO: Support resizing according to custom values
            pass

        # TODO: Remember the settings for next time

    def cancel(self, widget, data=None):
        """The user has elected to cancel.

        Called before the dialog returns gtk.RESPONSE_CANCEL for run()
        """
        self.destroy()

    def on_destroy(self, widget, data=None):
        """Called when the NautilusImageManipulatorWindow is closed."""
        # Clean up code for saving application state should be added here.
        gtk.main_quit()

    def error_with_parameters(self, error_message):
        label = gtk.Label(error_message)
        label.set_padding(10, 5)
        dialog = gtk.Dialog(_("Invalid parameters"),
                           self,
                           gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                           (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        dialog.vbox.pack_start(label)
        label.show()
        response = dialog.run()
        dialog.destroy()


if __name__ == "__main__":
    pass
