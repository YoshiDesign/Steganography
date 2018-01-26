#!/usr/bin/env python3
from PIL import Image
import binascii as bi
from pathlib import Path
import os
import functools
import inspect

path = ''
# If initialized by console or web/app
switch = 1

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
    print("Constructing Filename -- {}".format(nf_l))
    return nf_l


def rgb2hex(r,g,b):
    # print("RGB-2-HEX r-{} g-{} b-{}".format(r, g, b))
    return '#{:02x}{:02x}{:02x}'.format(r,g,b)


def hex2rgb(hexcode):
    # print("HEX-2-RGB {}".format(hexcode))
    rgb = tuple((int(hexcode[1:3], 16), int(hexcode[3:5], 16), int(hexcode[5:], 16)))
    return rgb


# binary of ordinal character, replace truncated prefix with zfill
def str2bin(msg):
    # print("STR-2-BIN {}".format(msg))
    return ''.join([bin(ord(ch))[2:].zfill(8) for ch in msg])


# format bin to int to hex to str for retr()
def bin2str(binary):
    try:
        message = str(bi.unhexlify('%x' % (int(binary, 2))), 'utf-8')
        return message
    # This bypasses any potential '0b' prefixes encountered:
    # Typically the first byte
    except ValueError:
        return "Remember, remember; drink your Ovaltine"


## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

def encode(hexcode, digit):
    # Find lowest blue values
    if hexcode[-1] in ('0', '1', '2', '3', '4'):
        # print("encoding {} with {}".format(hexcode, digit))
        hexcode = hexcode[:-1] + digit
        return hexcode
    else:
        return None

def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None

## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
@trackcalls
def hide(file_path, message):

    im = Image.open(file_path)
    # message is the string message from the user input
    binary = str2bin(message) + '1111111111111110'

    # check if it is editable (PNG = RGBA / L)
    if im.mode in ('RGBA'):
        #im = im.convert('RGBA')

        # getdata() returns a sequence-like object type-defined by PIL
        # This can also be converted to a Py list-type
        data = im.getdata()

        # For our new image
        newData = []

        # Traverses the message
        digit = 0

        for item in data:

            if(digit < len(binary)):

                # newpix is the current r, g, b being analyzed
                newpix = encode(rgb2hex(item[0], item[1], \
                    item[2]), binary[digit])

                # If returns None
                if newpix == None:
                    # Put the pixel back
                    newData.append(item)
                # if hex = 0 to 5
                else:
                    # Make tuple for new data
                    r, g, b = hex2rgb(newpix)
                    # append our new rgb with alpha
                    newData.append((r,g,b,255))
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
        im.save(file_path, "PNG")
        im.close()
        print("Steganography complete on -- {}".format(file_path))
        # end scene
        return file_path

    elif switch == 1:
        return False
    else:
        return "Incorrect Img mode : Failing gracefully"

@trackcalls
def retr(file_path):
    global path
    im = Image.open(file_path)
    binary = ''
    if im.mode in ('RGBA'):
        # Just for consistency
        #im = im.convert('RGBA')
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
                    print("success")
                    # Return our string
                    # Test from READALL.PY {b} because this will return a b'' object
                    return bin2str(binary[:-16])
        # Return what was found, regardless
        return bin2str(binary)
    return "Incorrect image mode"

def Main():
    parser = argparse.ArgumentParser(prog="steganography.py", description="Steganographic Image Processor")

    parser.add_argument("target", help="Image file to be encoded.")
    parser.add_argument("-d", "--decode", help="Decode Message", action="store_true")
    parser.add_argument("-e", "--encode", help="Encode Message", action="store_true")

    args = parser.parse_args()
    if args.encode:
        file_path = args.target
        message = input("Enter Message : ")
        if message and file_path:
            hide(file_path, message)
    if args.decode:
        file_path = args.target
        if file_path:
            news = retr(file_path)
            print(news)

if __name__ == '__main__':

    import argparse
    switch = 0
    Main()


if retr.has_been_called:
    print("Steganographic message retrieved successfully.")

if hide.has_been_called:
    print("Steganographic image encoded successfully.")





