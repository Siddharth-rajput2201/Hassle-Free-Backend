from flask import request , jsonify , blueprints
import jwt
from Auth.authhelper import check_for_token_email

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



@delete_blueprint.route('/deleteaccount' ,methods =['DELETE'])
@check_for_token_email
def deleteaccount():
   from app import mycursor,mydb,SECRET_PASSWORD,psycopg2
   try:
      TOKEN = request.form["JWT_TOKEN"]
      if not TOKEN:
         return jsonify({'message':'Missing Token'}),400
      data =  jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
      print(data['user_id'])
      print(data['username'])
      return("OK")
   except Exception as error:
      print(error)
      return jsonify({"message":"error"}),404 
   #    PASSWORD_ID = request.form["PASSWORD_ID"]
   #    if not PASSWORD_ID:
   #       return jsonify({'message':'Missing Password ID'}),400
   #    mycursor.execute("delete from {TABLENAME} where PASSWORD_ID = '{PASSWORDID}';".format(TABLENAME = data['username'] + "_" + str(data["user_id"]),PASSWORDID=PASSWORD_ID))
   #    mydb.commit()
   #    # mycursor.execute("select * from {TABLENAME};".format(TABLENAME = data['username'] + "_" + str(data['user_id'])))
   #    # fetchData = mycursor.fetchall()
   #    return jsonify({"message":"DELETE SUCCESSFULLY"}),200
   # except Exception as error:
   #    print(error)
   #    return jsonify({"message":"error"}),404   
   # except psycopg2.Error as error:
   #    print(error)
   #    return jsonify({"message":"error"}),403 