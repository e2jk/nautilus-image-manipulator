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

import os
import ConfigParser
import logging
from copy import copy, deepcopy

import gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class Config:
    size = {"small": (640, 640),
            "large": (1280, 1280)}
    actualversion = 2
    def __init__(self, configFile="~/.config/nautilus-image-manipulator/config"):
        self.file = os.path.expanduser(configFile)
        self.profiles = []
        if not os.path.isfile(self.file) or not self.read():
            # There is no config file, or the config file was not valid
            oldconfigfile = os.path.expanduser("~/.nautilus-image-manipulator.ini")
            if os.path.isfile(oldconfigfile):
                # With the new UI (profiles-based) the old config file is
                # now useless.
                os.remove(oldconfigfile)
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
                    zipname="%s.zip" % _("resized"),
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
                    zipname="%s.zip" % _("resized"),
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
        """Add a new profile to the list of profiles.
        If the profile already exists, return the existing one instead.
        If it really is a new profile, add it at position last-1 (last is
        always custom settings)"""
        # Remove the name from the profile, to compare profiles nameless
        name = newprofile.__dict__.pop("name")
        # Create a deep copy of the list of profiles, so that deleting the
        # name to compare profiles doesn't affect the real profiles
        tempprofiles = deepcopy(self.profiles[:-1])
        isNewProfile = True
        profileNumber = 0
        # Check if there is an exact match (ignore name differences)
        for p in tempprofiles:
            del p.__dict__["name"]
            if newprofile == p:
                isNewProfile = False
                break
            profileNumber += 1
        if isNewProfile:
            # Put the name back to the new profile
            newprofile.name = name
            # Add the new profile to the profiles list
            self.profiles.insert(len(self.profiles) - 1, newprofile)
            # Make sure that there are no conflicting profile names
            self.handleConflictingNames()
        logging.debug("%s profile, position %d" % (
                "New" if isNewProfile else "Existing", profileNumber))
        return profileNumber

    def handleConflictingNames(self):
        """Make sure that there are no profiles that have the same name"""
        # profilesMatrix will contain for each profile whether its default
        # name needs to be changed
        profilesMatrix = []
        for p in self.profiles[:-1]:
            profilesMatrix.append({"addQuality": False, "addPixels": False})
        tempprofiles = deepcopy(self.profiles[:-1])
        i = 0
        for p in self.profiles[:-2]:
            # Check the profiles one by one to see if their default name
            # would be the same 
            addQuality = False
            addPixels = False
            changeNameOfProfiles = []
            j = 0
            # Don't compare the profile to itself
            tempprofiles.pop(0)
            defaultProfileName = p.createname()
            for t in tempprofiles:
                # Check the current profile with all the profiles that follow it
                if defaultProfileName == t.createname():
                    # They would have received the same default name
                    if t.quality != p.quality:
                        # They have different qualities, add that
                        # information to their name
                        profilesMatrix[i]["addQuality"] = True
                        profilesMatrix[i + j + 1]["addQuality"] = True
                    else:
                        # They have the same quality, so the difference has
                        # to be the size. Add that information (in pixels)
                        # to their name
                        profilesMatrix[i]["addPixels"] = True
                        profilesMatrix[i + j + 1]["addPixels"] = True
                j += 1
            i += 1

        # The list of profiles that need their name changed has been created
        i = 0
        logging.debug("Outcome of handleConflictingNames:")
        for p in profilesMatrix:
            if p["addQuality"] or p["addPixels"]:
                # This profile needs its name changed
                self.profiles[i].createname(True, p["addQuality"], p["addPixels"])
            logging.debug("%d: %s  => %s" % (i, p, self.profiles[i].name))
            i += 1

    def deleteprofile(self, id):
        """Deletes a profile from the list of profiles"""
        if len(self.profiles) - 1 == id:
            # It's not possible to delete the last profile (custom settings)
            logging.debug("Not allowed to remove last profile %d, it's custom settings" % id)
            return False
        self.profiles.pop(id)
        logging.debug("Removed profile %d" % id)
        return True

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

        # Check if the saved profile's version is different than the current version
        profileversion = self.readvalue(c, "General", "profile version", "int")
        if profileversion != self.actualversion:
            # There will [probably] be some conversion to do to convert the
            # old settings to the newer.
            pass

        for section in sections[1:]:
            name = self.readvalue(c, section, "name")
            size = self.readvalue(c, section, "size")
            width = self.readvalue(c, section, "width", "float")
            height = self.readvalue(c, section, "height", "float")
            percent = self.readvalue(c, section, "percent", "float")
            quality = self.readvalue(c, section, "quality", "float", 95)
            destination = self.readvalue(c, section, "destination")
            appendstring = self.readvalue(c, section, "appendstring")
            foldername = self.readvalue(c, section, "foldername")
            zipname = self.readvalue(c, section, "zipname")
            url = self.readvalue(c, section, "url")
            p = Profile(size, width, height, percent, quality, destination,
                        appendstring, foldername, zipname, url, name)
            self.profiles.append(p)
        return True

    def write(self):
        logging.info("Saving configuration to %s" % self.file)

        # Create a new ConfigParser object, to make sure we only have the
        # latest parameters
        config = ConfigParser.ConfigParser()
        config.add_section("General")
        config.set("General", "profile version", self.actualversion)
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
            if p.zipname:
                config.set(section, "zipname", p.zipname)
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
                 foldername=None, zipname=None, url=None, name=None):
        self.size = size
        if self.size in ("small", "large"):
            (self.width, self.height) = Config.size[self.size]
        else:
            # Check if the custom sizes are the same as small or large
            for s in ("small", "large"):
                if (width, height) == Config.size[s]:
                    self.size = s
            self.width = width
            self.height = height
        if self.width and self.height:
            self.aspectratio = float(self.width) / float(self.height)
        self.percent = percent
        self.quality = quality
        self.destination = destination
        self.appendstring = appendstring
        self.foldername = foldername
        self.zipname = zipname
        if self.zipname:
            # Sanitize the name of the zipfile
            self.zipname = self.zipname.strip() # Strip whitespace
            # Remove starting non-alphabetic characters
            i = 0
            for c in self.zipname:
                if c.isalpha():
                    break
                i += 1
            self.zipname = "%s" % self.zipname[i:]
            # Make sure the zipfile's name ends in ".zip"
            if not self.zipname.endswith(".zip"):
                self.zipname += ".zip"
        self.url = url

        self.name = name if name else self.createname()

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
        elif self.destination == 'folder':
            p += "- Place the resized images in the \"%s\" folder" % self.foldername
        elif self.destination == 'upload':
            p += "- Zip the resized images in \"%s\"\n" % self.zipname
            p += "- Upload the resized images to \"%s\"" % self.url
        return p

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def createname(self, setSelf=False, addQuality=False, addPixels=False):
        """Create a profile name based on its attributes"""
        # Determine the images' size
        if self.size == "small":
            # Part of new profile name "Create small images[...]"
            imageSize = _("small")
        elif self.size == "large":
            # Part of new profile name "Create large images[...]"
            imageSize = _("large")
        elif self.percent:
            # Part of new profile name "Create 60% resized images[...]"
            imageSize = _("%d%% resized") % self.percent
        elif self.width and self.height:
            areaProfile = int(self.width) * int(self.height)
            areaSmall = Config.size["small"][0] * Config.size["small"][1]
            areaLarge = Config.size["large"][0] * Config.size["large"][1]
            if areaProfile < 0.8 * areaSmall:
                # Part of new profile name "Create very small images[...]"
                imageSize = _("very small")
            elif (areaProfile >= 0.8 * areaSmall) and \
                 (areaProfile < 1.2 * areaSmall):
                # Part of new profile name "Create small images[...]"
                imageSize = _("small")
            elif (areaProfile >= 1.2 * areaSmall) and \
                 (areaProfile < 0.8 * areaLarge):
                # Part of new profile name "Create medium images[...]"
                imageSize = _("medium")
            elif (areaProfile >= 0.8 * areaLarge) and \
                 (areaProfile < 1.2 * areaLarge):
                # Part of new profile name "Create large images[...]"
                imageSize = _("large")
            elif (areaProfile >= 1.2 * areaLarge):
                # Part of new profile name "Create very large images[...]"
                imageSize = _("very large")

        if addPixels:
            # Add the actual size information in the profile name
            imageSize += " (%dx%d)" % (self.width, self.height)

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
        if addQuality:
            # Add the quality information in the profile name
            n += " " + _("(%d%% quality)") % self.quality
        n = n if n else _("Unnamed profile")
        if setSelf:
            self.name = n
        else:
            return n
