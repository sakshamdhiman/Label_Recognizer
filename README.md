# Label_Recognizer
### This program labels the contents in any given picture. It is made using the AWS platform where the uploaded photos are stored on AWS S3, labels are generated using AWS Rekognition and the labels generated for the photos are stored in AWS RDS. All of this can be viewed on a web interface using AWS EC2.

![Screenshot (552)](https://user-images.githubusercontent.com/28104166/99189260-5d56c280-2786-11eb-9879-dc182932fd68.png)

### Running the project -
#### On local Instance - 
- Upload the attached folder on AWS Cloud9.
- Configure Environment variables ("ENV" in top right corner of terminal)-
  - PHOTOS_BUCKET : name of the S3 bucket you will create to save the photos
  - FLASK_SECRET : any alphanumeric string
  - DATABASE_HOST : database endpoint of the database you will create to store the labels 
  - DATABASE_USER : database username 
  - DATABASE_PASSWORD : database user password
  - DATABASE_DB_NAME : database name 
- Runner : Python3
- Command : Label_recognizer/FlaskApp/application.py
- Run the terminal with these commands and open the preview pane. The program should be running, test it by uploading a photo.

#### On global instance - 
- Upload a zip file of this folder to S3 bucket
- In Deploy/userdata.txt change "BUCKET_NAME" to your S3 bucket name.
- Create EC2 instance and paste all content from Deploy/userdata.txt in userdata textbox and create instance.
- Open the public ip for created instance. The program should be running. 



