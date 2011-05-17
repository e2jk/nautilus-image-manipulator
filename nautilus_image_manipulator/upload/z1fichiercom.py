#!/usr/bin/python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2010-2011 Emilien Klein <emilien _AT_ klein _DOT_ st>
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

import urllib2, re
from nautilus_image_manipulator.upload.poster.encode import multipart_encode
from nautilus_image_manipulator.upload.poster.streaminghttp import register_openers

class UploadSite():
    def __init__(self):
        """Determines the url to upload to for 1fichier.com.
        
        Documentation for 1fichier.com: http://www.1fichier.com/api/web.html
        Note: it's not up to date..."""
        # The session ID is read from the "files" form on http://www.1fichier.com
        html = urllib2.urlopen('http://www.1fichier.com').read()
        (sessionId) = re.search('<form enctype="multipart/form-data" id="files" action="http://upload\.1fichier\.com/upload.cgi\?id=(.*)" method="post">', html).groups()
        # Build the url to upload to and to retrieve the download and delete links:
        self.uploadUrl = "http://upload.1fichier.com/upload.cgi?id=%s" % sessionId
        self.endUploadUrl = "http://upload.1fichier.com/end.pl?xid=%s" % sessionId
    
    def upload(self, filename, callback):
        """Uploads a single file and saves the links to download and delete that file.
        
        ``filename`` is the file to upload
        ``callback`` is the function that updates the progress bar while uploading"""
        print "Uploading %s to %s" % (filename, self.uploadUrl)
        print "End upload url: %s" % self.endUploadUrl
        
        # Register the streaming http handlers with urllib2
        register_openers()

        # Start the multipart/form-data encoding of the file "filename"
        # headers contains the necessary Content-Type and Content-Length
        # datagen is a generator object that yields the encoded parameters
        datagen, headers = multipart_encode( [ ("file[]", open(filename, "rb")), ('domain', '0') ], cb = callback )
        
        # There is a bug in poster 0.7.0 that encodes parameter names. It will be fixed in the next release.

        request = urllib2.Request(self.uploadUrl, datagen, headers)
        urllib2.urlopen(request)
        
        # Retrieve the download page
        request = urllib2.Request(self.endUploadUrl)
        request.add_header("EXPORT", 1) # To get simplified values in the format explained below
        downloaded_page = urllib2.urlopen(request).read()
        
        # The return is like this:
        # filename;size;download identifier;deletion identifier;domain identifier;control hash
        
        try:
            (filename, size, download_id, deletion_id, domain_id, control_hash) = re.search("(.*);(.*);(.*);(.*);(.*);(.*)", downloaded_page).groups()
        except:
            # TODO: Better failed upload handling
            print 'The upload has failed, this is the returned page:\n"%s"\n' % downloaded_page
            raise
        
        downloadPage = "http://%s.1fichier.com" % download_id
        deletePage = "http://www.1fichier.com/remove/%s/%s" % (download_id, deletion_id)
        
        return (downloadPage, deletePage)
        
if __name__ == "__main__":
    pass

