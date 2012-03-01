# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2012 Emilien Klein <emilien _AT_ klein _DOT_ st>
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
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.builder.connect_signals(self)

        # Load the saved configuration
        self.loadConfig()
        self.processingCanceled = False

    def set_files(self, files):
        self.files = files

    def resize_button_clicked(self, widget, data=None):
        """The user has elected to resize the images

        Called before the dialog returns Gtk.RESONSE_OK from run().
        """
        idSelectedProfile = self.builder.get_object("profiles_combo").get_active()
        self.p = self.conf.profiles[idSelectedProfile]
        logging.info("The following profile has been selected:\n%s" % self.p)
        
        # Check if the mandatory values are filled
        if self.p.destination == 'append':
            if not self.p.appendstring:
                self.error_with_parameters(
                    _("Please enter some text to append to the filename."))
                return
            elif self.p.appendstring[-1] == os.path.sep:
                # If the appendString ends in "/", the image would be
                # called ".EXT", which is a hidden file in it's own folder.
                self.error_with_parameters(
                    _("The string to append cannot end in %s") % os.path.sep)
                return
            # TODO: Check that the value is valid to be appended to the filename
        if self.p.destination == 'upload':
            if not self.p.foldername:
                self.error_with_parameters(
                    _("Please enter the name of the folder."))
                return
        
        if self.p.width:
            # Disable the parameter UI elements and display the progress bar
            self.builder.get_object("details_box").set_sensitive(False)
            self.builder.get_object("resize_button").set_sensitive(False)
            self.builder.get_object("deleteprofile_button").set_visible(False)
            self.builder.get_object("newprofile_button").set_visible(False)
            self.builder.get_object("progressbar").set_text("%s 0%%" % ("Resizing images..."))
            self.builder.get_object("progressbar").show()
            while Gtk.events_pending():
                Gtk.main_iteration() # Used to refresh the UI
            # Resize the images
            im = ImageManipulations(self, self.files, self.p)
            im.connect("resizing_done", self.on_resizing_done)
            task = im.resize_images()
            GObject.idle_add(task.next)
        
        # Remember the settings for next time
        self.saveConfig()

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
        import_string = "from upload.z%s import UploadSite" % \
                self.p.url.replace(".", "").replace("/", "")
        # Make sure the import does not fail
        try:
            exec import_string
        except ImportError:
            if os.path.splitext(fileToUpload)[1] == ".zip":
                extraInfo = _("Your images have not been sent, but have been zipped together into this file:\n%(filename)s" % {"filename": fileToUpload})
            else:
                extraInfo = _("Your image has not been sent, but has successfully been resized.\nYou can find it at %(filename)s" % {"filename": fileToUpload})
            self.display_error(_("The selected upload site %(site_name)s is not valid." % {"site_name": '"%s"' % self.p.url}) + "\n\n" + extraInfo, (_("Please file a bug report on Launchpad"), "https://bugs.launchpad.net/nautilus-image-manipulator"))
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
        
        self.builder.get_object("progressbar").set_text("%s 0%%" % _("Uploading images..."))
        self.builder.get_object("progressbar").set_fraction(0)
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
        self.builder.get_object("details_box").hide()
        self.builder.get_object("progressbar").hide()
        self.builder.get_object("url_box").hide()
        # Display the error message
        self.builder.get_object("error_message_label").set_text(msg)
        self.builder.get_object("error_box").show()
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
            self.builder.get_object("progressbar").set_text("%s %d%%" % (_("Uploading images..."), percent100))
            self.builder.get_object("progressbar").set_fraction(percent)
            while Gtk.events_pending():
                Gtk.main_iteration() # Used to refresh the UI
            self.uploadPercent = percent100

    def on_uploading_done(self, downloadPage, deletePage):
        """Displays the url where the images can be downloaded from, or deleted."""
        self.builder.get_object("details_box").hide()
        self.builder.get_object("progressbar").hide()
        # Update the link buttons with the urls
        self.builder.get_object("download_linkbutton").set_label(downloadPage)
        self.builder.get_object("download_linkbutton").set_uri(downloadPage)
        self.builder.get_object("delete_linkbutton").set_label(deletePage)
        self.builder.get_object("delete_linkbutton").set_uri(deletePage)
        self.builder.get_object("url_box").show()
        # Hide the cancel and resize button, and show the close button
        self.builder.get_object("cancel_button").hide()
        self.builder.get_object("resize_button").hide()
        self.builder.get_object("close_button").show()
        self.resize(1, 1)

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
        idCustomSettings = len(self.conf.profiles)-1
        idSelectedProfile = self.builder.get_object("profiles_combo").get_active()
        customSelected = (idCustomSettings == idSelectedProfile)
        # Only show the advanced parameters when the custom settings is selected
        self.builder.get_object("parameters_box").set_visible(customSelected)
        self.builder.get_object("deleteprofile_button").set_visible(customSelected == False)
        self.builder.get_object("newprofile_button").set_visible(customSelected)

    def ui_update (self, p, data=None):
        # UI UPDATE
        # Delete profile button state
        if p.default:
            self.builder.get_object("deleteprofile_button").set_sensitive(False)
        else:
            self.builder.get_object("deleteprofile_button").set_sensitive(True)
        # Size is in percent
        if p.percent:
            self.builder.get_object("percent_radio").set_active(True)
            self.builder.get_object("percent_scale").set_value(p.percent)
        # Size is in pixels
        else:
            self.builder.get_object("pixels_radio").set_active(True)
            self.builder.get_object("width_spin").set_value(p.width)
        # Quality
        self.builder.get_object("quality_scale").set_value(p.quality)
        # Destination
        dest_model = self.builder.get_object("destination_combo").get_model()
        dest_iter = dest_model.get_iter_first()
        while dest_iter is not None:
            dest = dest_model.get(dest_iter, 1)[0]
            if dest == p.destination:
                self.builder.get_object("destination_combo").set_active_iter(dest_iter)
                break
            dest_iter = dest_model.iter_next(dest_iter)
        if p.appendstring:
            self.builder.get_object("append_entry").set_text(p.appendstring)
        if p.foldername:
            self.builder.get_object("subfolder_entry").set_text(p.foldername)
        url_model = self.builder.get_object("upload_combo").get_model()
        url_iter = url_model.get_iter_first()
        while url_iter is not None:
            url = url_model.get(url_iter, 0)[0]
            if url == p.url:
                self.builder.get_object("upload_combo").set_active_iter(url_iter)
                return True
            url_iter = url_model.iter_next(url_iter)

    def newprofile_button_clicked(self, widget, data=None):
        p = Profile(self.builder)
        p.create()

    def deleteprofile_button_clicked(self, widget, data=None):
        profilesCombo = self.builder.get_object("profiles_combo")
        idSelectedProfile = profilesCombo.get_active()
        # Remove from the list of profiles in self.conf
        self.conf.deleteprofile(idSelectedProfile)
        # Remove from the profiles combobox
        profilesCombo.remove(idSelectedProfile)
        # Determine which profile to select now
        if idSelectedProfile > 0 and (
           idSelectedProfile == len(self.conf.profiles)-1):
            # If the last profile in the list before the custom settings
            # just got deleted, but there are still other profiles in the
            # list, select the new last profile.
            idSelectedProfile -= 1
        profilesCombo.set_active(idSelectedProfile)

    def pixels_radio_toggled(self, widget, data=None):
        if widget.get_active():
            self.builder.get_object("width_spin").set_sensitive(True)
            self.builder.get_object("width_combo").set_sensitive(True)
            self.builder.get_object("percent_box1").set_sensitive(False)

    def percent_radio_toggled(self, widget, data=None):
        if widget.get_active():
            self.builder.get_object("width_spin").set_sensitive(False)
            self.builder.get_object("width_combo").set_sensitive(False)
            self.builder.get_object("percent_box1").set_sensitive(True)

    def width_combo_changed(self, widget, data=None):
        model = widget.get_model()
        iter = widget.get_active_iter()
        choice = model.get_value(iter, 0)
        if not choice == 'custom':
            self.builder.get_object("width_spin").set_value(model.get_value(iter, 1))

    def width_spin_changed(self, widget, data=None):
        spinvalue = int(widget.get_value())
        model = self.builder.get_object("width_combo").get_model()
        iter = model.get_iter_first()
        iteradapt = None
        while iter is not None:
            value = model.get(iter, 1)[0]
            if value == spinvalue:
                iteradapt = iter
                break
            iteradapt = iter
            iter = model.iter_next(iter)
        self.builder.get_object("width_combo").set_active_iter(iteradapt)

    def destination_combo_changed(self, widget, data=None):
        dest_model = widget.get_model()
        dest_iter = widget.get_active_iter()
        dest = dest_model.get_value(dest_iter, 1)
        if dest == 'folder':
            self.builder.get_object("subfolder_box").show()
            self.builder.get_object("append_box").hide()
            self.builder.get_object("upload_box").hide()
        elif dest == 'append':
            self.builder.get_object("subfolder_box").hide()
            self.builder.get_object("append_box").show()
            self.builder.get_object("upload_box").hide()
        elif dest == 'upload':
            self.builder.get_object("subfolder_box").hide()
            self.builder.get_object("append_box").hide()
            self.builder.get_object("upload_box").show()
        else:
            self.builder.get_object("subfolder_box").hide()
            self.builder.get_object("append_box").hide()
            self.builder.get_object("upload_box").hide()

    def upload_combo_changed(self, widget, data=None):
        #TODO: implement this stub
        logging.info('upload_combo_changed not yet implemented')
        pass

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
        buttons =(_("_Skip"), 0,
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

    def loadConfig(self):
        self.conf = Config()
        # Populate the combobox with the names of the profiles
        profilesCombo = self.builder.get_object("profiles_combo")
        for p in self.conf.profiles:
            profilesCombo.append_text(p.name)
        # Set the active profile
        profilesCombo.set_active(self.conf.activeprofile)

    def saveConfig(self):
        self.conf.activeprofile = self.builder.get_object(
                                          "profiles_combo").get_active()
        #TODO: save the config to the configuration file


if __name__ == "__main__":
    pass
