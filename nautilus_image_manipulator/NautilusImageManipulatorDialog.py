# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2011 Emilien Klein <emilien _AT_ klein _DOT_ st>
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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import ConfigParser
import os
import urllib2
import logging

from nautilus_image_manipulator.helpers import get_builder
from nautilus_image_manipulator.ImageManipulations import ImageManipulations

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class NautilusImageManipulatorDialog(Gtk.Dialog):
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

        # Load the saved configuration
        self.loadConfig()
        
        self.processingCanceled = False
        
    def set_files(self, files):
        self.files = files

    def resize_images(self, widget, data=None):
        """The user has elected to resize the images

        Called before the dialog returns Gtk.RESONSE_OK from run().
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
            if appendString[-1] == os.path.sep:
                # If the appendString ends in "/", the image would be
                # called ".EXT", which is a hidden file in it's own folder.
                self.error_with_parameters(
                       _("The string to append cannot end in %s") %
                       os.path.sep)
                return
            # TODO: Check that the value is valid to be appended to the filename

        elif self.builder.get_object("inplace_radiobutton").get_active():
            # Nothing to do
            pass
        
        # Determine the resizing parameters
        geometry = None # The size parameters for the resizing operation
        # Resize using default values
        if self.builder.get_object("default_size_radiobutton").get_active():
            model = self.builder.get_object("size_combobox").get_model()
            iterator = self.builder.get_object("size_combobox").get_active_iter()
            geometry = model.get_value(iterator, 0)




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
            while Gtk.events_pending():
                Gtk.main_iteration() # Used to refresh the UI
            # Resize the images
            im = ImageManipulations(self, self.files, geometry, subdirectoryName, appendString)
            im.connect("resizing_done", self.on_resizing_done)
            task = im.resize_images()
            GObject.idle_add(task.next)

        # Remember the settings for next time
        self.saveConfig()

    def on_resizing_done(self, im):
        """Triggered when all the images have been resized"""
        # Only pack and send the images if the process was not canceled and if there is at least one image to pack
        if self.builder.get_object("send_checkbutton").get_active() and not self.processingCanceled and len(im.newFiles) > 0:
            if self.builder.get_object("upload_radiobutton").get_active():
                # The user wants to upload to a website
                if len(im.newFiles) > 1:
                    # There are more than one image, zip the files together and upload the zipfile
                    im.connect("packing_done", self.on_packing_done)
                    task = im.pack_images()
                    GObject.idle_add(task.next)
                else:
                    # There is only one image, send that image alone (don't zip the file)
                    self.upload_file(im, im.newFiles[0])
            elif self.builder.get_object("send_email_radiobutton").get_active():
                # The user wants to send the images via email, send them as attachments
                # TODO: implement the sending as email attachments
                pass
        else:
            # The user doesn't want to send the images, we're done!
            self.destroy()

    def on_packing_done(self, im, zipfile):
        """Triggered when all the images have been packed together."""
        self.upload_file(im, zipfile)

    def upload_file(self, im, fileToUpload):
        """Uploads a file to a website."""
        model = self.builder.get_object("upload_combobox").get_model()
        iterator = self.builder.get_object("upload_combobox").get_active_iter()
        uploadSiteName = model.get_value(iterator, 0)
        # Import the module that takes care of uploading to the selected website
        import_string = "from upload.z%s import UploadSite" % uploadSiteName.replace(".", "").replace("/", "")
        # Make sure the import does not fail
        try:
            exec import_string
        except ImportError:
            if os.path.splitext(fileToUpload)[1] == ".zip":
                extraInfo = _("Your images have not been sent, but have been zipped together into this file:\n%(filename)s" % {"filename": fileToUpload})
            else:
                extraInfo = _("Your image has not been sent, but has successfully been resized.\nYou can find it at %(filename)s" % {"filename": fileToUpload})
            self.display_error(_("The selected upload site %(site_name)s is not valid." % {"site_name": '"%s"' % uploadSiteName}) + "\n\n" + extraInfo, (_("Please file a bug report on Launchpad"), "https://bugs.launchpad.net/nautilus-image-manipulator"))
            return
        u = None
        try:
            u = UploadSite()
        except urllib2.URLError:
            # Impossible to contact the website (no network, site down, etc.)
            if os.path.splitext(fileToUpload)[1] == ".zip":
                extraInfo = _("Your images have not been sent, but have been zipped together into this file:\n%(filename)s" % {"filename": fileToUpload})
            else:
                extraInfo = _("Your image has not been sent, but has successfully been resized.\nYou can find it at %(filename)s" % {"filename": fileToUpload})
            self.display_error(_("The upload site %(site_name)s could not be contacted, please check your internet connection." % {"site_name": '"%s"' % uploadSiteName}) + "\n\n" + extraInfo)
            return
        
        self.builder.get_object("progress_progressbar").set_text("%s 0%%" % _("Uploading images..."))
        self.builder.get_object("progress_progressbar").set_fraction(0)
        self.uploadPercent = 0
        (downloadPage, deletePage) = u.upload(fileToUpload, self.uploading_callback)
        logging.info('downloadPage: %s' % downloadPage)
        logging.info('deletePage: %s' % deletePage)
        #(downloadPage, deletePage) = ("http://TTTTT.1fichier.com", "http://www.1fichier.com/remove/TTTTT/VVVVV")
        # Put the download url in the clipboard (both the normal "Ctrl-C" and selection clipboards)
        # Note that the selection clipboard will be empty when the dialog gets closed.
        # More info: http://standards.freedesktop.org/clipboards-spec/clipboards-latest.txt
        
        #TODO: Removed clipboard functionality when migrating to GTK+ 3. Will need to be updated to work again.
        #gtk.Clipboard(gtk.gdk.display_get_default(), "CLIPBOARD").set_text(downloadPage)
        #gtk.Clipboard(gtk.gdk.display_get_default(), "PRIMARY").set_text(downloadPage)
        self.on_uploading_done(downloadPage, deletePage)

    def display_error(self, msg, urlInfo=None):
        """Displays an error message.
        
        Using the option ``urlInfo`` parameter, you can diplay a link button to open a url.
        This parameter is a tuple of the form (message, url)"""
        # Hide the unneccessary sections
        self.builder.get_object("parameters_vbox").hide()
        self.builder.get_object("progress_progressbar").hide()
        self.builder.get_object("upload_url_vbox").hide()
        # Display the error message
        self.builder.get_object("error_message_label").set_text(msg)
        self.builder.get_object("error_vbox").show()
        # Hide the cancel and resize button, and show the close button
        self.builder.get_object("cancel_button").hide()
        self.builder.get_object("resize_button").hide()
        self.builder.get_object("close_button").show()
        # Eventually display an url
        if urlInfo:
            self.builder.get_object("error_url_linkbutton").set_label(urlInfo[0])
            self.builder.get_object("error_url_linkbutton").set_uri(urlInfo[1])
            self.builder.get_object("error_url_hbox").show()
        else:
            self.builder.get_object("error_url_hbox").hide()
        #TODO: Make the close button the default behavior (to respond to Enter)
        self.resize(1, 1)

    def uploading_callback(self, param, current, total):
        """This function gets called when uploading the images.
        
        It updates the progress bar according to the progress of the upload."""
        percent = float(current)/total
        percent100 = int(percent * 100)
        if percent100 > self.uploadPercent:
            self.builder.get_object("progress_progressbar").set_text("%s %d%%" % (_("Uploading images..."), percent100))
            self.builder.get_object("progress_progressbar").set_fraction(percent)
            while Gtk.events_pending():
                Gtk.main_iteration() # Used to refresh the UI
            self.uploadPercent = percent100

    def on_uploading_done(self, downloadPage, deletePage):
        """Displays the url where the images can be downloaded from, or deleted."""
        self.builder.get_object("parameters_vbox").hide()
        self.builder.get_object("progress_progressbar").hide()
        # Update the link buttons with the urls
        self.builder.get_object("download_linkbutton").set_label(downloadPage)
        self.builder.get_object("download_linkbutton").set_uri(downloadPage)
        self.builder.get_object("delete_linkbutton").set_label(deletePage)
        self.builder.get_object("delete_linkbutton").set_uri(deletePage)
        self.builder.get_object("upload_url_vbox").show()
        # Hide the cancel and resize button, and show the close button
        self.builder.get_object("cancel_button").hide()
        self.builder.get_object("resize_button").hide()
        self.builder.get_object("close_button").show()
        self.resize(1, 1)
        

    def cancel(self, widget, data=None):
        """The user has elected to cancel.

        Called before the dialog returns Gtk.ResponseType.CANCEL for run()
        """
        self.destroy()

    def on_destroy(self, widget, data=None):
        """Called when the NautilusImageManipulatorWindow is closed."""
        # Note: The parameters don't get saved when canceling. It is called at the end of self.resize().
        Gtk.main_quit()

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
        if widget.get_active():
            self.builder.get_object("send_options_hbox").show()
        else:
            self.builder.get_object("send_options_hbox").hide()
            self.resize(1, 1)

    def on_send_type_toggled(self, widget, data=None):
        """Updates the sensitiveness of the upload combobox when changing the sending options."""
        self.builder.get_object("upload_combobox").set_sensitive(self.builder.get_object("upload_radiobutton").get_active())

    def error_with_parameters(self, error_message):
        """Displays an error message if the parameters given to resize the images are not valid."""
        label = Gtk.Label(label=error_message)
        label.set_padding(10, 5)
        dialog = Gtk.Dialog(_("Invalid parameters"),
                           self,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        response = dialog.run()
        dialog.destroy()

    def error_resizing(self, filename=None, dependencyMissing=False):
        """Displays an error message if ImageMagick returned an error while resizing one image."""
        label = None
        if filename:
            (folder, image) = os.path.split(filename)
            buttons =(_("_Skip"), 0,
                   Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   _("_Retry"), 1)
            label = Gtk.Label(label=_('The image "%(image)s" could not be resized.\n\nCheck whether you have permission to write to this folder:\n%(folder)s' % {"image": image, "folder": folder}))
        if dependencyMissing:
            buttons =(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                   _("_Retry"), 1)
            label = Gtk.Label(label=_("The image conversion program wasn't found on your system.\nHave you installed ImageMagick?"))
        label.set_padding(10, 5)
        dialog = Gtk.Dialog(_("Could not resize image"),
                           self,
                           Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                           buttons)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        response = dialog.run()
        dialog.destroy()
        # The values to be returned
        skip = (response == 0)
        self.processingCanceled = (response == Gtk.ResponseType.CANCEL)
        retry = (response == 1)
        return (skip, self.processingCanceled, retry)

    def loadConfig(self):
        """Read the ini file to get the previous configuration. The ini file is located at ~/.nautilus-image-manipulator.ini.
        
        If no previous values are found, sets the UI to default values."""
        self.configFilename = os.path.expanduser("~/.nautilus-image-manipulator.ini")
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.configFilename)
        if len(self.config.sections()) > 0:
            # TODO: take care of eventual exceptions if a value is not set
            # Resize
            size_combobox_value = self.config.getint("Resize", "size_combobox")
            scale_adjustment_value = self.config.getint("Resize", "scale_adjustment")
            width_adjustment_value = self.config.getint("Resize", "width_adjustment")
            height_adjustment_value = self.config.getint("Resize", "height_adjustment")
            toggled_size_radiobutton = self.config.get("Resize", "toggled_size_radiobutton")
            
            # Output
            subdirectory_name_entry_value = self.config.get("Output", "subdirectory_name_entry")
            append_name_entry_value = self.config.get("Output", "append_name_entry")
            toggled_output_radiobutton = self.config.get("Output", "toggled_output_radiobutton")
            
            # Sending
            is_send_checkbutton_toggled = self.config.getboolean("Sending", "is_send_checkbutton_toggled")
            toggled_sending_option_radiobutton = self.config.get("Sending", "toggled_sending_option_radiobutton")
            upload_combobox_value = self.config.getint("Sending", "upload_combobox")
            
            # TODO: Make sure that the values read from the ini file are valid, else use default values
        else:
            # Default parameters
            # Resize
            size_combobox_value = 4
            scale_adjustment_value = 50
            width_adjustment_value = 1000
            height_adjustment_value = 1000
            toggled_size_radiobutton = "default_size_radiobutton"
            
            # Output
            toggled_output_radiobutton = "subdirectory_radiobutton"
            # Default name of the subdirectory in which the resized images will be put
            subdirectory_name_entry_value = _("resized")
            # Default value of the string that will be appended to the filename of the resized images
            append_name_entry_value = _("-resized")
            
            # Sending
            is_send_checkbutton_toggled = False
            toggled_sending_option_radiobutton = "upload_radiobutton"
            upload_combobox_value = 0
        
        # Update the UI with the previous (or default) values
        # Size parameters
        self.builder.get_object("size_combobox").set_active(size_combobox_value)
        self.builder.get_object("scale_adjustment").set_value(scale_adjustment_value)
        self.builder.get_object("width_adjustment").set_value(width_adjustment_value)
        self.builder.get_object("height_adjustment").set_value(height_adjustment_value)
        self.builder.get_object(toggled_size_radiobutton).set_active(True)
        
        # Output parameters
        self.builder.get_object("subdirectory_name_entry").set_text(subdirectory_name_entry_value)
        self.builder.get_object("append_name_entry").set_text(append_name_entry_value)
        self.builder.get_object(toggled_output_radiobutton).set_active(True)
        
        # Sending parameters
        self.builder.get_object("send_checkbutton").set_active(is_send_checkbutton_toggled)
        self.builder.get_object(toggled_sending_option_radiobutton).set_active(True)
        self.builder.get_object("upload_combobox").set_active(upload_combobox_value)

    def saveConfig(self):
        """Save the current configuration in the ini file"""
        f = open(self.configFilename, "w")
        
        if not self.config.has_section("Resize"):
            self.config.add_section("Resize")
        self.config.set("Resize", "size_combobox", int(self.builder.get_object("size_combobox").get_active()))
        for v in ("scale_adjustment", "width_adjustment", "height_adjustment"):
            self.config.set("Resize", v, int(self.builder.get_object(v).get_value()))
        for b in ("default_size_radiobutton", "custom_scale_radiobutton", "custom_size_radiobutton"):
            if self.builder.get_object(b).get_active():
                self.config.set("Resize", "toggled_size_radiobutton", b)
        
        if not self.config.has_section("Output"):
            self.config.add_section("Output")
        for v in ("subdirectory_name_entry", "append_name_entry"):
            self.config.set("Output", v, self.builder.get_object(v).get_text())
        for b in ("subdirectory_radiobutton", "append_radiobutton", "inplace_radiobutton"):
            if self.builder.get_object(b).get_active():
                self.config.set("Output", "toggled_output_radiobutton", b)
        
        if not self.config.has_section("Sending"):
            self.config.add_section("Sending")
        self.config.set("Sending", "is_send_checkbutton_toggled", self.builder.get_object("send_checkbutton").get_active())
        for b in ("upload_radiobutton", "send_email_radiobutton"):
            if self.builder.get_object(b).get_active():
                self.config.set("Sending", "toggled_sending_option_radiobutton", b)
        self.config.set("Sending", "upload_combobox", int(self.builder.get_object("upload_combobox").get_active()))
        
        self.config.write(f)


if __name__ == "__main__":
    pass
