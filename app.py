# import mysql.connector
import collections
from doctest import debug
import psycopg2
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request , jsonify
import jwt
import datetime
import bcrypt
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from Auth.authentication import auth_blueprint
from Delete.delete import delete_blueprint
from Insert.insert import insert_blueprint
from Auth.e_mail import email_blueprint
from Update.update import update_blueprint
from Data.data import data_blueprint
from Auth.authhelper import check_for_token_email


app = Flask(__name__)
app.register_blueprint(auth_blueprint,url_prefix='/auth')
app.register_blueprint(delete_blueprint,url_prefix='/delete')
app.register_blueprint(insert_blueprint,url_prefix='/insert')
app.register_blueprint(email_blueprint,url_prefix='/emailauth')
app.register_blueprint(update_blueprint,url_prefix='/update')
app.register_blueprint(data_blueprint,url_prefix='/data')
load_dotenv()

# UNCOMMENT FOR SERVER
DB_HOST = os.getenv('HEROKUDBHOST')
DB_NAME = os.getenv('HEROKUDATABASE')
DB_USER = os.getenv('HEROKUDBUSER')
DB_PASSWORD = os.getenv('HEROKUDBPASSWORD')
DB_PORT = os.getenv('HEROKUPORT')
SECRET_PASSWORD = os.getenv('SECRETKEY')
SALTING_KEY = os.getenv('SALTING')
EMAILADDRESS = os.getenv('EMAILADDRESS')
EMAILPASSWORD = os.getenv('EMAILPASSWORD')
SECRET_JWT_KEY = os.getenv('SECRETEMAILJWTKEY')
mydb = psycopg2.connect(
   host = DB_HOST ,
   dbname = DB_NAME,
   user = DB_USER,
   password = DB_PASSWORD,
   port = DB_PORT
)

# UNCOMMENT FOR LOCAL
# DB_PASSWORD = os.getenv('PASSWORD')
# SECRET_PASSWORD = os.getenv('SECRETKEY')
# SALTING_KEY = os.getenv('SALTING')
# DB_USERNAME = os.getenv('DBUSERNAME')
# DATABASE = os.getenv('DATABASE')
# EMAIL_ADDRESS = os.getenv('EMAILADDRESS')
# EMAIL_PASSWORD = os.getenv('EMAILPASSWORD')
# SECRET_JWT_KEY = os.getenv('SECRETEMAILJWTKEY')

# mydb = psycopg2.connect(
#    host = "localhost" ,
#    dbname = DATABASE,
#    user = DB_USERNAME,
#    password = DB_PASSWORD,
#    port = 5432
# )

mycursor = mydb.cursor()


@app.route('/fetchByName' ,methods =['POST'])
def fetch_data_username():
    name = request.form['name']
    mycursor.execute("select * from Hassle_Free_Register where USERNAME = '{qname}';".format(qname = name))
    data = mycursor.fetchall()
    return jsonify(data)
    
@app.route('/fetchAllData' ,methods =['GET'])
def fetch_all_data():
    mycursor.execute("select * from Hassle_Free_Register;")
    data = mycursor.fetchall()
    return jsonify(data)


@app.route('/token' ,methods =['POST'])
def generatetoken():
   NAME = request.form['USER_NAME']
   PASSWORD = request.form['USER_PASSWORD']
   token = jwt.encode({"username ":NAME,"password":PASSWORD}, SECRET_PASSWORD, algorithm="HS256")
   return jsonify(token)


@app.route('/decode' ,methods =['POST'])
def decodetoken():
   try:
      TOKEN = request.form['JWT_TOKEN']
      decoded = jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      return jsonify(decoded)
   except Exception as error:
      return jsonify(str(error))


@app.route('/test' ,methods =['POST'])
def createtable():
   try:
      NAME = request.form['USER_NAME']
      mycursor.execute("select USER_ID,EMAIL_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = NAME))
      data = mycursor.fetchone()
      print(data[1])
      return jsonify(data);
   except Exception as error:
      return jsonify(str(error))
   
@app.route('/extra' ,methods =['POST'])
def extra():
   try:
      mycursor.execute("create table hassle_free_register(USER_ID SERIAL PRIMARY KEY NOT NULL, USERNAME varchar(255) NOT NULL UNIQUE ,PASSWORD varchar(255) NOT NULL,EMAIL_ID varchar(255) NOT NULL UNIQUE , EMAIL_VERIFICATION boolean NOT NULL );")
      mydb.commit()
      return "BUNGYA BHAI TABLE AND DATABASE"
   except Exception as error:
      return jsonify(str(error)) 

if __name__ == '__main__':
   print("Running The Server")
   app.run(debug=False)
