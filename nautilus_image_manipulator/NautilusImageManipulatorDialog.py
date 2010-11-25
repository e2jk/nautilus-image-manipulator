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

import gtk, gobject

from nautilus_image_manipulator.helpers import get_builder
from ImageManipulations import resize_images

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
        self.builder.get_object("subdirectory_name_entry").set_sensitive(True)
        self.builder.get_object("append_name_entry").set_sensitive(False)

    def resize(self, widget, data=None):
        """The user has elected to resize the images

        Called before the dialog returns gtk.RESONSE_OK from run().
        """
        # Test files (they should be provided by the nautilus extension)
        files = ["/home/emilien/Bureau/test/IMG_0185.JPG", "/home/emilien/Bureau/test/IMG_0186.JPG"]
        files = ["/home/emilien/Bureau/test/IMG_0185.JPG", "/home/emilien/Bureau/test/IMG_0186.JPG", "/home/emilien/Bureau/test/IMG_0186.JPG", "/home/emilien/Bureau/test/IMG_0186.JPG", "/home/emilien/Bureau/test/IMG_0186.JPG"]
        #files = ["/home/emilien/Bureau/test/IMG_0186.JPG"]

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
        geometry = None # The size parameters for the resizing operation
        # Resize using default values
        if self.builder.get_object("default_size_radiobutton").get_active():
            geometry = self.builder.get_object("size_combobox").get_active_text()

        # Resize using a custom scale value
        elif self.builder.get_object("custom_scale_radiobutton").get_active():
            geometry = "%d%%" % int(self.builder.get_object("scale_spinbutton").get_value())

        # Resize using custom scale values
        elif self.builder.get_object("custom_size_radiobutton").get_active():
            geometry = "%dx%d" % (int(self.builder.get_object("width_spinbutton").get_value()), int(self.builder.get_object("height_spinbutton").get_value()))
        
        if geometry:
            # Disable the parameter UI elements and display the progress bar
            self.builder.get_object("parameters_vbox").set_sensitive(False)
            self.builder.get_object("resize_button").set_sensitive(False)
            self.builder.get_object("progress_progressbar").set_text("%s 0%%" % _("Resizing images..."))
            self.builder.get_object("progress_progressbar").show()
            while gtk.events_pending():
                gtk.main_iteration() # Used to refresh the UI
            # Resize the images
            task = resize_images(self, files, geometry, subdirectoryName, appendString)
            gobject.idle_add(task.next)

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

    def on_size_option_toggled(self, widget, data=None):
        """Updates the sensitiveness of the size option fields depending on which option is chosen."""
        if widget.get_active():
            isDefaultSize = (widget == self.builder.get_object("default_size_radiobutton"))
            self.builder.get_object("size_combobox").set_sensitive(isDefaultSize)
            self.builder.get_object("def_size_pixels_label").set_sensitive(isDefaultSize)
            isScale = (widget == self.builder.get_object("custom_scale_radiobutton"))
            self.builder.get_object("scale_spinbutton").set_sensitive(isScale)
            self.builder.get_object("scale_percent_label").set_sensitive(isScale)
            isCustomSize = (widget == self.builder.get_object("custom_size_radiobutton"))
            self.builder.get_object("custom_width_label").set_sensitive(isCustomSize)
            self.builder.get_object("width_spinbutton").set_sensitive(isCustomSize)
            self.builder.get_object("custom_height_label").set_sensitive(isCustomSize)
            self.builder.get_object("height_spinbutton").set_sensitive(isCustomSize)
            self.builder.get_object("custom_pixels_label").set_sensitive(isCustomSize)

    def on_filename_toggled(self, widget, data=None):
        """Updates the sensitiveness of the filename entry boxes depending on which option is chosen."""
        if widget.get_active():
            self.builder.get_object("subdirectory_name_entry").set_sensitive(widget == self.builder.get_object("subdirectory_radiobutton"))
            self.builder.get_object("append_name_entry").set_sensitive(widget == self.builder.get_object("append_radiobutton"))

    def on_send_toggled(self, widget, data=None):
        """Updates the sensitiveness of the elements involved with sending the images."""
        doSend = widget.get_active()
        self.builder.get_object("upload_radiobutton").set_sensitive(doSend)
        self.builder.get_object("upload_combobox").set_sensitive(doSend and self.builder.get_object("upload_radiobutton").get_active())
        self.builder.get_object("send_email_radiobutton").set_sensitive(doSend)

    def on_send_type_toggled(self, widget, data=None):
        """Updates the sensitiveness of the upload combobox when changing the sending options."""
        self.builder.get_object("upload_combobox").set_sensitive(self.builder.get_object("upload_radiobutton").get_active())

    def error_with_parameters(self, error_message):
        """Displays an error message if the parameters given to resize the images are not valid."""
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
