from flask import request , jsonify , blueprints
import bcrypt
from Auth.emailhelper import sendEmailVerification
import psycopg2


email_blueprint = blueprints.Blueprint('email_blueprint', __name__)

@email_blueprint.route('/resendemail' ,methods =['POST'])
def resendEmail():
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
                mycursor.execute("select USER_ID,EMAIL_ID,USERNAME from Hassle_Free_Register where username = %s",[name]) 
                data = mycursor.fetchone()
                sendEmailVerification(data[1],data[2])
            else:
                return jsonify({"message":"INVALID CREDENTIALS"}),200
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
        