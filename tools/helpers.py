import os
from PIL import Image
from functools import wraps
from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from .plot import plots

# Rename file if it already exists
def rename(file, dest, count=1, steg=False):

    prefix, ext = os.path.splitext(file)

    # The 7 dwarves had better naming conventions...
    if count > 9:
        # Probably not though.
        new_name = '%s(%d)%s' % (prefix[-3:-2], count, ext)
    if count > 1:
        new_name = '%s(%d)%s' % (prefix[:-3], count, ext)
    else:
        new_name = '%s(%d)%s' % (prefix, count, ext)

    # If exists already, try again
    if os.path.exists(dest + new_name):
        return rename(new_name, dest, count=count+1)

    else:
        print("file renamed - %s" % (new_name))
        return new_name

# Gather arbitrary data
def get_stats(picture):

    im_s = Image.open(picture)

    # (width, height)
    if not im_s:
        return 'file format error'
    im_s.convert('RGBA')

    # Get name & simple metrics
    name = im_s.filename
    (width, height) = im_s.width, im_s.height
    area = width * height
    reds, greens, blues = 0, 0, 0

    # Array of all pixels in arg
    pixel_data = im_s.getdata()

    # Collect rgb value totals
    try:
        for item in pixel_data:
            reds += item[0]
            greens += item[1]
            blues += item[2]
    except TypeError:
        for i, item in enumerate(pixel_data):
            if not (i % 3):
                blues += pixel_data[i]
            elif not (i % 2):
                greens += pixel_data[i]
            elif not (i % 1):
                reds += pixel_data[i]
    finally:
        print('P Data - {}'.format(pixel_data))

    im_s.close()

    stats = {
        'width' : width,
        'height': height,
        'pixels':{
            'red-pix' : reds // area,
            'green-pix' : greens // area,
            'blue-pix' : blues // area
        }
    }

    return (int(stats['pixels']['red-pix']) , \
        int(stats['pixels']['green-pix']), \
        int(stats['pixels']['blue-pix']))

