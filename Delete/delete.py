from flask import render_template, request , jsonify , blueprints
import jwt
from Auth.authhelper import check_for_token_email
import bcrypt
from Auth.e_mailhelp import sendDeleteAccountVerification
import psycopg2


delete_blueprint = blueprints.Blueprint('delete_blueprint',__name__)

@delete_blueprint.route('/deletepass' ,methods =['DELETE'])
@check_for_token_email
def deletepasswords():
   from app import mycursor,mydb,SECRET_PASSWORD,psycopg2
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
      # mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
      # fetchData = mycursor.fetchall()
      return jsonify({"message":"DELETE SUCCESSFULLY"}),200
   except psycopg2.Error as error:
      print(error)
      return jsonify({"message":"error"}),403 
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}),404   



@delete_blueprint.route('/deleteaccount' ,methods =['GET'])
def deleteaccount():
   from app import mycursor,mydb,SECRET_JWT_KEY,psycopg2
   args = request.args
   token = args.get('t')
   if not token:
      return jsonify({"message":"TOKEN MISSING"}),400
   try:
      tokendata = jwt.decode(token,SECRET_JWT_KEY,algorithms="HS256")
      mycursor.execute("select EMAIL_VERIFICATION,USER_ID from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = tokendata['username']))
      DATA = mycursor.fetchone()
      if(DATA[0]==True):
         mycursor.execute("delete from hassle_free_register where username = '{USER_NAME}';".format(USER_NAME = tokendata['username']))
         mycursor.execute("drop table {TABLENAME};".format(TABLENAME = tokendata['username'] + "_" + str(DATA[1])))
         mydb.commit()
         return render_template('deletesuccess.html'),201
      else:
         return render_template('emailnotverified.html'),200
   except psycopg2.Error as error:
      print(error)
      return render_template('error.html'),403
   except Exception as error:
      return str(error)
   except:
      return render_template('error.html'),403



@delete_blueprint.route('/delaccemail' ,methods =['POST'])
def sendDelAccEmail():
    from app import mycursor
    try:
        name = request.form['USER_NAME']
        password = request.form['USER_PASSWORD']
        if(len(name)==0):
            return jsonify({"message":"USERNAME CANNOT BE EMPTY"})
        if(len(password)==0):
            return jsonify({"message":"PASSWORD CANNOT BE EMPTY"})

        mycursor.execute("select USER_ID,EMAIL_VERIFICATION from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = name))
        data = mycursor.fetchone()
        
        # generation of token 
        if data :
           if data[1]==True:
               mycursor.execute("select PASSWORD from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = name))
               hashed_pass = mycursor.fetchone()
               if bcrypt.checkpw(password.encode('utf-8'),str(hashed_pass[0]).encode('utf-8')):
                  mycursor.execute("select USER_ID,EMAIL_ID,USERNAME from Hassle_Free_Register where username = %s",[name]) 
                  data = mycursor.fetchone()
                  sendDeleteAccountVerification(data[1],data[2])
               else:
                  return jsonify({"message":"INVALID CREDENTIALS"}),200
           else:
                return jsonify({"message":"ACCOUNT NOT VERIFIED"}),200
        else:
            return jsonify({"message":"USER DOES NOT EXIST"}),401
        return jsonify({"message" : "EMAIL SUCCESSFULLY SENT"}),201
    except TypeError as error:
        print(error)
        return jsonify({"message":"error"}),400
    except ValueError as error:
        print(error)
        return jsonify({"message":"error"}),403
    except psycopg2.Error as error:
        print(error)
        return jsonify({"message":"error"}),403
    except Exception as error:
        print(error)
        return jsonify({"message":"error"}),403