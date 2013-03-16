#!/usr/bin/python
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

import glob
import subprocess
import os

def main():
    uiFolder = "./data/ui"

    #TODO: better not use the "/usr/bin/" part of the command
    cmd = "/usr/bin/glade"
    if not os.path.exists(cmd):
        print "ERROR: Please check your Glade installation."
        exit(-1)


    # Check if the folder exists, i.e. uiFolder is a valid folder
    if not os.path.isdir(uiFolder):
        # The folder does not exist, we are probably not running the script from the root of the repository
        # Exit with an error message
        print "ERROR: Please run this script from the root of the repository."
        exit(-1)

    # List all ".ui" files in uiFolder
    files = []
    for ui_file in glob.glob(uiFolder + "/*.ui"):
        files.append(ui_file)

    # Prepare the command to be run to launch Glade
    cmd = "GLADE_CATALOG_SEARCH_PATH=%s %s %s" % (uiFolder, cmd, " ".join(files))

    # Run Glade
    subprocess.Popen(cmd, shell=True)

if __name__ == '__main__':
    main()
