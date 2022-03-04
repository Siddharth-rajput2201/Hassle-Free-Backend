import smtplib
import os
from dotenv import load_dotenv
from flask import jsonify
import jwt
import datetime
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAILADDRESS')
EMAIL_PASSWORD = os.getenv('EMAILPASSWORD')
SECRET_JWT_KEY = os.getenv('SECRETEMAILJWTKEY')

def sendEmailVerification(inputUserID,inputEmail,inputUsername):
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        try:
            smtp.login(str(EMAIL_ADDRESS),str(EMAIL_PASSWORD))
            token = jwt.encode({"user_id":inputUserID,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},SECRET_JWT_KEY, algorithm="HS256")
            link = "http://192.168.0.104:5000/auth/verifyemail?t="+token.decode('utf-8')
            print(link)
            subject = 'ACCOUNT VERIFICATION REQUEST INTIATION - HASSLE FREE'
            body = "Hello {username},\nThanks for registering with Hassle Free. \n WE BELIEVE IN PRIVACY\n Click here to verfiy your account : {verificationlink}".format(username = str(inputUsername) , verificationlink=str(link))
            msg = f'SUBJECT:{subject}\n\n{body}'
            smtp.sendmail(EMAIL_ADDRESS,inputEmail,msg)
        except Exception as error:
            return jsonify({"message":"error"}),400
    