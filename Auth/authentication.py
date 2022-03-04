import psycopg2
from flask import request , jsonify , blueprints
import jwt
import datetime
import bcrypt
from Auth.authhelper import checkForDigit , checkForUpper , checkForSpecialChar , checkForLower , checkEmailID
from Auth.emailhelper import sendEmailVerification

auth_blueprint = blueprints.Blueprint('auth_blueprint', __name__)

@auth_blueprint.route('/register' ,methods =['POST'])
def register():
   from app import mycursor,mydb
   try:
      name = request.form['USER_NAME']
      password = request.form['USER_PASSWORD']
      email_id = request.form['EMAIL_ID']
      if(len(name)==0):
         return jsonify({"message" :"USERNAME CANNOT BE EMPTY"}),200
      if(len(password)<=8):
         return jsonify({"message" :"PASSWORD LENGTH TOO SHORT"}),200
      if(len(password)>=30):
         return jsonify({"message" :"PASSWORD LENGTH TOO LONG"}),200
      if(checkForDigit(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A DIGIT"}),200
      if(checkForUpper(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A UPPER CHARACTER"}),200
      if(checkForLower(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A LOWER CHARACTER"}),200
      if(checkForSpecialChar(str(password)) == False):
         return jsonify({"message" :"PASSWORD MUST CONTAIN A SPECIAL CHARATER"}),200
      if(checkEmailID(str(email_id)) == False):
         return jsonify({"message":"EMAIL ID IS NOT VALID"}),200
      HASHEDPASS = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())   
      mycursor.execute("insert into hassle_free_register (USERNAME,PASSWORD,EMAIL_ID,EMAIL_VERIFICATION) values(%s,%s,%s,%s);",[name,HASHEDPASS.decode('utf-8'),email_id,False]) 
      mycursor.execute("select USER_ID,EMAIL_ID,USERNAME from Hassle_Free_Register where username = %s and password::bytea = %s;",[name,HASHEDPASS]) 
      data = mycursor.fetchone()
      sendEmailVerification(data[0],data[1],data[2])
      mycursor.execute("create table {TABLENAME} (PASSWORD_ID SERIAL NOT NULL PRIMARY KEY,APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255) NOT NULL);".format(TABLENAME = name + "_" + str(data[0])))
      mydb.commit()
      return jsonify({"message":"REGISTERED SUCCESSFULLY"}),201 
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
      return jsonify({"token" : token.decode('utf-8')})
   except TypeError as error:
      print(error)
      return jsonify({"message":"error"}),400
   except ValueError as error:
      print(error)
      return jsonify({"message":"error"}),403
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403

# @auth_blueprint.route('/verifyemail' ,methods =['POST'])
# def register():
#    from app import mycursor,mydb
#    try:
#       HASHEDPASS = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())   
#       mycursor.execute("insert into hassle_free_register (USERNAME,PASSWORD,EMAIL_ID,EMAIL_VERIFICATION) values(%s,%s,%s,%s);",[name,HASHEDPASS.decode('utf-8'),email_id,False]) 
#       mycursor.execute("select USER_ID from Hassle_Free_Register where username = %s and password::bytea = %s;",[name,HASHEDPASS]) 
#       data = mycursor.fetchone()
#       mycursor.execute("create table {TABLENAME} (PASSWORD_ID SERIAL NOT NULL PRIMARY KEY,APP_NAME varchar(255) NOT NULL, APP_USERNAME varchar(255) NOT NULL , APP_PASSWORD varchar(255) NOT NULL);".format(TABLENAME = name + "_" + str(data[0])))
#       mydb.commit()
#       return jsonify({"message":"REGISTERED SUCCESSFULLY"}),201 
#    except TypeError as error:
#       print(error)
#       return jsonify({"message":"error"}),400
#    except ValueError as error:
#       print(error)
#       return jsonify({"message":"error"}),400
#    except psycopg2.Error as error:
#       print(error)
#       if(error.pgcode == str(23505)):
#          mydb.rollback()
#          return jsonify({"message":"USER ALREADY REGISTERED"}),400
#       else:
#          mydb.rollback()
#          return jsonify({"message":"error"}),403