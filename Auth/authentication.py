# import collections
import psycopg2
# from dotenv import load_dotenv
# import os
from flask import Flask, request , jsonify , blueprints
import jwt
# from functools import wraps
import datetime
import bcrypt
from Auth.authhelper import checkForDigit , checkForUpper , checkForSpecialChar , checkForLower
# from cryptography.fernet import Fernet
# import base64
# from cryptography.fernet import Fernet
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


auth_blueprint = blueprints.Blueprint('auth_blueprint', __name__)

@auth_blueprint.route('/register' ,methods =['POST'])
def register():
   from app import mycursor,mydb
   try:
      name = request.form['USER_NAME']
      password = request.form['USER_PASSWORD']
      if(len(name)==0):
         return jsonify({"message" :"USERNAME CANNOT BE EMPTY"}),400
      if(len(password)<=8):
         return jsonify({"message" :"PASSWORD LENGTH TOO SHORT"}),400
      if(len(password)>=30):
         return jsonify({"message" :"PASSWORD LENGTH TOO LONG"}),400
      if(checkForDigit(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A DIGIT"}),400
      if(checkForUpper(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A UPPER CHARACTER"}),400
      if(checkForLower(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A LOWER CHARACTER"}),400
      if(checkForSpecialChar(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A SPECIAL CHARATER"}),400
      HASHEDPASS = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())   
      mycursor.execute("insert into hassle_free_register (USERNAME,PASSWORD) values(%s, %s);",[name,HASHEDPASS.decode('utf-8')]) 
      mycursor.execute("select USER_ID from Hassle_Free_Register where username = %s and password::bytea = %s;",[name,HASHEDPASS]) 
      data = mycursor.fetchone()
      mycursor.execute("create table {TABLENAME} (PASSWORD_ID SERIAL NOT NULL PRIMARY KEY,APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255) NOT NULL);".format(TABLENAME = name + "_" + str(data[0])))
      mydb.commit()
      return jsonify({"message":"REGISTERED SUCCESSFULLY"}) 
   except TypeError as error:
      print(error)
      return jsonify({"message":"error"}),400
   except ValueError as error:
      print(error)
      return jsonify({"message":"error"}),400
   except psycopg2.Error as error:
      print(error)
      if(error.pgcode == str(23505)):
         mydb.rollback()
         return jsonify({"message":"USER ALREADY REGISTERED"}),400
      else:
         mydb.rollback()
         return jsonify({"message":"error"}),403

@auth_blueprint.route('/login' ,methods =['POST'])
def login():
   from app import mycursor,SECRET_PASSWORD
   try:
      name = request.form['USER_NAME']
      password = request.form['USER_PASSWORD']
      if(len(name)==0):
         return jsonify({"message":"USERNAME CANNOT BE EMPTY"})
      if(len(password)==0):
         return jsonify({"message":"PASSWORD CANNOT BE EMPTY"})

      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = name))
      data = mycursor.fetchone()
      
      # generation of token 
      if data:
         mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = name))
         hashed_pass = mycursor.fetchone()
         if bcrypt.checkpw(password.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
            token = jwt.encode({"username":name,"user_id":data[0],"exp":datetime.datetime.utcnow() + datetime.timedelta(days=1)},SECRET_PASSWORD, algorithm="HS256") 
         else:
            return jsonify({"message":"INVALID CREDENTIALS"}),401
      else:
         return jsonify({"message":"USER DOES NOT EXIST"}),400
      return jsonify({"token" : token})
   except TypeError as error:
      return jsonify({"message":"error"}),400
   except ValueError as error:
      return jsonify({"message":"error"}),403
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403