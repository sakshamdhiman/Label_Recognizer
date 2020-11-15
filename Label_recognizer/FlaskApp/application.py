"Demo Flask application"
import sys

import requests
import boto3
from flask import Flask, render_template_string
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

import config
import util
import database

application = Flask(__name__)
application.secret_key = config.FLASK_SECRET

### FlaskForm set up
class PhotoForm(FlaskForm):
    """flask_wtf form class the file upload"""
    photo = FileField('image', validators=[
        FileRequired()
    ])


@application.route("/", methods=('GET', 'POST'))
def home():
    """Homepage route"""
    all_labels = ["No labels yet"]

    
    s3_client = boto3.client('s3')
    photos = database.list_photos()
    for photo in photos:
        photo["signed_url"] = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': config.PHOTOS_BUCKET, 'Key': photo["object_key"]}
        )

    form = PhotoForm()
    url = None
    if form.validate_on_submit():
        image_bytes = util.resize_image(form.photo.data, (300, 300))
        if image_bytes:
            #######
            # s3 
            #######
            prefix = "photos/"
            key = prefix + util.random_hex_bytes(8) + '.png'
            s3_client.put_object(
                Bucket=config.PHOTOS_BUCKET,
                Key=key,
                Body=image_bytes,
                ContentType='image/png'
            )
            
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': config.PHOTOS_BUCKET, 'Key': key})

            #######
            # rekcognition 
            #######
            rek = boto3.client('rekognition')
            response = rek.detect_labels(
                Image={
                    'S3Object': {
                        'Bucket': config.PHOTOS_BUCKET,
                        'Name': key
                    }
                })
            all_labels = [label['Name'] for label in response['Labels']]

            labels_comma_separated = ", ".join(all_labels)
            database.add_photo(key, labels_comma_separated)

    return render_template_string("""
            {% extends "main.html" %}
            {% block content %}
            <h4>Upload Photo</h4>
            <form method="POST" enctype="multipart/form-data" action="{{ url_for('home') }}">
                {{ form.csrf_token }}
                  <div class="control-group">
                   <label class="control-label">Photo</label>
                    {{ form.photo() }}
                  </div>

                    &nbsp;
                   <div class="control-group">
                    <div class="controls">
                        <input class="btn btn-primary" type="submit" value="Upload">
                    </div>
                  </div>
            </form>

            {% if url %}
            <hr/>
            <h3>Uploaded!</h3>
            <img src="{{url}}" /><br/>
            {% for label in all_labels %}
            <span class="label label-info">{{label}}</span>
            {% endfor %}
            {% endif %}
            
            {% if photos %}
            <hr/>
            <h4>Photos</h4>
            {% for photo in photos %}
                <table class="table table-bordered">
                <tr> <td rowspan="4" class="col-md-2 text-center"><img width="150" src="{{photo.signed_url}}" /> </td></tr>
                <tr> <th scope="row" class="col-md-2">Labels</th> <td>{{photo.labels}}</td> </tr>
                <tr> <th scope="row" class="col-md-2">Created</th> <td>{{photo.created_datetime}} UTC</td> </tr>
                </table>

            {% endfor %}
            {% endif %}


            {% endblock %}
                """, form=form, url=url, photos=photos, all_labels=all_labels)


@application.route("/info")
def info():
    "Webserver info route"
    metadata = "http://169.254.169.254"
    instance_id = requests.get(metadata +
                               "/latest/meta-data/instance-id").text
    availability_zone = requests.get(metadata +
                                     "/latest/meta-data/placement/availability-zone").text

    return render_template_string("""
            {% extends "main.html" %}
            {% block content %}
            <b>instance_id</b>: {{instance_id}} <br/>
            <b>availability_zone</b>: {{availability_zone}} <br/>
            <b>sys.version</b>: {{sys_version}} <br/>
            {% endblock %}""",
                                  instance_id=instance_id,
                                  availability_zone=availability_zone,
                                  sys_version=sys.version)


if __name__ == "__main__":
    
    use_c9_debugger = False
    application.run(use_debugger=not use_c9_debugger, debug=True,
                    use_reloader=not use_c9_debugger, host='0.0.0.0', port=8080)
