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

import os, gettext
from gettext import gettext as _
gettext.textdomain('nautilus-image-manipulator')

def resize_images(files, geometry, subdirectoryName, appendString):
    """Loops over all files to resize them."""
    
    # Clean the subdirectory name input
    if subdirectoryName:
        # Remove eventual slashes at the beginning or end of the subdirectory name
        cleanSubdirectoryName = []
        for i in subdirectoryName.split("/"):
            if i:
                cleanSubdirectoryName.append(i)
        subdirectoryName = "/".join(cleanSubdirectoryName)
    
    for f in files:
        retVal = resize_one_image(f, geometry, subdirectoryName, appendString)

def resize_one_image(fileName, geometry, subdirectoryName, appendString):
    """Performs the resizing operation on one image.
    
    The return value indicates if this resizing operation was successful.
    """
    s = fileName.split("/")
    basePath = "/".join(s[:-1])
    name = s[-1]
    
    if subdirectoryName:
        basePath = "%s/%s" % (basePath, subdirectoryName)
    
    if appendString:
        # TODO: If the appendString ends in "/", the images will be called ".jpg" which is a
        # hidden file in it's own new folder (folder name == the image name).
        # What should we do about it?
        n = name.split(".")
        extension = n[-1].lower() # Also convert the extension to lower case
        name = "%s%s.%s" % (".".join(n[:-1]), appendString, extension)
    
    # This is the output filename
    newFileName = "%s/%s" % (basePath, name)
    
    # Make sure the directory exists
    # Note: a new subdirectorie will also need to be created if a / was entered in the appendString
    try: os.makedirs("/".join(newFileName.split("/")[:-1]))
    except: pass
    
    # Resize the image using ImageMagick
    cmd = "/usr/bin/convert %(fileName)s -resize %(geometry)s %(newFileName)s" % {"fileName": fileName, "geometry": geometry, "newFileName": newFileName}
    retVal = 0
    retVal = os.system(cmd)
    if retVal != 0:
        # TODO: Better handling of this error (write to log?)
        print "Error while executing resize command:", retVal
    return retVal

if __name__ == "__main__":
    pass
