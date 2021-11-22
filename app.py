# import mysql.connector
import collections
import psycopg2
from dotenv import load_dotenv
import os
from flask import Flask, request , jsonify
import jwt
from functools import wraps
import datetime
import bcrypt
from cryptography.fernet import Fernet
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

app = Flask(__name__)

load_dotenv()

# UNCOMMENT FOR SERVER
DB_HOST = os.getenv('HEROKUDBHOST')
DB_NAME = os.getenv('HEROKUDATABASE')
DB_USER = os.getenv('HEROKUDBUSER')
DB_PASSWORD = os.getenv('HEROKUDBPASSWORD')
DB_PORT = os.getenv('HEROKUPORT')
SECRET_PASSWORD = os.getenv('SECRETKEY')
SALTING_KEY = os.getenv('SALTING')
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


# mydb = psycopg2.connect(
#    host = "localhost" ,
#    dbname = DATABASE,
#    user = DB_USERNAME,
#    password = DB_PASSWORD,
#    port = 5432
# )

mycursor = mydb.cursor()
# mycursor.execute("use Hassle_Free;")


# @app.route('/check' ,methods =['POST'])
# def fetch_data_username():
#    return jsonify({"message":"everything working fine"})

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

@app.route('/register' ,methods =['POST'])
def register():
   try:
      NAME = request.form['USER_NAME']
      PASSWORD = request.form['USER_PASSWORD']
      if(len(NAME)==0):
         return jsonify({"message" :"USERNAME CANNOT BE EMPTY"}),400
      if(len(PASSWORD)<=8):
         return jsonify({"message" :"PASSWORD LENGTH TOO SHORT"}),400
      if(len(PASSWORD)>=30):
         return jsonify({"message" :"PASSWORD LENGTH TOO LONG"}),400
      HASHEDPASS = bcrypt.hashpw(PASSWORD.encode('utf-8'),bcrypt.gensalt())   
      mycursor.execute("insert into hassle_free_register (USERNAME,PASSWORD) values(%s, %s);",[NAME,HASHEDPASS.decode('utf-8')]) 
      mycursor.execute("select USER_ID from Hassle_Free_Register where username = %s and password::bytea = %s;",[NAME,HASHEDPASS]) 
      data = mycursor.fetchone()
      mycursor.execute("create table {TABLENAME} (PASSWORD_ID SERIAL NOT NULL PRIMARY KEY,APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255) NOT NULL);".format(TABLENAME = NAME + "_" + str(data[0])))
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

@app.route('/login' ,methods =['POST'])
def login():
   try:
      NAME = request.form['USER_NAME']
      PASSWORD = request.form['USER_PASSWORD']
      if(len(NAME)==0):
         return jsonify({"message":"USERNAME CANNOT BE EMPTY"})
      if(len(PASSWORD)==0):
         return jsonify({"message":"PASSWORD CANNOT BE EMPTY"})

      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = NAME))
      data = mycursor.fetchone()
      
      # generation of token 
      if data:
         mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = NAME))
         hashed_pass = mycursor.fetchone()
         if bcrypt.checkpw(PASSWORD.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
            token = jwt.encode({"username":NAME,"user_id":data[0],"exp":datetime.datetime.utcnow() + datetime.timedelta(days=1)},SECRET_PASSWORD, algorithm="HS256") 
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

def check_for_token(func):
   @wraps(func)
   def wrapped():
      TOKEN = request.form['JWT_TOKEN']
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      try:
         jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      except:
         return jsonify({"message":"UNAUTHORIZED"}),403
      return func()
   return wrapped


@app.route('/insertpassword' ,methods =['POST'])
@check_for_token
def insertpassword():
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


@app.route('/decrypt' ,methods =['POST'])
@check_for_token
def decrypt():
   try:
      TOKEN = request.form['JWT_TOKEN']
      APP_PASS = request.form['APP_PASS']
      PASSWORD = request.form['PASS']
      if not APP_PASS:
         return jsonify({'message':'APP PASSWORD CANNOT BE EMPTY'}),400
      if not PASSWORD:
         return jsonify({'message':'PASSWORD CANNOT BE EMPTY'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = data['username']))
      hashed_pass = mycursor.fetchone()

      if bcrypt.checkpw(PASSWORD.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
         salt = SALTING_KEY.encode('utf-8')
         kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         )
         key = base64.urlsafe_b64encode(kdf.derive(PASSWORD.encode('utf-8')))
         f = Fernet(key)
         token = APP_PASS.encode('utf-8')
         return jsonify({"PASSWORD":str(f.decrypt(token).decode('utf-8'))})
      else:
         return jsonify({"message":"UNAUTHORIZED"}),403
   except Exception as error:
      return jsonify({"message":"error"}) 
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403

# update passowrd
# delete password
# reterive all password's

@app.route('/retrieve' ,methods =['POST'])
@check_for_token
def retrievepasswords():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      fetchData = mycursor.fetchall()
      result = []
      for fd in fetchData:
         d = collections.OrderedDict()
         d["password_id"] = fd[0]
         d["app_name"] = fd[1]
         d["username"] = fd[2]
         d["encrypted_password"] = fd[3]
         result.append(d)
      return jsonify(result)  
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404   
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403

@app.route('/delete' ,methods =['DELETE'])
@check_for_token
def deletepasswords():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      PASSWORD_ID = request.form["PASSWORD_ID"]
      if not PASSWORD_ID:
         return jsonify({'message':'Missing Password ID'}),400
      mycursor.execute("delete from {TABLENAME} where PASSWORD_ID = '{PASSWORDID}';".format(TABLENAME = data['username'] + "_" + str(data["user_id"]),PASSWORDID=PASSWORD_ID))
      mydb.commit()
      mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      fetchData = mycursor.fetchall()
      return jsonify(str(fetchData))
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404   
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403 
   

@app.route('/updatepassword' ,methods =['PUT'])
@check_for_token
def updatepasswords():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      PASSWORD = request.form["USER_PASSWORD"]
      PASSWORD_ID = request.form["PASSWORD_ID"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      if not PASSWORD_ID:
         return jsonify({'message':'MISSING PASSWORD ID'}),400
      if not PASSWORD:
         return jsonify({'message':'PASSWORD CANNOT BE EMPTY'}),400
      CHANGE_PASSWORD = request.form["CHANGE_PASSWORD"]   
      if not CHANGE_PASSWORD:
         return jsonify({'message':'MISSING CHANGE PASSWORD'}),400
      mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = data['username']))
      hashed_pass = mycursor.fetchone()
      if bcrypt.checkpw(PASSWORD.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
         salt = SALTING_KEY.encode('utf-8')
         kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         )
         key = base64.urlsafe_b64encode(kdf.derive(PASSWORD.encode('utf-8')))
         f = Fernet(key)
         changed_app_pass = f.encrypt(CHANGE_PASSWORD.encode('utf-8'))
         mycursor.execute("update {TABLENAME} SET APP_PASSWORD = %s where PASSWORD_ID = %s;".format(TABLENAME = data['username'] + "_" + str(data["user_id"])),(changed_app_pass.decode('utf-8'),PASSWORD_ID))
         mydb.commit()
         mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
         fetchData = mycursor.fetchall()
         return jsonify(str(fetchData))
      else:
         return jsonify({"message":"UNAUTHORIZED"})
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 

