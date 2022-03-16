import base64
from flask import render_template, request , jsonify , blueprints
import jwt
from Auth.authhelper import check_for_token_email
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


update_blueprint = blueprints.Blueprint('update_blueprint',__name__)

@update_blueprint.route('/updatepass' ,methods =['PUT'])
@check_for_token_email
def updatepasswords():
   from app import mycursor,mydb,SECRET_PASSWORD,SALTING_KEY
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
         backend=default_backend(),
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
         # mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
         # fetchData = mycursor.fetchall()
         return jsonify({"message":"UPDATED SUCCESSFULLY"}),200
      else:
         return jsonify({"message":"UNAUTHORIZED"})
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 

@update_blueprint.route('/updateappname' ,methods =['PUT'])
@check_for_token_email
def updateappname():
   from app import mycursor,mydb,SECRET_PASSWORD
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
      # mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      # fetchData = mycursor.fetchall()
      return jsonify({"message":"UPDATED SUCCESSFULLY"}),200
   # except mysql.connector.Error as error:
   #    print(error)
   #    return jsonify({"message":"error"}), 404
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 

@update_blueprint.route('/updateappusername' ,methods =['PUT'])
@check_for_token_email
def updateappusername():
   from app import mycursor,mydb,SECRET_PASSWORD
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
      # mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      # fetchData = mycursor.fetchall()
      return jsonify({"message":"UPDATED SUCCESSFULLY"}),200
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 