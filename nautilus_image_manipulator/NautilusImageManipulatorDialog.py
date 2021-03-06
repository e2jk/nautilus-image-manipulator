# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2013 Emilien Klein <emilien _AT_ klein _DOT_ st>
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
import os
import urllib2
import logging

from nautilus_image_manipulator.helpers import get_builder
from nautilus_image_manipulator.ImageManipulations import ImageManipulations
from ProfileSettings import Profile, Config
from upload.BaseUploadSite import UnknownUploadDestinationException
from upload.BaseUploadSite import InvalidEndURLsException
from upload.BaseUploadSite import FinalURLsNotFoundException

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
        
        Put your initialization code in here and leave __init__ undefined.
        """
        # Get a reference to the builder's get_object and set up the signals.
        self.o = builder.get_object
        builder.connect_signals(self)

        # Populate the list of sites to upload to
        model = self.o("upload_combo").get_model()
        self.upload_sites = [model.get_value(model.get_iter(i), 0) for \
                             i, k in enumerate(model)]

        # Load the saved configuration
        self.loadConfig()
        self.processingCanceled = False

        # Give the Resize button the focus to respond to Enter
        self.o("resize_button").grab_focus()

    def set_files(self, files):
        self.files = files

    def resize_button_clicked(self, widget, data=None):
        """The user has elected to resize the images

        Called before the dialog returns Gtk.RESONSE_OK from run().
        """
        idSelectedProfile = self.o("profiles_combo").get_active()
        # If the custom profile was selected, update it with the currently
        # selected parameters
        if idSelectedProfile == (len(self.conf.profiles) - 1):
            p = self.create_new_profile_from_custom_settings()
            p.name = _("Custom settings")
            self.conf.profiles[idSelectedProfile] = p
        self.p = self.conf.profiles[idSelectedProfile]
        logging.info("The following profile has been selected:\n%s" % self.p)

        # Disable the parameter UI elements and display the progress bar
        self.o("details_box").set_sensitive(False)
        self.o("resize_button").set_sensitive(False)
        self.o("deleteprofile_button").set_visible(False)
        self.o("newprofile_button").set_visible(False)
        self.o("progressbar").set_text("%s 0%%" % ("Resizing images..."))
        self.o("progressbar").show()
        while Gtk.events_pending():
            Gtk.main_iteration() # Used to refresh the UI
        # Resize the images
        im = ImageManipulations(self, self.files, self.p)
        im.connect("resizing_done", self.on_resizing_done)
        task = im.resize_images()
        GObject.idle_add(task.next)

        # Remember the settings for next time
        self.saveConfig()

    def destination_entry_changed_cb(self, widget, data=None):
        if widget == self.o("subfolder_entry"):
            isError = (0 == len(widget.get_text()))
            errorLabel = self.o("subfolder_entry_error_label")
        elif widget == self.o("append_entry"):
            errorLabel = None
            if 0 == len(widget.get_text()):
                isError = True
                self.o("append_entry_empty_error_label").set_visible(True)
                self.o("append_entry_invalid_error_label").set_visible(False)
            elif os.path.sep == widget.get_text()[-1]:
                isError = True
                self.o("append_entry_invalid_error_label").set_text(_("The string to append cannot end in %s") % os.path.sep)
                self.o("append_entry_empty_error_label").set_visible(False)
                self.o("append_entry_invalid_error_label").set_visible(True)
            else:
                # TODO: Check that the value is valid to be appended to the filename
                isError = False
                self.o("append_entry_empty_error_label").set_visible(False)
                self.o("append_entry_invalid_error_label").set_visible(False)
        elif widget == self.o("zipname_entry"):
            isError = (0 == len(widget.get_text()))
            errorLabel = self.o("zipname_entry_error_label")

        # Adapt the visibility of the appropriate error message
        if errorLabel:
            errorLabel.set_visible(isError)
        # Don't allow resizing if text is empty
        self.o("resize_button").set_sensitive(not isError)

    def on_resizing_done(self, im):
        """Triggered when all the images have been resized"""
        # Only pack and send the images if the process was not canceled and if there is at least one image to pack
        if self.p.destination == 'upload' and not self.processingCanceled and len(im.newFiles) > 0:
            # The user wants to upload to a website
            if len(im.newFiles) > 1:
                # There are more than one image, zip the files together and upload the zipfile
                im.connect("packing_done", self.on_packing_done)
                task = im.pack_images()
                GObject.idle_add(task.next)
            else:
                # There is only one image, send that image alone (don't zip the file)
                self.upload_file(im, im.newFiles[0])
        else:
            # The user doesn't want to send the images, we're done!
            self.destroy()

    def on_packing_done(self, im, zipfile):
        """Triggered when all the images have been packed together."""
        self.upload_file(im, zipfile)

    def upload_file(self, im, fileToUpload):
        """Uploads a file to a website."""
        # Import the module that takes care of uploading to the selected website
        import_string = "from upload.z_%s import UploadSite" % \
                self.p.url.replace(".", "_").replace("/", "")
        logging.debug("import_string: %s" % import_string)
        # Make sure the import does not fail
        try:
            exec import_string
        except ImportError:
            self.error_on_uploading(_("The selected upload site %(site_name)s is not valid.") % {"site_name": '"%s"' % self.p.url} + "\n\n%(extra_info)s", fileToUpload, True)
            return
        u = None
        try:
            u = UploadSite()
        except urllib2.URLError:
            # Impossible to contact the website (no network, site down, etc.)
            self.error_on_uploading(_("The upload site %(site_name)s could not be contacted, please check your internet connection.") % {"site_name": '"%s"' % self.p.url} + "\n\n%(extra_info)s", fileToUpload, False)
            return
        except UnknownUploadDestinationException:
            self.error_on_uploading(_("The upload destination for %(site_name)s could not be determined, please report a bug so that this can be fixed.") % {"site_name": '"%s"' % self.p.url} + "\n\n%(extra_info)s", fileToUpload, True)
            return

        self.o("progressbar").set_text("%s 0%%" % _("Uploading images..."))
        self.o("progressbar").set_fraction(0)
        self.uploadPercent = 0
        u.connect("uploading_done", self.on_uploading_done)
        u.connect("waiting_for_validation", self.waiting_for_validation)
        try:
            u.upload(fileToUpload, self.uploading_callback)
        except InvalidEndURLsException:
            self.error_on_uploading(_("The page where your file can be downloaded from could not be determined.") + "\n" + _("Please try again, and report a bug if it happens again.") + "\n\n%(extra_info)s", fileToUpload, True)
            return
        except FinalURLsNotFoundException:
            self.error_on_uploading(_("Your images were successfully uploaded to %(site_name)s, but their verification failed.") % {"site_name": '"%s"' % self.p.url} + "\n" + _("Please try again, and report a bug if it happens again.") + "\n\n%(extra_info)s", fileToUpload, True)
            return

    def error_on_uploading(self, message, fileToUpload, reportBug):
        """Displays an error message.
        
        Can also display a link to report a bug on Launchpad"""
        if os.path.splitext(fileToUpload)[1] == ".zip":
            extra_info = _("Your images have been zipped together into this file:") + "\n" + fileToUpload
        else:
            extra_info = _("You can find your image at %(filename)s") % {"filename": fileToUpload}
        # Hide the unneccessary sections
        self.o("details_box").hide()
        self.o("progressbar").hide()
        self.o("url_box").hide()
        # Display the error message
        self.o("error_message_label").set_text(message % {"extra_info": extra_info})
        self.o("error_box").show()
        # Hide the cancel and resize button, and show the close button
        self.o("cancel_button").hide()
        self.o("resize_button").hide()
        self.o("close_button").show()
        # Display the link to report a bug
        if reportBug:
            self.o("error_url_linkbutton").set_label(_("Please file a bug report on Launchpad"))
            self.o("error_url_linkbutton").set_uri("https://bugs.launchpad.net/nautilus-image-manipulator")
            self.o("error_url_hbox").show()
        else:
            self.o("error_url_hbox").hide()
        # Give the close button the focus to respond to Enter
        self.o("close_button").grab_focus()
        self.resize(1, 1)

    def uploading_callback(self, param, current, total):
        """This function gets called when uploading the images.
        
        It updates the progress bar according to the progress of the upload."""
        percent = float(current) / total
        percent100 = int(percent * 100)
        if percent100 > self.uploadPercent:
            self.o("progressbar").set_text("%s %d%%" % (_("Uploading images..."), percent100))
            self.o("progressbar").set_fraction(percent)
            while Gtk.events_pending():
                Gtk.main_iteration() # Used to refresh the UI
            self.uploadPercent = percent100

    def pulse(self):
        """Sets the progress bar in activity mode, and makes the block move
        back and forth within the progress bar"""
        self.o("progressbar").pulse()
        return self.still_working # True = repeat, False = stop

    def waiting_for_validation(self, u):
        """Triggered when the file has been uploaded, but has not yet been verified."""
        self.still_working = True
        self.o("progressbar").set_text(_("Waiting for validation..."))
        GObject.timeout_add(100, self.pulse)

    def on_uploading_done(self, u):
        """Triggered when the file has been uploaded.
        Displays the url where the images can be downloaded from, or deleted."""
        # Stop updating the progress bar
        self.still_working = False
        # Put the download url in the clipboard (both the normal "Ctrl-C" and selection clipboards)
        # Note that the selection clipboard will be empty when the dialog gets closed.
        # More info: http://standards.freedesktop.org/clipboards-spec/clipboards-latest.txt
        # and http://readthedocs.org/docs/python-gtk-3-tutorial/en/latest/clipboard.html
        Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(u.downloadPage, -1)
        Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).set_text(u.downloadPage, -1)

        self.o("details_box").hide()
        self.o("progressbar").hide()
        # Update the link buttons with the urls
        self.o("download_linkbutton").set_label(u.downloadPage)
        self.o("download_linkbutton").set_uri(u.downloadPage)
        self.o("delete_linkbutton").set_label(u.deletePage)
        self.o("delete_linkbutton").set_uri(u.deletePage)
        self.o("url_box").show()
        # Hide the cancel and resize button, and show the close button
        self.o("cancel_button").hide()
        self.o("resize_button").hide()
        self.o("close_button").show()
        self.resize(1, 1)

        #TODO: delete the temporary folder where the images where placed
        #Question: should the zipfile also be deleted?

    def cancel_button_clicked(self, widget, data=None):
        """The user has elected to cancel.

        Called before the dialog returns Gtk.ResponseType.CANCEL for run()
        """
        self.destroy()

    def on_destroy(self, widget, data=None):
        """Called when the NautilusImageManipulatorWindow is closed."""
        # Note: The parameters don't get saved when canceling. It is called at the end of self.resize().
        Gtk.main_quit()

    def profiles_combo_changed(self, widget, data=None):
        """Updates the UI according to which profile gets selected"""
        idCustomSettings = len(self.conf.profiles) - 1
        idSelectedProfile = self.o("profiles_combo").get_active()
        customSelected = (idCustomSettings == idSelectedProfile)
        # Only show the advanced parameters when the custom settings is selected
        self.o("parameters_box").set_visible(customSelected)
        self.o("deleteprofile_button").set_visible(customSelected == False)
        self.o("newprofile_button").set_visible(customSelected)
        if customSelected:
            self.set_advanced_settings_from_custom_profile()

    def set_advanced_settings_from_custom_profile(self):
        """Update the advance settings based on the custom settings profile"""
        p = self.conf.profiles[-1]
        # Size settings
        if p.percent:
            self.o("percent_radio").set_active(True)
            self.o("percent_scale").set_value(p.percent)
            # Set the size combobox by default to small
            self.o("size_combo").set_active(0)
        else:
            self.o("pixels_radio").set_active(True)
            if p.size:
                sizeSettings = ("small", "large").index(p.size)
            else:
                sizeSettings = 2
                self.o("width_spin").set_value(p.width)
                self.o("height_spin").set_value(p.height)
            self.o("size_combo").set_active(sizeSettings)
            self.size_radio_toggled(None)
        self.o("quality_scale").set_value(p.quality)
        # Force updating the color and tooltip of the quality scale (if
        # quality is too low)
        self.quality_scale_changed(None, None, p.quality)

        # Destination settings
        dest_model = self.o("destination_combo").get_model()
        dest_iter = dest_model.get_iter_first()
        while dest_iter is not None:
            dest = dest_model.get(dest_iter, 1)[0]
            if dest == p.destination:
                self.o("destination_combo").set_active_iter(dest_iter)
                break
            dest_iter = dest_model.iter_next(dest_iter)
        if p.destination == "append":
            self.o("append_entry").set_text(p.appendstring)
        elif p.destination == "folder":
            self.o("subfolder_entry").set_text(p.foldername)
        elif p.destination == 'upload':
            self.o("zipname_entry").set_text(p.zipname)
            try:
                i = self.upload_sites.index(p.url)
            except ValueError:
                i = 0
            self.o("upload_combo").set_active(i)

    def create_new_profile_from_custom_settings(self):
        """Returns a new profile instance based on the data in the advanced
        settings"""
        # Size settings
        size = None
        width = None
        height = None
        percent = None
        if self.o("pixels_radio").get_active():
            sizeSettings = self.o("size_combo").get_active()
            sizeSettings = ("small", "large", "custom")[sizeSettings]
            if sizeSettings == "custom":
                width = self.o("width_spin").get_value()
                height = self.o("height_spin").get_value()
            else:
                size = sizeSettings
        else:
            percent = self.o("percent_scale").get_value()
        quality = self.o("quality_scale").get_value()

        # Destination settings
        dest_model = self.o("destination_combo").get_model()
        dest_iter = self.o("destination_combo").get_active_iter()
        destination = dest_model.get_value(dest_iter, 1)
        appendstring = None
        foldername = None
        zipname = None
        url = None
        if destination == "append":
            appendstring = self.o("append_entry").get_text()
        elif destination == "folder":
            foldername = self.o("subfolder_entry").get_text()
        elif destination == 'upload':
            zipname = self.o("zipname_entry").get_text()
            url = self.o("upload_combo").get_active_text()

        # Create and add that profile to the list of profiles
        p = Profile(size, width, height, percent, quality, destination,
                    appendstring, foldername, zipname, url)
        return p

    def newprofile_button_clicked(self, widget, data=None):
        """Adds a new profile to the list of available profiles"""
        p = self.create_new_profile_from_custom_settings()
        profileNumber = self.conf.addprofile(p)
        self.populate_profiles_combobox(profileNumber)

    def deleteprofile_button_clicked(self, widget, data=None):
        profilesCombo = self.o("profiles_combo")
        idSelectedProfile = profilesCombo.get_active()
        # Remove from the list of profiles in self.conf
        self.conf.deleteprofile(idSelectedProfile)
        # Remove from the profiles combobox
        profilesCombo.remove(idSelectedProfile)
        # Determine which profile to select now
        if idSelectedProfile > 0 and (
           idSelectedProfile == len(self.conf.profiles) - 1):
            # If the last profile in the list before the custom settings
            # just got deleted, but there are still other profiles in the
            # list, select the new last profile.
            idSelectedProfile -= 1
        profilesCombo.set_active(idSelectedProfile)

    def size_radio_toggled(self, widget, data=None):
        if not widget:
            widget = self.o("pixels_radio")
        if widget == self.o("pixels_radio"):
            # This if condition prevents the call to be executed twice
            # (once for each radio button)
            pixels = widget.get_active()
            percent = not pixels
            self.o("size_combo").set_sensitive(pixels)
            self.update_width_height_box_sensitivity(pixels)
            self.o("percent_scale").set_sensitive(percent)
            self.o("percent_label").set_sensitive(percent)

    def size_combo_changed(self, widget, data=None):
        # Don't use the text of the combobox, since it will be translated.
        # Instead, use the selected ID and map it to one of the 3 values.
        sizeSettings = self.get_size_settings()
        self.update_width_height_box_sensitivity(True, sizeSettings)
        if sizeSettings in ("small", "large"):
            # Update the values to show the predetermined width and height
            (w, h) = Config.size[sizeSettings]
            self.o("width_spin").set_value(w)
            self.o("height_spin").set_value(h)

    def get_size_settings(self):
        s = self.o("size_combo").get_active()
        return ("small", "large", "custom")[s]

    def update_width_height_box_sensitivity(self, pixels, size=None):
        sensitive = False
        if pixels:
            if not size:
                size = self.get_size_settings()
            sensitive = (size == "custom")
        self.o("width_height_box").set_sensitive(sensitive)

    def quality_scale_changed(self, widget, data=None, value=0):
        #TODO: check if possible to make the quality scale red as well
        if value < 70:
            labeltext = "<span foreground='red'>%s</span>"
            # Visible when hovering over the quality scale in the custom
            # settings when the quality is too low
            tooltiptext = _("Warning: the lower the quality, the more "\
                            "deteriorated the images will be")
        else:
            labeltext = "%s"
            # Visible when hovering over the quality scale in the custom
            # settings when the quality is high enough
            tooltiptext = _("Determines the quality of the resized images "\
                            "(the higher the quality, the larger the image size)")
        self.o("quality_label").set_markup(labeltext % _("Quality:"))
        self.o("quality_percent_label").set_markup(labeltext % "%")
        self.o("quality_box").set_tooltip_text(tooltiptext)

    def destination_combo_changed(self, widget, data=None):
        dest_model = widget.get_model()
        dest_iter = widget.get_active_iter()
        dest = dest_model.get_value(dest_iter, 1)
        # Make sure the Resize button is clickable
        self.o("resize_button").set_sensitive(True)
        if dest == 'folder':
            if not self.o("subfolder_entry").get_text():
                # Default folder name
                self.o("subfolder_entry").set_text(_("resized"))
            self.o("subfolder_box").show()
            self.o("append_box").hide()
            self.o("upload_box").hide()
            self.destination_entry_changed_cb(self.o("subfolder_entry"))
        elif dest == 'append':
            if not self.o("append_entry").get_text():
                # Default value to append to filename
                self.o("append_entry").set_text("-%s" % _("resized"))
            self.o("subfolder_box").hide()
            self.o("append_box").show()
            self.o("upload_box").hide()
            self.destination_entry_changed_cb(self.o("append_entry"))
        elif dest == 'upload':
            if not self.o("zipname_entry").get_text():
                # Default zipfile name
                self.o("zipname_entry").set_text(_("resized"))
            if not self.o("upload_combo").get_active_text():
                # Default upload site
                self.o("upload_combo").set_active(0)
            self.o("subfolder_box").hide()
            self.o("append_box").hide()
            self.o("upload_box").show()
        else:
            self.o("subfolder_box").hide()
            self.o("append_box").hide()
            self.o("upload_box").hide()

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

    def error_resizing(self, filename):
        """Displays an error message if an error got detected while
        resizing one image."""
        label = None
        (folder, image) = os.path.split(filename)
        buttons = (_("_Skip"), 0,
               Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
               _("_Retry"), 1)
        label = Gtk.Label(label=_('The image "%(image)s" could not be resized.\n\nCheck whether you have permission to write to this folder:\n%(folder)s' % {"image": image, "folder": folder}))
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

    def populate_profiles_combobox(self, profileNumber=None):
        """Populate the profiles combobox with the names of the profiles"""
        profilesCombo = self.o("profiles_combo")
        # Empty the combobox
        profilesCombo.remove_all()
        # Add the names of the profiles
        for p in self.conf.profiles:
            profilesCombo.append_text(p.name)
        # Select the right profile
        if profileNumber == None:
            profileNumber = self.conf.activeprofile
        profilesCombo.set_active(profileNumber)

    def loadConfig(self):
        self.conf = Config()
        self.populate_profiles_combobox()

    def saveConfig(self):
        self.conf.activeprofile = self.o("profiles_combo").get_active()
        # Save the settings to the configuration file
        self.conf.write()


if __name__ == "__main__":
    pass