@app.route('/updateappname' ,methods =['PUT'])
@check_for_token
def updateappname():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      PASSWORD_ID = request.form["PASSWORD_ID"]
      if not PASSWORD_ID:
         return jsonify({'message':'Missing Password ID'}),400
      CHANGE_APPNAME = request.form["CHANGE_APPNAME"]   
      if not CHANGE_APPNAME:
         return jsonify({'message':'Missing Changed Password'}),400
      mycursor.execute("update {TABLENAME} SET APP_NAME = '{CHANGEAPPNAME}' where PASSWORD_ID = '{PASSWORDID}';".format(TABLENAME = data['username'] + "_" + str(data["user_id"]),PASSWORDID=PASSWORD_ID,CHANGEAPPNAME = CHANGE_APPNAME))
      mydb.commit()
      mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      fetchData = mycursor.fetchall()
      return jsonify(str(fetchData))
   # except mysql.connector.Error as error:
   #    print(error)
   #    return jsonify({"message":"error"}), 404
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 

@app.route('/updateappusername' ,methods =['PUT'])
@check_for_token
def updateappusername():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      PASSWORD_ID = request.form["PASSWORD_ID"]
      if not PASSWORD_ID:
         return jsonify({'message':'Missing Password ID'}),400
      CHANGE_APPUSERNAME = request.form["CHANGE_APPUSERNAME"]   
      if not CHANGE_APPUSERNAME:
         return jsonify({'message':'Missing Changed Password'}),400
      mycursor.execute("update {TABLENAME} SET APP_USERNAME = '{CHANGEAPPUSERNAME}' where PASSWORD_ID = '{PASSWORDID}';".format(TABLENAME = data['username'] + "_" + str(data["user_id"]),PASSWORDID=PASSWORD_ID,CHANGEAPPUSERNAME = CHANGE_APPUSERNAME))
      mydb.commit()
      mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      fetchData = mycursor.fetchall()
      return jsonify(str(fetchData))
   # except mysql.connector.Error as error:
   #    print(error)
   #    return jsonify({"message":"error"}), 404
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 
      
@app.route('/auth' ,methods =['POST'])
@check_for_token
def valid():
   return "ONLY IF TOKEN IS VALID"

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





@app.route('/createtable' ,methods =['POST'])
def createtable():
   try:
      NAME = request.form['USER_NAME']
      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = NAME))
      data = mycursor.fetchone()
      return jsonify(data);
   except Exception as error:
      return jsonify(str(error))
   
@app.route('/extra' ,methods =['POST'])
def extra():
   try:
      mycursor.execute("create table hassle_free_register(USER_ID SERIAL PRIMARY KEY NOT NULL, USERNAME varchar(255) NOT NULL UNIQUE ,PASSWORD varchar(255) NOT NULL);")
      mydb.commit()
      return "BUN BHAI TABLE AND DATABASE"
   except Exception as error:
      return jsonify(str(error)) 



if __name__ == '__main__':
   print("Running The Server")
   app.run()