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
import gettext
from gi.repository import GObject
import zipfile
import subprocess
import Image
import pyexiv2
import logging
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

class ImageManipulations(GObject.GObject):
    def __init__(self, dialog, files, inpercent, width, percent, quality, 
                                    destination, appendstring, foldername):
        super(ImageManipulations, self).__init__()
        self.resizeDialog = dialog
        self.origFiles = files
        self.numFiles = len(self.origFiles)
        self.inpercent = inpercent
        self.width = width
        self.percent = percent
        self.quality = quality
        self.destination = destination
        self.appendstring = appendstring
        self.foldername = foldername
        
        # Clean the subdirectory name input
        if foldername:
            # Remove eventual slashes at the beginning or end of the subdirectory name
            cleanfoldername = []
            for i in foldername.split("/"):
                if i:
                    cleanfoldername.append(i)
            self.foldername = "/".join(cleanfoldername)
        
        logging.debug('files: %s' % self.origFiles)
        logging.debug('inpercent: %s' % self.inpercent)
        logging.debug('width: %s' % self.width)
        logging.debug('percent: %s' % self.percent)
        logging.debug('quality: %s' % self.quality)
        logging.debug('destination: %s' % self.quality)
        logging.debug('appendstring: %s' % self.appendstring)
        logging.debug('foldername: %s' % self.foldername)

    def resize_images(self):
        """Loops over all files to resize them."""
        if self.inpercent and self.percent == "100" and self.quality == "100":
            # If scaling to 100% with a compression of 100%, don't
            # actually resize files (it would just degrade the quality)
            # This configuration might be used if the user just wants to
            # send the zipped files via Internet
            self.newFiles = self.origFiles
        else:
            # Resize and/or compress the images
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
                self.resizeDialog.builder.get_object("progressbar").set_text("%s %d%%" % (_("Resizing images..."), int(percent * 100)))
                self.resizeDialog.builder.get_object("progressbar").set_fraction(percent)
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
        logging.debug('resizing image: %s' % fileName)
        skip = False
        cancel = False
        
        (basePath, name) = os.path.split(fileName)
        
        if self.destination == 'folder':
            basePath = "%s/%s" % (basePath, self.foldername)
        logging.debug('basePath: %s' % basePath)
        logging.debug('name: %s' % name)
        
        if self.destination == 'append':
            # Insert the append string and convert the extension to lower case
            n = os.path.splitext(name)
            name = "%s%s%s" % (n[0], self.appendstring, n[1].lower())
        
        # This is the output filename
        newFileName = "%s/%s.%s" % (basePath, os.path.splitext(name)[0], "jpg")
        logging.debug('newFileName: %s' % newFileName)
        
        # Make sure the directory exists
        # Note: a new subdirectory will also need to be created if a / was
        # entered in the appendString
        try: os.makedirs("/".join(newFileName.split("/")[:-1]))
        except: pass
        
        # Open image with PIL
        im = Image.open(fileName)
        # Get original geometry
        (w, h) = im.size
        logging.debug('Original image size %sx%s' % (w, h))
        if self.inpercent:
            # New geometry is a %
            factor = int(self.percent) / 100.0
            width = int(w*factor)
            height = int(h*factor)
        else:
            # New geometry is in pixels and aspect ratio is respected
            if (h > w):
                # Image is vertical
                height = self.width
                factor = int(height) / float(h)
                width = int(w * factor)
            else:
                width = self.width
                factor = int(self.width) / float(w)
                height = int(h * factor)
           
        logging.debug('New image size %sx%s' % (width, height))
        # Resize and save image
        im = im.resize((int(width),int(height)))
        retry = False
        try:
            im.save(newFileName, "JPEG", quality=int(self.quality))
        except IOError as (errno, strerror):
            logging.error("I/O error({0}): {1}".format(errno, strerror))
            (skip, cancel, retry) = self.resizeDialog.error_resizing(fileName)
        if retry:
            # Retry with the same image
            (skip, cancel, newFileName) = self.resize_one_image(fileName)

        if not (skip or retry or cancel):
            # Load EXIF data
            exif = pyexiv2.ImageMetadata(fileName)
            exif.read()
            # Change EXIF image size to the new size
            exif["Exif.Photo.PixelXDimension"] = int(width)
            exif["Exif.Photo.PixelYDimension"] = int(height)
            # Copy the EXIF data to the new image
            newExif = pyexiv2.ImageMetadata(newFileName)
            newExif.read()
            exif.copy(newExif)
            newExif.write()
        return (skip, cancel, newFileName)

    def pack_images(self):
        """Creates a zip file containing the modified files"""
        # Generate the name of the zipfile
        dirname = os.path.dirname(self.origFiles[0])
        if not dirname:
            # Put the zipfile in the user's home folder if no base directory name could be determined.
            dirname = os.path.expanduser("~")
        zipname = "images" # Default filename
        if self.subdirectoryName:
            zipname = self.subdirectoryName
        if self.appendString:
            zipname = self.appendString
        # Sanitize the name of the zipfile
        zipname = zipname.strip() # Strip whitespace
        # Remove starting non-alphabetic characters
        i = 0
        for c in zipname:
            if c.isalpha():
                break
            i += 1
        zipname = "%s.zip" % zipname[i:]
        
        # Make sure the zipfile will not be created in a subdirectory
        # If that would have been the case, make sure we zip the files
        # using the name relative to where the zipfile is made, so that the
        # zipped files' names do not conflict (test with this string to
        # append: `-resized/yy.jpg`)
        useRelName = False
        temp = os.path.basename(zipname)
        if temp != zipname:
            zipname = temp
            useRelName = True
        
        # Create the final zip file name
        self.zipfile = os.path.join(dirname, zipname)
        
        # Zip the files into a PKZIP format .zip file
        zout = zipfile.ZipFile(self.zipfile, "w")
        i = float(0)
        for fname in self.newFiles:
            if useRelName:
                # This is the filename relative to where the zipfile is created. 
                fzname = os.path.relpath(fname, dirname)
            else:
                fzname = os.path.basename(fname)
            #TODO: Check what to do with non-ASCII filenames
            zout.write(fname, fzname, zipfile.ZIP_DEFLATED)
            i += 1
            percent = i / self.numFiles
            self.resizeDialog.builder.get_object("progressbar").set_text("%s %d%%" % (_("Packing images..."), int(percent * 100)))
            self.resizeDialog.builder.get_object("progressbar").set_fraction(percent)
            # There's more work, return True
            yield True
        zout.close() # Close the zip file
        
        # TODO: check with zipfile.is_zipfile(self.zipfile) and ZipFile.testzip() if the generated zipfile is valid
        
        # Signal we are done packing
        self.emit("packing_done", self.zipfile)
        # No more work, return False
        yield False
        

GObject.type_register(ImageManipulations)
GObject.signal_new("resizing_done", ImageManipulations, GObject.SignalFlags.RUN_FIRST, None, ())
GObject.signal_new("packing_done", ImageManipulations, GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_STRING, ))

if __name__ == "__main__":
    pass
