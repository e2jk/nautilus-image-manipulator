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

import os
import ConfigParser
import logging
from copy import copy

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class Config:
    size = {"small": (640, 640),
            "large": (1280, 1280)}
    def __init__(self):
        self.file = os.path.expanduser("~/.config/nautilus-image-manipulator/config")
        self.config = ConfigParser.ConfigParser()
        self.profiles = []
        if not os.path.isfile(self.file):
            # There is no config file
            if not os.path.exists(os.path.dirname(self.file)):
                # Create the folder to contain the new config file
                os.makedirs(os.path.dirname(self.file))
            # Create a default configuration
            logging.info("Create a default configuration")
            self.defaultvalues()
        else:
            # Read the settings from the config file
            self.config.read(self.file)
        self.activeprofile = self.readvalue("Saved state","activeprofile",0,"int")
        logging.info("There are %d profiles" % len(self.profiles))
        for p in self.profiles:
            logging.debug("%s\n%s" % ("="*64, p))

    def defaultvalues(self):
        """Determines the default profiles"""
        defaultUploadUrl = "1fichier.com"
        # Make small images and upload them to 1fichier.com
        self.profiles.append(
            Profile(None,
                    name=_("Send %(imageSize)s images to %(uploadUrl)s") % {
                                  "imageSize": _("small"),
                                  "uploadUrl": defaultUploadUrl},
                    size="small",
                    quality=90,
                    destination="upload",
                    foldername=_("resized"),
                    url=defaultUploadUrl)
        )
        
        # Make small images and do not upload them
        self.profiles.append(
            Profile(None,
                    name=_("Create %(imageSize)s images in the \"%(directoryName)s\" folder") % {
                                  "imageSize": _("small"),
                                  "directoryName": _("resized")},
                    size="small",
                    quality=90,
                    destination="folder",
                    foldername=_("resized"))
        )
        
        # Make large images and upload them to 1fichier.com
        self.profiles.append(
            Profile(None,
                    name=_("Send %(imageSize)s images to %(uploadUrl)s") % {
                                  "imageSize": _("large"),
                                  "uploadUrl": defaultUploadUrl},
                    size="large",
                    destination="upload",
                    foldername=_("resized"),
                    url=defaultUploadUrl)
        )
        
        # Make large images and do not upload them
        self.profiles.append(
            Profile(None,
                    name=_("Create %(imageSize)s images in the \"%(directoryName)s\" folder") % {
                                  "imageSize": _("large"),
                                  "directoryName": _("resized")},
                    size="large",
                    destination="folder",
                    foldername=_("resized"))
        )
        
        # Default custom profile is basically the same as the first one
        customprofile = copy(self.profiles[0])
        customprofile.name = _("Custom settings")
        self.profiles.append(customprofile)

    def writeprofile(self, profile):
        p = profile
        section = "Profile %i" % p.id
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, "name", p.name)
        self.config.set(section, "id", p.id)
        self.config.set(section, "inpercent", p.inpercent)
        self.config.set(section, "width", p.width)
        self.config.set(section, "percent", p.percent)
        self.config.set(section, "quality", p.quality)
        self.config.set(section, "destination", p.destination)
        self.config.set(section, "appendstring", p.appendstring)
        self.config.set(section, "foldername", p.foldername)
        self.config.set(section, "url", p.url)
        self.write()

    def addprofile(self, newprofile):
        # Add the new profile at position last-1 (last is always custom settings)
        self.profiles.insert(len(self.profiles)-1, newprofile)

    def deleteprofile(self, id):
        self.profiles.pop(id)

    def writestate(self, activeprofile):
        p = activeprofile
        section = "Saved state"
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, "activeprofile", p)
        self.write()

    def write(self):
        f = open(self.file, "w")
        self.config.write(f)
        f.close()

    def readvalue(self, section, name, value=None, type=None):
        try:
            if type == "int":
                value = self.config.getint(section, name)
            elif type == "bool":
                value = self.config.getboolean(section, name)
            else:
                value = self.config.get(section, name)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            pass
        return value


