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

import os, gettext, gobject
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class ImageManipulations(gobject.GObject):
    def __init__(self, dialog, files, geometry, subdirectoryName, appendString):
        self.__gobject_init__()
        self.resizeDialog = dialog
        self.origFiles = files
        self.numFiles = len(self.origFiles)
        self.geometry = geometry
        self.subdirectoryName = None
        self.appendString = appendString
        
        # Clean the subdirectory name input
        if subdirectoryName:
            # Remove eventual slashes at the beginning or end of the subdirectory name
            cleanSubdirectoryName = []
            for i in subdirectoryName.split("/"):
                if i:
                    cleanSubdirectoryName.append(i)
            self.subdirectoryName = "/".join(cleanSubdirectoryName)

    def resize_images(self):
        """Loops over all files to resize them."""
        i = float(0)
        newFiles = []
        for f in self.origFiles:
            (retVal, newFileName) = self.resize_one_image(f)
            newFiles.append(newFileName)
            # TODO: handle error in resizing image (ask to retry, ignore this image or cancel the whole operation)
            i += 1
            percent = i / self.numFiles
            self.resizeDialog.builder.get_object("progress_progressbar").set_text("%s %d%%" % (_("Resizing images..."), int(percent * 100)))
            self.resizeDialog.builder.get_object("progress_progressbar").set_fraction(percent)
            # There's more work, return True
            yield True
        # 
        # No more work, return False
        yield False

    def resize_one_image(self, fileName):
        """Performs the resizing operation on one image.
        
        The return value indicates if this resizing operation was successful.
        """
        s = fileName.split("/")
        basePath = "/".join(s[:-1])
        name = s[-1]
        
        if self.subdirectoryName:
            basePath = "%s/%s" % (basePath, self.subdirectoryName)
        
        if self.appendString:
            # TODO: If the appendString ends in "/", the images will be called ".jpg" which is a
            # hidden file in it's own new folder (folder name == the image name).
            # What should we do about it?
            n = name.split(".")
            extension = n[-1].lower() # Also convert the extension to lower case
            name = "%s%s.%s" % (".".join(n[:-1]), self.appendString, extension)
        
        # This is the output filename
        newFileName = "%s/%s" % (basePath, name)
        
        # Make sure the directory exists
        # Note: a new subdirectorie will also need to be created if a / was entered in the appendString
        try: os.makedirs("/".join(newFileName.split("/")[:-1]))
        except: pass
        
        # Resize the image using ImageMagick
        cmd = "/usr/bin/convert %(fileName)s -resize %(geometry)s %(newFileName)s" % {"fileName": fileName, "geometry": self.geometry, "newFileName": newFileName}
        retVal = 0
        retVal = os.system(cmd)
        if retVal != 0:
            # TODO: Better handling of this error (write to log?)
            print "Error while executing resize command:", retVal
        return (retVal, newFileName)

if __name__ == "__main__":
    pass
