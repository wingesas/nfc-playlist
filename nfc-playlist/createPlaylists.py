#!/usr/bin/env python

import os
import fnmatch
from mutagen.easyid3 import EasyID3

# create playlists
mediaDir = '/var/lib/mopidy/media/mp3'
playlistsDir = '/var/lib/mopidy/playlists'

os.system("rm " + playlistsDir + "/*.m3u")
os.system("echo '/var/lib/mopidy/media/beep.mp3' > beep.m3u")
os.system("echo '/var/lib/mopidy/media/beepDouble.mp3' > beepDouble.m3u")

for root, dirs, files in os.walk(mediaDir):
    # magic marker in directory?
    if len(fnmatch.filter(files, 'magic.marker')) > 0:
        # grep all mp3 files
        matches = fnmatch.filter(files, '*.mp3')
        if len(matches) > 0:
            audio = EasyID3(os.path.join(root, matches[0]))
            with open(os.path.join(playlistsDir, audio['artist'][0] + ' - ' + audio['album'][0] + '.m3u'), 'wb') as m3u:
                for match in sorted(matches):
                    m3u.write(os.path.join(root, match) + '\n')

os.system("chown mopidy:audio " + playlistsDir + "/*.m3u")
