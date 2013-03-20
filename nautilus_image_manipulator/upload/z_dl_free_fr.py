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

import os
import urllib2
import HTMLParser
import re
import logging
from gi.repository import GObject

from nautilus_image_manipulator.upload.poster.encode import multipart_encode, MultipartParam
from nautilus_image_manipulator.upload.poster.streaminghttp import register_openers
import BaseUploadSite

class UploadSite(BaseUploadSite.BaseUploadSite):
    def __init__(self):
        """Determines the upload url for dl.free.fr
        
        No real API documentation available, just using the non-JavaScript
        upload form at http://dl.free.fr/index_nojs.pl"""
        super(UploadSite, self).__init__()
        html = urllib2.urlopen('http://dl.free.fr/index_nojs.pl').read()
        try:
            (sessionId) = re.search('<form action="/upload.pl\?(.*)" enctype="multipart/form-data" method="post" style="border: 0">', html).groups()
        except AttributeError:
            # If this exception is raised, fix the previous regex
            raise BaseUploadSite.UnknownUploadDestinationException()
        # Build the url to upload to and to retrieve the download and delete links:
        self.uploadUrl = "http://dl.free.fr/upload.pl?%s" % sessionId
        self.endUploadUrl = None

    def upload(self, filename, callback):
        """Uploads a single file and saves the links to download and delete that file.
        
        ``filename`` is the file to upload
        ``callback`` is the function that updates the progress bar while uploading"""
        self.send(filename, callback)
        GObject.timeout_add(3000, self.waitForValidation)

    def waitForValidation(self):
        """Repeatedly checks the page where the file will be made available,
        waiting for when it is validated (checked for viruses).
        
        Returns the links to download and delete that file."""
        logging.debug('checking if file is ready for download')
        # Retrieve the download page
        request = urllib2.Request(self.endUploadUrl)
        downloaded_page = urllib2.urlopen(request).read()
        # Search for the refresh function that is only present while the
        # file is not yet ready for download
        m = re.search('function refresh\(\) { window.location.reload', downloaded_page)
        if not m:
            # The file is ready for download, let's extract the relevant URLs
            logging.debug('file ready for download')
            try:
                (downloadPage, deletePage) = re.search('Le fichier sera accessible \&agrave; l\'adresse suivante: <a class="underline" href="http://dl.free.fr/(.+)" onclick=.*Vous pouvez supprimer le fichier lorsque vous le d\&eacute;sirez via l\'adresse suivante:  <a class="underline" href="http://dl.free.fr/rm.pl\?(.+)" onclick="', downloaded_page).groups()
            except AttributeError:
                logging.error("could not find the urls. Content of the download page:\n%s" % downloaded_page)
                raise BaseUploadSite.FinalURLsNotFoundException()
            self.downloadPage = "http://dl.free.fr/%s" % downloadPage
            self.deletePage = "http://dl.free.fr/rm.pl?%s" % HTMLParser.HTMLParser().unescape(deletePage)
            logging.info('downloadPage: %s' % self.downloadPage)
            logging.info('deletePage: %s' % self.deletePage)

            # Signal we are done uploading
            self.emit("uploading_done")
            # Do not call this function again
            return False
        # Not yet done, return True to allow the function to be called again
        logging.debug('file not yet ready for download')
        return True

    def send(self, filename, callback):
        """Uploads a single file.
        
        ``filename`` is the file to upload
        ``callback`` is the function that updates the progress bar while uploading"""
        logging.debug('uploading %s to %s' % (filename, self.uploadUrl))
        logging.debug('end upload url: Not known yet')

        # Register the streaming http handlers with urllib2
        register_openers()

        # Start the multipart/form-data encoding of the file "filename"
        # headers contains the necessary Content-Type and Content-Length
        # datagen is a generator object that yields the encoded parameters
        image_param = MultipartParam.from_file("ufile", filename)
        # The filename must not be specially encoded...
        # This is a workaround, should probably be fixed directly in Poster
        image_param.filename = os.path.basename(filename)
        (datagen, headers) = multipart_encode([image_param], cb=callback)

        request = urllib2.Request(self.uploadUrl, datagen, headers)
        f = urllib2.urlopen(request)

        self.endUploadUrl = f.geturl()
        logging.debug('file uploaded')
        logging.debug('end upload url: %s' % self.endUploadUrl)


GObject.type_register(UploadSite)
GObject.signal_new("uploading_done", UploadSite, GObject.SignalFlags.RUN_FIRST, None, ())

if __name__ == "__main__":
    pass

