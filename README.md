# Steganography Flask web/app and CLI tool

Conceal messages in plain (digitally temporal) sight and decode them.

The web interface only supports png.

/tools/steganography.py can be run as is and supports png / jpg / jpeg.

~# python steganography.py -h

## Python3.6

Images are stored on the FS when using the web interface.
If a filesystem isnt available or the filesystem is ephemeral, one is created for you.
The CLI tool applies encoding without creating a backup or duplicate image. Don't use -I and say I didn't warn you!

