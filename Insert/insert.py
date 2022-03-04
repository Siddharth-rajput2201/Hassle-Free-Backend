import psycopg2
from dotenv import load_dotenv
from flask import  request , jsonify , blueprints
import jwt
from functools import wraps
import bcrypt
from cryptography.fernet import Fernet
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from Auth.authhelper import check_for_token_email

insert_blueprint = blueprints.Blueprint('insert_blueprint', __name__)

@insert_blueprint.route('/insertpass' ,methods =['POST'])
@check_for_token_email
def insertpassword():
   from app import mycursor,mydb,SECRET_PASSWORD , SALTING_KEY
   try:
      PASSWORD = request.form["USER_PASSWORD"]
      APP_NAME = request.form["APP_NAME"]
      APP_USERNAME = request.form["APP_USERNAME"]
      APP_PASSWORD = request.form["APP_PASSWORD"]
      if not PASSWORD:
         return jsonify({"message":"PASSWORD CANNOT BE EMPTY"}),400
      if not APP_NAME:
         return jsonify({"message":"APP NAME CANNOT BE EMPTY"}),400
      if not APP_USERNAME:
         return jsonify({"message":"APP USERNAME CANNOT BE EMPTY"}),400
      if not APP_PASSWORD:
         return jsonify({"message":"APP PASSWORD CANNOT BE EMPTY"}),400
      TOKEN = request.form["JWT_TOKEN"]
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = data['username']))
      hashed_pass = mycursor.fetchone()
      if bcrypt.checkpw(PASSWORD.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
         salt = SALTING_KEY.encode('utf-8')
         kdf = PBKDF2HMAC(
         backend=default_backend(),
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         )
        
         key = base64.urlsafe_b64encode(kdf.derive(PASSWORD.encode('utf-8')))
         f = Fernet(key)
         app_pass = f.encrypt(APP_PASSWORD.encode('utf-8'))
         mycursor.execute("insert into {TABLENAME} (APP_NAME,APP_USERNAME,APP_PASSWORD) values (%s,%s,%s);".format(TABLENAME = data['username'] + "_" + str(data['user_id'])),(APP_NAME,APP_USERNAME,app_pass.decode('utf-8')))
         mydb.commit()
         return jsonify({"message":"ADDED SUCCESSFULLY"}),200
      else:
         return jsonify({"message":"UNAUTHORIZED"}),403
   except TypeError as error:
      print(error)
      return jsonify({"message":"error"}),403
   except ValueError as error:
      print(error)
      return jsonify({"message":"error"}),400
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}),403