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
        self.profiles = []
        if not os.path.isfile(self.file) or not self.read():
            # There is no config file, or the config file was not valid
            if not os.path.exists(os.path.dirname(self.file)):
                # Create the folder to contain the new config file
                os.makedirs(os.path.dirname(self.file))
            # Create a default configuration
            logging.info("Create a default configuration")
            self.defaultprofiles()
            self.activeprofile = 0
        logging.info("There are %d profiles" % len(self.profiles))
        for p in self.profiles:
            logging.debug("%s\n%s" % ("="*64, p))

    def defaultprofiles(self):
        """Determines the default profiles"""
        defaultUploadUrl = "1fichier.com"
        # Make small images and upload them to 1fichier.com
        self.profiles.append(
            Profile(name=_("Send %(imageSize)s images to %(uploadUrl)s") % {
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
            Profile(name=_("Create %(imageSize)s images in the \"%(directoryName)s\" folder") % {
                                  "imageSize": _("small"),
                                  "directoryName": _("resized")},
                    size="small",
                    quality=90,
                    destination="folder",
                    foldername=_("resized"))
        )
        
        # Make large images and upload them to 1fichier.com
        self.profiles.append(
            Profile(name=_("Send %(imageSize)s images to %(uploadUrl)s") % {
                                  "imageSize": _("large"),
                                  "uploadUrl": defaultUploadUrl},
                    size="large",
                    destination="upload",
                    foldername=_("resized"),
                    url=defaultUploadUrl)
        )
        
        # Make large images and do not upload them
        self.profiles.append(
            Profile(name=_("Create %(imageSize)s images in the \"%(directoryName)s\" folder") % {
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

    def addprofile(self, newprofile):
        """Add the new profile at position last-1 (last is always custom settings)"""
        self.profiles.insert(len(self.profiles)-1, newprofile)

    def deleteprofile(self, id):
        """Deletes a profile from the list of profiles"""
        self.profiles.pop(id)

    def read(self):
        logging.info("Reading configuration from %s" % self.file)
        c = ConfigParser.ConfigParser()
        c.read(self.file)
        
        sections = c.sections()
        if len(sections) < 2:
            logging.error("There are no profiles defined")
            return False
        if sections[0] != "General":
            logging.error("Invalid first configuration section")
            return False
        
        self.activeprofile = 0
        a = self.readvalue(c, "General", "active profile")
        if a:
            self.activeprofile = int(a.replace("Profile ", ""))
        
        for section in sections[1:]:
            name = self.readvalue(c, section, "name")
            size = self.readvalue(c, section, "size")
            width = self.readvalue(c, section, "width", "int")
            height = self.readvalue(c, section, "height", "int")
            percent = self.readvalue(c, section, "percent", "int")
            quality = self.readvalue(c, section, "quality", "float", 95)
            destination = self.readvalue(c, section, "destination")
            appendstring = self.readvalue(c, section, "appendstring")
            foldername = self.readvalue(c, section, "foldername")
            url = self.readvalue(c, section, "url")
            p = Profile(size, width, height, percent, quality, destination,
                        appendstring, foldername, url, name)
            self.profiles.append(p)
        return True

    def write(self):
        logging.info("Saving configuration to %s" % self.file)
        
        # Create a new ConfigParser object, to make sure we only have the
        # latest parameters
        config = ConfigParser.ConfigParser()
        config.add_section("General")
        config.set("General", "active profile", "Profile %i" % self.activeprofile)
        
        logging.info("There are %d profiles" % len(self.profiles))
        i = 0
        for p in self.profiles:
            section = "Profile %i" % i
            config.add_section(section)
            config.set(section, "name", p.name)
            if p.size:
                config.set(section, "size", p.size)
            if p.width and p.height:
                config.set(section, "width", p.width)
                config.set(section, "height", p.height)
            if p.percent:
                config.set(section, "percent", p.percent)
            config.set(section, "quality", p.quality)
            config.set(section, "destination", p.destination)
            if p.appendstring:
                config.set(section, "appendstring", p.appendstring)
            if p.foldername:
                config.set(section, "foldername", p.foldername)
            if p.url:
                config.set(section, "url", p.url)
            
            logging.debug("%s\n%s" % ("="*64, p))
            i += 1
        
        f = open(self.file, "w")
        config.write(f)
        f.close()

    def readvalue(self, config, section, name, type=None, value=None):
        try:
            if type == "int":
                value = config.getint(section, name)
            elif type == "float":
                value = config.getfloat(section, name)
            elif type == "bool":
                value = config.getboolean(section, name)
            else:
                value = config.get(section, name)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
            pass
        return value


class Profile:
    def __init__(self, size=None, width=None, height=None, percent=None,
                 quality=95, destination=None, appendstring=None,
                 foldername=None, url=None, name=None):
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
        
        self.name = name
        if not self.name:
            # Create a profile name based on its parameters
            # Determine the images' size
            if self.size == "small":
                # Part of "Create small images[...]"
                imageSize = _("small")
            elif self.size == "large":
                # Part of "Create large images[...]"
                imageSize = _("large")
            elif self.percent:
                # Part of "Create 60% resized images[...]"
                imageSize = _("%d%% resized") % self.percent
            elif self.width and self.height:
                areaProfile = int(self.width) * int(self.height)
                areaSmall = Config.size["small"][0] * Config.size["small"][1]
                areaLarge = Config.size["large"][0] * Config.size["large"][1]
                if areaProfile < 0.8 * areaSmall:
                    # Part of "Create very small images[...]"
                    imageSize = _("very small")
                elif (areaProfile >= 0.8 * areaSmall) and \
                     (areaProfile < 1.2 * areaSmall):
                    # Part of "Create small images[...]"
                    imageSize = _("small")
                elif (areaProfile >= 1.2 * areaSmall) and \
                     (areaProfile < 0.8 * areaLarge):
                    # Part of "Create medium images[...]"
                    imageSize = _("medium")
                elif (areaProfile >= 0.8 * areaLarge) and \
                     (areaProfile < 1.2 * areaLarge):
                    # Part of "Create large images[...]"
                    imageSize = _("large")
                elif (areaProfile >= 1.2 * areaLarge):
                    # Part of "Create very large images[...]"
                    imageSize = _("very large")
            
            # Determine the string depending on the destination
            n = None
            if self.destination == "upload":
                n = _("Send %(imageSize)s images to %(uploadUrl)s") % {
                                  "imageSize": imageSize,
                                  "uploadUrl": self.url}
            elif self.destination == "folder":
                n = _("Create %(imageSize)s images in the \"%(directoryName)s\" folder") % {
                                  "imageSize": imageSize,
                                  "directoryName": self.foldername}
            elif self.destination == "append":
                n = _("Create %(imageSize)s images and append \"%(appendString)s\"") % {
                                  "imageSize": imageSize,
                                  "appendString": self.appendstring}
            self.name = n if n else _("Unnamed profile")

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
