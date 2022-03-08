import smtplib
import os
from dotenv import load_dotenv
from flask import request ,jsonify
import jwt
import datetime
from functools import wraps
load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAILADDRESS')
EMAIL_PASSWORD = os.getenv('EMAILPASSWORD')
SECRET_JWT_KEY = os.getenv('SECRETEMAILJWTKEY')

def sendEmailVerification(inputEmail,inputUsername):
    from app import mycursor
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        try:
            mycursor.execute("select EMAIL_VERIFICATION from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = inputUsername))
            STATUS = mycursor.fetchone()
            if(STATUS[0]==False):
                smtp.login(str(EMAIL_ADDRESS),str(EMAIL_PASSWORD))
                token = jwt.encode({"username":inputUsername,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},SECRET_JWT_KEY, algorithm="HS256")
                link = "https://hassle-free.herokuapp.com/auth/verifyemail?t="+token.decode('utf-8')
                subject = 'ACCOUNT VERIFICATION REQUEST INTIATION - HASSLE FREE'
                body = "Hello {username},\nThanks for registering with Hassle Free. \n WE BELIEVE IN PRIVACY\n Click here to verfiy your account : {verificationlink}".format(username = str(inputUsername) , verificationlink=str(link))
                msg = f'SUBJECT:{subject}\n\n{body}'
                smtp.sendmail(EMAIL_ADDRESS,inputEmail,msg)
            else:
                return jsonify({"message":"ACCOUNT ALREADY VERIFIED"}),400 
        except Exception as error:
            return jsonify({"message":"error"}),400

def sendDeleteAccountVerification(inputEmail,inputUsername):
    from app import mycursor
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        try:
            mycursor.execute("select EMAIL_VERIFICATION from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = inputUsername))
            STATUS = mycursor.fetchone()
            print(STATUS)
            if(STATUS[0]==True):
                smtp.login(str(EMAIL_ADDRESS),str(EMAIL_PASSWORD))
                token = jwt.encode({"username":inputUsername,"exp":datetime.datetime.utcnow() + datetime.timedelta(minutes=5)},SECRET_JWT_KEY, algorithm="HS256")
                print(token)
                link = "https://hassle-free.herokuapp.com/delete/deleteaccount?t="+token.decode('utf-8')
                subject = 'ACCOUNT DELETION REQUEST INTIATION - HASSLE FREE'
                body = "Hello {username},\nWe are sad to see you gooo . :( \n WE BELIEVE IN PRIVACY\n Click here to delete your account : {deletionlink}".format(username = str(inputUsername) , deletionlink=str(link))
                msg = f'SUBJECT:{subject}\n\n{body}'
                smtp.sendmail(EMAIL_ADDRESS,inputEmail,msg)
            else:
                return jsonify({"message":"ACCOUNT NOT VERIFIED"}),400 
        except Exception as error:
            return jsonify({"message":"error"}),400

def login(inputEmail):
    from app import mycursor
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp:
        try:           
            smtp.login(str("hasslefreenoreply@gmail.com"),str("tH!sIsN0tpA55w03d"))
            smtp.sendmail("hasslefreenoreply@gmail.com",inputEmail,"HELLO")
            return "OK"
        except Exception as error:
            return jsonify({"message":"error"}),400
