nfc-playlist
============

Install::

    git clone https://github.com/wingesas/nfc-playlist.git
    cd nfc-playlist
    pip install .

    cp nfc-playlist/{nfcPlaylist.py,data.json} /usr/local/bin
    chmod 755 /usr/local/bin/nfcPlaylist.py

    cp nfcPlaylist.sh /etc/init.d
    chmod 755 /etc/init.d/nfcPlaylist.sh

    update-rc.d nfcPlaylist.sh defaults

    /etc/init.d/nfcPlaylist.sh start

    tail -f /tmp/nfcPlaylist.log
