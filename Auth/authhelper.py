import re
import jwt
from flask import request ,jsonify
from functools import wraps

def checkForDigit(inputString):
    return any(char.isdigit() for char in inputString)

def checkForUpper(inputString):
    return any(char.isupper() for char in inputString)

def checkForLower(inputString):
    return any(char.islower() for char in inputString)

def checkForSpecialChar(inputString):

    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if(regex.search(inputString) == None):
        return False
         
    else:
        return True

def checkEmailID(inputString):
    regex = re.compile('[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}')
    if(re.fullmatch(regex, inputString)):
        return True
    else:
        return False

def check_for_token_email(func):
   @wraps(func)
   def wrapped():
      from app import SECRET_PASSWORD,mycursor
      TOKEN = request.form['JWT_TOKEN']
      if not TOKEN:
         return jsonify({'message':'MISSING TOKEN'}),400
      try:
         data = jwt.decode(TOKEN,SECRET_PASSWORD,algorithms="HS256")
         mycursor.execute("select EMAIL_VERIFICATION from Hassle_Free_Register where USERNAME = '{USER_NAME}';".format(USER_NAME = data['username']))
         STATUS = mycursor.fetchone()
         if(STATUS[0]==False):
             return jsonify({"message":"EMAIL NOT VERIFIED"}),403
      except:
         return jsonify({"message":"UNAUTHORIZED"}),403
      return func()
   return wrapped
