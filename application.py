# All uploads / Stegs are saved to the FS
# Decodes are saved to user_temp but purged after each successful request
import pathlib
import os
import time
import pytz
from datetime import datetime
from PIL import Image
from flask import Flask, url_for, redirect, render_template, request, session, flash, after_this_request, jsonify
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect, CSRFError
from .tools.forms import User_Form, Decode
from .tools.helpers import get_stats, rename
from .tools.plot import plots
from .tools import steganography as STG


app = Flask(__name__)
csrf = CSRFProtect(app)
bootstrap = Bootstrap(app)

app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY') or \
    'e42af6a5ecc8a-d73d2dafe6c-0f0c-acea49e8f-61a422ce65a88cce01'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'bb4a312c-500bf-21caaf5-78efaa3-dd6e1f34a90adaf7-4af'
app.config['UPLOAD_FOLDER'] = str(pathlib.Path('static/uploads'))
app.config['STATIC_PATH_S'] = str(pathlib.Path('uploads/stegs'))
app.config['TEMP_FOLDER'] = str(pathlib.Path('user_temp'))

tz_east = pytz.timezone('US/Eastern')
dt_east = datetime.now(tz=tz_east)


@app.route('/', methods=['GET', 'POST'])
def subform():

    form=User_Form()

    if request.method == "POST" and form.validate():

        pth = app.config['UPLOAD_FOLDER']

        # Get Image and sub-mode
        f = form.upload.data
        v = form.verbose.data

        # Sanitize Image path
        filename = str(secure_filename(f.filename))
        # Collect Message
        message = str(form.message_area.data)

        # Enumerate names if duplicate
        if os.path.exists(pth + "/" + str(pathlib.Path(filename))):
            filename = rename(filename, pth + "/")

        if filename:
            # Save original to
            f.save(os.path.join(pth, filename))

            # Change filename to a path in 'stegs'

            filename = os.path.join(pth, filename)
            # Get Pixel Distrobution totals
            rb, bb, gb = get_stats(filename)

            # Original Image
            # [:-1] is auxillary. Might aid portability
            u_photo = '/'.join(filename.split('/')[1:])

            # User Conditions
            if not v:
                try:
                    s_photo = os.path.basename(STG.hide(filename, message))
                except TypeError:
                    message =   """
                                Your image path is not POSIX compliant :
                                To remedy this, simply open the image in a photo editor and re-save it as a .png
                                """
                    flash(message)
                    return redirect(url_for('subform'))
            else:
                s_photo = os.path.basename(STG.hide(str(filename), message, bug=1))

            # If the gods have failed us
            if not s_photo:
                flash("Your image could not be encoded. Sorry!")
                return redirect(url_for('subform'))
            # Log
            fd = open('user_temp/logs.log', 'a')
            fd.write('\nENCODE -- ' + filename + ' DATE -- ' + \
                dt_east.strftime('%D, %H:%M:%S') + ' -- ' \
                'ENCODED MESSAGE : ' + message + '\n')
            fd.close()

            # This constructs a POSIX Path
            s_photo = pathlib.Path(app.config['STATIC_PATH_S'] + '/' + s_photo)
            # Get pixel distrobution totals
            (ra, ba, ga) = get_stats("static/" + str(s_photo))
            #  Pie Chart / Bar Graph
            chart = plots.pie(ra, ba, ga)
            bars = plots.bar_comp(ra, ba, ga, rb, bb, gb)
            return render_template('complete.html', u_photo=u_photo, s_photo=s_photo, chart=chart, bars=bars)

    return render_template('subform.html', form=form)


@app.route('/complete')
def complete():

    @after_this_request
    def destroy_file(response):
        os.remove("user_temp/*")
        os.remove("static/uploads/*")
        return response
    return redirect(url_for('complete'))

@app.route('/decode', methods=['GET', 'POST'])
def decode():

    form = Decode()

    if request.method == 'POST' and form.validate():
        # Get user's file
        f = form.upload.data

        if not f:
            flash('No file detected')
            return redirect(url_for('decode'))

        # Sanitize
        veri_path = secure_filename(f.filename)
        if veri_path:

            im = Image.open(f)
            im.save(app.config['TEMP_FOLDER'] + '/' + veri_path, 'PNG')
            # time.sleep(3)
            im.close()

            # Locate Sanitized Image and Decode
            if os.path.exists("user_temp/" + veri_path):
                message = STG.retr("user_temp/" + veri_path)
                if not message:
                    message = """
                        No message was detected.
                        Perhaps the message was too long, or the image too small.
                        Make sure your message is of adequate size and try again.
                        """
                    flash(message)
                    return redirect(url_for('subform'))

            # A reliable tempfile
            @after_this_request
            def destroy_file(response):
                os.remove("user_temp/" + veri_path)
                print(response)
                return response

            # Log
            fd = open('user_temp/logs.log', 'a')
            fd.write('\nDECODE -- ' + veri_path + ' DATE -- ' + \
                dt_east.strftime('%D %H:%M:%S') + ' -- DECODED MESSAGE : ' + message + '\n')
            fd.close()

            return render_template('message.html', message=message)
        else:
            flash('Error Uploading Image')
            return redirect(url_for('decode'))

    return render_template('decode.html', form=form)


# Errors
@app.errorhandler(CSRFError)
def csrf_error(e):
    # Will print to console, not noticeable from front end
    return "CSRF ERROR"
