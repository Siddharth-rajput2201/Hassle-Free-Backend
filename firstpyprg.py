import mysql.connector
from dotenv import load_dotenv
import os
from flask import Flask, json, request , jsonify


load_dotenv()
SQL_PASSWORD = os.getenv('PASSWORD')

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
   NAME = request.form['USER_NAME']
   PASSWORD = request.form['USER_PASSWORD']
   mycursor.execute("insert into Hassle_Free_Register(USERNAME,PASSWORD) values('{USER_NAME}','{USER_PASSWORD}');".format(USER_NAME = NAME,USER_PASSWORD = PASSWORD))
   data = mycursor.fetchall()
   mydb.commit()
   return jsonify(data)
   # print("insert into Hassle_Free_Register values ('{USER_NAME}','{USER_PASSWORD}');".format(USER_NAME = NAME,USER_PASSWORD = PASSWORD))

if __name__ == '__main__':
   app.run()