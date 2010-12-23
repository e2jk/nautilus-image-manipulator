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

import os, gettext, gobject, zipfile, subprocess
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
        self.newFiles = []
        for f in self.origFiles:
            (skip, cancel, newFileName) = self.resize_one_image(f)
            if cancel:
                break
            if not skip:
                self.newFiles.append(newFileName)
            i += 1
            percent = i / self.numFiles
            self.resizeDialog.builder.get_object("progress_progressbar").set_text("%s %d%%" % (_("Resizing images..."), int(percent * 100)))
            self.resizeDialog.builder.get_object("progress_progressbar").set_fraction(percent)
            # There's more work, return True
            yield True
        # Signal we are done resizing
        self.emit("resizing_done")
        # No more work, return False
        yield False

    def resize_one_image(self, fileName):
        """Performs the resizing operation on one image.
        
        The return value indicates if this resizing operation was successful.
        """
        skip = False
        cancel = False
        
        (basePath, name) = os.path.split(fileName)
        
        if self.subdirectoryName:
            basePath = "%s/%s" % (basePath, self.subdirectoryName)
        
        if self.appendString:
            # TODO: If the appendString ends in "/", the images will be called ".jpg" which is a
            # hidden file in it's own new folder (folder name == the image name).
            # What should we do about it?
            # Insert the append string and convert the extension to lower case
            n = os.path.splitext(name)
            name = "%s%s%s" % (n[0], self.appendString, n[1].lower())
        
        # This is the output filename
        newFileName = "%s/%s" % (basePath, name)
        
        # Make sure the directory exists
        # Note: a new subdirectorie will also need to be created if a / was entered in the appendString
        try: os.makedirs("/".join(newFileName.split("/")[:-1]))
        except: pass
        
        # Resize the image using ImageMagick
        args = ["/usr/bin/convert", fileName, "-resize", self.geometry, newFileName]
        retVal = subprocess.call(args)
        if retVal != 0:
            # TODO: Write error value to log?
            print "Error while executing resize command:", retVal
            (skip, cancel, retry) = self.resizeDialog.error_resizing(fileName)
            if retry:
                # Retry with the same image
                (skip, cancel, newFileName) = self.resize_one_image(fileName)
        return (skip, cancel, newFileName)

    def pack_images(self):
        """Creates a zip file containing the modified files"""
        # Generate the name of the zipfile
        dirname = os.path.dirname(self.origFiles[0])
        zipname = "images" # Default filename
        if self.subdirectoryName:
            zipname = self.subdirectoryName
        if self.appendString:
            zipname = self.appendString
        self.zipfile = "%s/%s.zip" % (dirname, zipname)
        
        # Zip the files into a PKZIP format .zip file
        zout = zipfile.ZipFile(self.zipfile, "w")
        i = float(0)
        for fname in self.newFiles:
            # TODO: make sure the name of the images are unique (could not be true if using appendString)
            zout.write(fname, os.path.basename(fname), zipfile.ZIP_DEFLATED)
            i += 1
            percent = i / self.numFiles
            self.resizeDialog.builder.get_object("progress_progressbar").set_text("%s %d%%" % (_("Packing images..."), int(percent * 100)))
            self.resizeDialog.builder.get_object("progress_progressbar").set_fraction(percent)
            # There's more work, return True
            yield True
        zout.close() # Close the zip file
        
        # TODO: check with zipfile.is_zipfile(self.zipfile) and ZipFile.testzip() if the generated zipfile is valid
        
        # Signal we are done packing
        self.emit("packing_done", self.zipfile)
        # No more work, return False
        yield False
        

gobject.type_register(ImageManipulations)
gobject.signal_new("resizing_done", ImageManipulations, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())
gobject.signal_new("packing_done", ImageManipulations, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, ))

if __name__ == "__main__":
    pass
