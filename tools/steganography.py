#!/usr/bin/env python3

# Based on LSB Steganography
# Features :
#
# - Python 3.x
# - Decorator to track which method is being used (hide / retrieve)
# - Web interface integration
# - Renaming convention for duplicate files when saved. (front-end only)
# - Encode with (bug=1) -I --inspector (shows encoding)
# - Simple failure mechanisms for smoothe front end experience
#
# Notes :
#
# Messages are safe up to approximately 2000 characters; image dependent.
# Your picture will be overwritten when running from the cmd line.

from PIL import Image
import binascii as bi
import os
import functools
import inspect

# Just added for practice w/ decorators. Quite an excellent use-case
# https://stackoverflow.com/questions/9882280/find-out-if-a-function-has-been-called
def trackcalls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global path
        sig = inspect.signature(func)
        if len(sig.parameters) > 1:
            path = "static/uploads/stegs/"
        else:
            path = "static/uploads/"
        wrapper.has_been_called = True
        return func(*args, **kwargs)
    wrapper.has_been_called = False
    return wrapper


# Simple naming convention
def add_suffix(file_path):
    nf_l = list(os.path.splitext(file_path))
    nf_l = os.path.basename('%s%s' % (nf_l[0] + '_s', nf_l[1]))
    print("Constructing Filename ({})".format(nf_l))
    return nf_l

# Conversion Functions
def rgb2hex(r,g,b):
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)

def hex2rgb(hexcode):
    rgb = tuple((int(hexcode[1:3], 16), int(hexcode[3:5], 16), int(hexcode[5:], 16)))
    return rgb

def str2bin(msg):
    return ''.join([bin(ord(ch))[2:].zfill(8) for ch in msg])

def bin2str(binary):
    try:
        message = str(bi.unhexlify('%x' % (int(binary, 2))))
        return message[2:]
    # If attempting to decode msg larger than img, will throw ValueError
    except ValueError:
        print("Error - no delimiter detected.")
        print("Last sequence encountered -- {0}".format(binary[-32:]))
        return 0


# Encode / Decode Functions
####    ####    ####    ####    ####
def encode(hexcode, digit, verb=0):
    # Find slightest blue values
    if hexcode[-1] in ('0', '1', '2', '3', '4'):
        if verb:
            hexcode = hexcode[:-4] + 'aaa' + digit
        else:
            hexcode = hexcode[:-1] + digit
        return hexcode
    else:
        return None

def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None
####    ####    ####    ####    ####

@trackcalls
def hide(file_path, message, bug=0, alpha=255):

    # Arbitrary...
    if hide.has_been_called:
        print(__file__ + " < encode")

    im = Image.open(file_path)
    # message is the string message from the user input
    binary = str2bin(message) + '1111111111111110'

    if im.mode in ('RGBA'):

        # returns iterable-type
        data = im.getdata()

        # For our new image
        newData = []

        # Traverses the message
        digit = 0

        for item in data:

            if(digit < len(binary)):

                # newpix is the current r, g, b being analyzed
                if not bug:
                    newpix = encode(rgb2hex(item[0], item[1], \
                        item[2]), binary[digit])
                else:
                    newpix = encode(rgb2hex(item[0], item[1], \
                        item[2]), binary[digit], verb=1)

                # If returns None
                if newpix == None:
                    # Put the pixel back
                    newData.append(item)
                # if hex = 0 to 5
                else:
                    # Make tuple for new data
                    r, g, b = hex2rgb(newpix)
                    # append our new rgb with alpha
                    newData.append((r,g,b,alpha))
                    # track where we are in our message binary
                    digit += 1
            else:
                # If we exhaust our message, replace the original pixels
                newData.append(item)
        # Restore Image pixel data w/ our newData array
        im.putdata(newData)
        # file_path = os.path.dirname('.')

        # If ran by Flask
        if switch:

            global path
            from .helpers import rename
            # Format new filename with our function
            file_path = add_suffix(file_path)

            # Where the steg file will save to
            file_path = '%s/%s' % (path, file_path)
            if(os.path.exists(file_path)):
                # Rename if file exists
                file_path = rename(file_path, path)

        # Save
        if not (im.save(file_path, "PNG")):
            im.close()
            print(__file__ + " < success : {}".format(file_path))
            # end scene
            return file_path
        else:
            print(__file__ + " < error : unable to write file")
    # Front-end err-safe
    elif switch == 1:
        return False
    else:
        return "Incorrect Img mode : Failing gracefully"


def retr(file_path):
    global path

    # Arbitrary...
    #if retr.has_been_called:
    #    print(__file__ + " < decode")

    im = Image.open(file_path)
    binary = ''
    if im.mode in ('RGBA'):
        # Just for consistency
        im = im.convert('RGBA')
        data = im.getdata()
        # loop through the images pixel data
        for item in data:
            # Turn our pixels into hex, decode checks for a 0 or 1 in the blue pixel position.
            digit = decode(rgb2hex(item[0], item[1], item[2]))
            # Ignore otherwise
            if digit == None:
                pass
            # Found a 0 or 1
            else:
                # append to our binary (potential message) array
                binary = binary + digit
                # If the last 16 bits were our delimiter
                if(binary[-16:] == '1111111111111110'):
                    # We have retrieved our message
                    # Return our string
                    # Test from READALL.PY {b} because this will return a b'' object
                    return bin2str(binary[:-16])
        # Return what was found, regardless
        return bin2str(binary)
    return "Incorrect image mode"

def Main():
    parser = argparse.ArgumentParser(prog="steganography.py", description="Steganographic Image Processor")
    # Create switches
    parser.add_argument("target", help="Image file to be encoded.")
    parser.add_argument("-I", "--inspector", help="Highlights encoded pixels on output", action="store_true")
    parser.add_argument("-d", "--decode", help="Decode an image", action="store_true")
    parser.add_argument("-e", "--encode", help="Encode a message", action="store_true")
    # Initialize switches
    args = parser.parse_args()

    if args.encode:
        file_path = args.target
        if not args.target:
            return "error: no file detected."
        message = input("Enter Message : ")
        if message and file_path:
            if args.inspector:
                print(__file__ + "Running inspector")
                hide(file_path, message, bug=1)
            else:
                hide(file_path, message)
    if args.decode:
        file_path = args.target
        if not args.target:
            return "error: no file detected."
        if file_path:
            news = retr(file_path)
            print(news)

if __name__ == '__main__':

    import argparse
    switch = 0
    Main()
else:
    path = ''
    switch = 1
