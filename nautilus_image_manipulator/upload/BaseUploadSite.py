#!/usr/bin/python
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
from gi.repository import GObject

class UnknownUploadDestinationException(Exception):
       """Impossible to determine the upload destination for this website,
       the upload website has most likely changed it's API/website"""
       pass

class InvalidEndURLsException(Exception):
       """Impossible to determine the URLs where the file will be made
       available."""
       pass

class FinalURLsNotFoundException(Exception):
       """The upload was successful, but the file can't be downloaded.
       Probably due to verification on the external side not being successful."""
       pass

class BaseUploadSite(GObject.GObject):
    def __init__(self):
        super(BaseUploadSite, self).__init__()

    def upload(self, filename, callback):
        """Uploads a single file and saves the links to download and delete that file.
        
        ``filename`` is the file to upload
        ``callback`` is the function that updates the progress bar while uploading"""
        pass

if __name__ == "__main__":
    pass

