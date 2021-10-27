import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, json, request , jsonify
import jwt
from functools import wraps

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
      mycursor.execute("create table {TABLENAME} (APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255));".format(TABLENAME = NAME + "_" + str(data[0])))
      mydb.commit()
      return jsonify("REGISTERED SUCCESSFULLY") 
   except ValueError as error:
      return jsonify({"message":str(error)}),403
   except mysql.connector.Error as error:
      print(error)
      return jsonify({"message":"error"}), 403

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
         token = jwt.encode({"username ":NAME,"password":PASSWORD}, SECRET_PASSWORD, algorithm="HS256")
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


def check_for_token(func):
   @wraps(func)
   def wrapped(*args , **kwargs):
      TOKEN = request.form['JWT_TOKEN']
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),403
      try:
         data = jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      except Exception as error:
         return jsonify(error),403
      return func(*args,**kwargs)
   return wrapped



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