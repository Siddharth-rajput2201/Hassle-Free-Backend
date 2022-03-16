import base64
from flask import render_template, request , jsonify , blueprints
import jwt
import collections
from Auth.authhelper import check_for_token_email
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


data_blueprint = blueprints.Blueprint('data_blueprint',__name__)

@data_blueprint.route('/retrieve' ,methods =['POST'])
@check_for_token_email
def retrievepasswords():
   from app import mycursor,SECRET_PASSWORD,psycopg2
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
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}), 404 

@data_blueprint.route('/decrypt' ,methods =['POST'])
@check_for_token_email
def decrypt():
   from app import mycursor,SECRET_PASSWORD,psycopg2,SALTING_KEY
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
         backend=default_backend(),
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
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}) 