class Profile:
    def __init__(self, builder, name=None, size=None, width=None, height=None,
                 percent=None, quality=95, destination=None, appendstring=None,
                 foldername=None, url=None):
        self.builder = builder
        self.name = name
        self.size = size
        if self.size in ("small", "large"):
            (self.width, self.height) = Config.size[self.size]
        else:
            self.width = width
            self.height = height
        if self.width and self.height:
            self.aspectratio = float(self.width)/float(self.height)
        self.percent = percent
        self.quality = quality
        self.destination = destination
        self.appendstring = appendstring
        self.foldername = foldername
        self.url = url
        
        if not self.name:
            #TODO: Create a name based on the profile parameters
            self.name = "Unnamed profile"

    def __str__(self):
        """Returns a string representation of a Profile
        
        Useful for debugging or logging"""
        p = ""
        if self.name == _("Custom settings"):
            p += "%s:\n" % self.name
        else:
            p += "Profile \"%s\":\n" % self.name
        if self.percent:
            p += "- Resize images by %d%%" % self.percent
        elif self.width:
            s = "Width: %dpx Height: %dpx" % (self.width, self.height)
            if self.size:
                p += "- %s images (%s)" % (self.size.capitalize(), s)
            else:
                p += "- Custom size: %s" % s
        p += "\n- Quality: %d%%\n" % self.quality
        if self.destination == 'append':
            p += "- Append \"%s\" to the file names" % self.appendstring
        elif self.destination in ('folder', 'upload'):
            p += "- Place the resized images in the \"%s\" folder" % self.foldername
            if self.destination == 'upload':
                p += "\n- Upload the resized images to \"%s\"" % self.url
        return p

    def create(self):
        """ Create a new gtktree iter with the current profile set """
        # At first load settings from the ui
        #self.loadfromui()
        # load the gtktree model
        model = self.builder.get_object("profiles_combo").get_model()
        # Find unused id
        find = False
        # id < 10 are reserved for default profiles
        self.id = 10
        while self.id < 30:
            iter = model.get_iter_first()
            while iter is not None:
                if model.get_value(iter, 1) == self.id:
                    find = True
                    break
                iter = model.iter_next(iter)
            if find == False:
                break
            find = False
            self.id = self.id + 1
        # Make the profile name reflect on the settings
        if self.percent:
            self.name = "%s %% scaled" % self.percent
        elif self.width == 640:
            self.name = "Small"
        elif self.width == 1024:
            self.name = "Normal"
        elif self.width == 1280:
            self.name = "Large"
        else:
            self.name = "%s pixels" % int(self.width)
        self.name = "%s images" % self.name
        if self.destination == 'folder':
            self.name = "%s in a folder" % self.name
        elif self.destination == 'upload':
            self.name = "%s send to %s" % (self.name, self.url)
        # Put the profile settings in a new gtktree item
        iter = self.uiaddprofile()
        # Select the profile in the ui
        Config().writeprofile(self)
        self.builder.get_object("profiles_combo").set_active_iter(iter)

    def delete(self):
        """ Delete a profile in gtktree and in config file """
        model = self.builder.get_object("profiles_combo").get_model()
        iter = self.builder.get_object("profiles_combo").get_active_iter()
        id = model.get_value(iter, 1)
        first = model.get_iter_first()
        self.builder.get_object("profiles_combo").set_active_iter(first)
        model.remove(iter)
        Config().deleteprofile(id)

    def uiaddprofile(self):
        """ Put the profile settings in a new gtktree item """
        model = self.builder.get_object("profiles_combo").get_model()
        iter = model.append(None)
        model.set_value(iter, 0, self.name)
        model.set_value(iter, 1, self.id)
        model.set_value(iter, 2, False)
        #model.set_value(iter, 3, self.inpercent)
        model.set_value(iter, 4, self.width)
        model.set_value(iter, 5, self.percent)
        model.set_value(iter, 6, self.quality)
        model.set_value(iter, 7, self.destination)
        model.set_value(iter, 8, self.appendstring)
        model.set_value(iter, 9, self.foldername)
        model.set_value(iter, 10, self.url)
        return iter
