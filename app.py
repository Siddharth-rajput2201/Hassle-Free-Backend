import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, json, request , jsonify
import jwt
from functools import wraps
import datetime

load_dotenv()
SQL_PASSWORD = os.getenv('PASSWORD')
SECRET_PASSWORD = os.getenv('SECRETKEY')
mydb = mysql.connector.connect(
   host = "localhost" ,
   user = "root",
   password =  SQL_PASSWORD,
)

mycursor = mydb.cursor()
mycursor.execute("use Hassle_Free;")

#query = """insert into marks values ("Sid",036,101)""";
# mycursor.execute(query)
# mydb.commit()
# mycursor.execute(str)
# mycursor.execute("update marks SET marks = 99 WHERE name = 'Sid';")
# mycursor.execute("delete from marks where name = 'Sid';")
# mycursor.execute("select * from marks;")
# data = mycursor.fetchall()
# print(data)


app = Flask(__name__)



@app.route('/fetchByName' ,methods =['POST'])
def fetch_data_username():
    name = request.form['name']
    mycursor.execute("select * from Hassle_Free_Register where USERNAME = '{qname}';".format(qname = name))
    data = mycursor.fetchall()
    return jsonify(data);

@app.route('/fetchAllData' ,methods =['GET'])
def fetch_all_data():
    mycursor.execute("select * from Hassle_Free_Register;")
    data = mycursor.fetchall()
    return jsonify(data);

@app.route('/register' ,methods =['POST'])
def register():
   try:
      NAME = request.form['USER_NAME']
      PASSWORD = request.form['USER_PASSWORD']
      if(len(NAME)==0):
         raise ValueError("USERNAME CANNOT BE EMPTY")
      if(len(PASSWORD)<=8):
         raise ValueError("PASSWORD LENGTH TOO SHORT")
      if(len(PASSWORD)>=30):
         raise ValueError("PASSWORD LENGTH TOO LONG")
      mycursor.execute("insert into Hassle_Free_Register(USERNAME,PASSWORD) values('{USER_NAME}','{USER_PASSWORD}');".format(USER_NAME = NAME,USER_PASSWORD = PASSWORD))
      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}' and PASSWORD = '{USER_PASSWORD}';".format(USER_NAME = NAME,USER_PASSWORD = PASSWORD))
      data = mycursor.fetchone()
      mycursor.execute("create table {TABLENAME} (PASSWORD_ID int NOT NULL AUTO_INCREMENT ,APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255) NOT NULL,PRIMARY KEY (PASSWORD_ID));".format(TABLENAME = NAME + "_" + str(data[0])))
      mydb.commit()
      return jsonify("REGISTERED SUCCESSFULLY") 
   except ValueError as error:
      return jsonify({"message":str(error)}),403
   except mysql.connector.Error as error:
      print(error)
      return jsonify({"message":"error"}), 404

@app.route('/login' ,methods =['POST'])
def login():
   try:
      NAME = request.form['USER_NAME']
      PASSWORD = request.form['USER_PASSWORD']
      if(len(NAME)==0):
         raise ValueError("USERNAME CANNOT BE EMPTY")
      if(len(PASSWORD)==0):
         raise ValueError("PASSWORD CANNOT BE EMPTY")
      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}' and PASSWORD = '{USER_PASSWORD}';".format(USER_NAME = NAME , USER_PASSWORD = PASSWORD))
      data = mycursor.fetchone()
      if data:
         token = jwt.encode({"username":NAME,"user_id":data[0],"exp":datetime.datetime.utcnow() + datetime.timedelta(days=1)},SECRET_PASSWORD, algorithm="HS256") 
      else:
         raise ValueError("INVALID CREDENTIALS")
      return jsonify({"token" : token})

   except ValueError as error:
      mycursor.rollback()
      return jsonify({"message":str(error)}),403
   except mysql.connector.Error as error:
      mycursor.rollback()
      print(error)
      return jsonify({"message":"error"}), 403
      

def check_for_token(func):
   @wraps(func)
   def wrapped():
      TOKEN = request.form['JWT_TOKEN']
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      try:
         jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      except:
         return jsonify({"message":"error"}),401
      return func()
   return wrapped


@app.route('/insertpassword' ,methods =['POST'])
@check_for_token
def insertpassword():
   try:
      APP_NAME = request.form["APP_NAME"]
      APP_USERNAME = request.form["APP_USERNAME"]
      APP_PASSWORD = request.form["APP_PASSWORD"]
      if not APP_NAME:
         raise ValueError("app name cannot be empty")
      if not APP_USERNAME:
         raise ValueError("app username cannot be empty")
      if not APP_PASSWORD:
         raise ValueError("app password cannot be empty")
      TOKEN = request.form["JWT_TOKEN"]
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      mycursor.execute("insert into {TABLENAME}(APP_NAME,APP_USERNAME,APP_PASSWORD) values ('{APPNAME}','{APPUSERNAME}','{APPPASSWORD}');".format(TABLENAME = data['username'] + "_" + str(data['user_id']),APPNAME=APP_NAME,APPUSERNAME=APP_USERNAME,APPPASSWORD=APP_PASSWORD))
      mydb.commit()
      return jsonify({"message":"ADDED SUCCESSFULLY"}),200
   except ValueError as error:
      return jsonify({"message":str(error)}),403
   except mysql.connector.Error as error:
      print(error)
      return jsonify({"message":"error"}), 403

# update passowrd
# delete password
# reterive all password's

@app.route('/retrieve' ,methods =['POST'])
@check_for_token
def retrievepasswords():
   try:
      TOKEN = request.form["JWT_TOKEN"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      fetchData = mycursor.fetchall()
      return jsonify(str(fetchData))
   except mysql.connector.Error as error:
      print(error)
      return jsonify({"message":"error"}), 404
      
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
   except mysql.connector.Error as error:
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
      NAME = request.form['USER_NAME']
      mycursor.execute("select USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = NAME))
      data = mycursor.fetchone()
      mycursor.execute("create table {TABLENAME} (APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255));".format(TABLENAME = NAME + "_" + str(data[0])))
      return "SUCCESS CREATED TABLE"
   except Exception as error:
      return jsonify(str(error))
if __name__ == '__main__':
   app.run()