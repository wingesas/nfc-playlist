nfc-playlist
============

Install::

    git clone https://github.com/wingesas/nfc-playlist.git
    cd nfc-playlist
    pip install .

    cp nfc-playlist/{nfcPlaylist.py,data.json,gpioButtons.py} /usr/local/bin
    chmod 755 {/usr/local/bin/nfcPlaylist.py,/usr/local/bin/gpioButtons.py}

    cp {nfcPlaylist.sh,gpioButtons.sh} /etc/init.d
    chmod 755 {/etc/init.d/nfcPlaylist.sh,/etc/init.d/gpioButtons.sh}

    update-rc.d nfcPlaylist.sh defaults
    update-rc.d gpioButtons.sh defaults

    /etc/init.d/nfcPlaylist.sh start
    /etc/init.d/gpioButtons.sh start

    tail -f /tmp/nfcPlaylist.log
