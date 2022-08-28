"""
# VALIDATING REQUEST OBJECTS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-July-25
"""


from flask_restful import Api, Resource, request
from flask import Flask, request, jsonify, make_response
from Validation.Validation import RegisterValidation
from Const.const import USERTB, USERDB, CURRENT_TIMESTAMP, MAIN, MAIN_ERROR_LOG
from passlib.hash import sha256_crypt
from Component.User import User
import jwt
from Config.RDS_Config.DB_Config import Rds_Config
import datetime
from functools import wraps
import collections
from Config.Logger.Logger import Logger

application = Flask(__name__)
api = Api(application)
application.config["SECRET_KEY"] = '2d39db5c766544a8869a8cd0df37a274' # THIS IS USED TO AUTHENTICATE THE JWT TOKEN THAT IS GENERATED.
debug = Logger()

"""
TOKEN_REQUIRED. THIS WRAPPER IS USED TO CHECK WHETHER USER IS LOGGED IN CURRETNLY BY CHECKING THE TOKEN.
"""
def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers["x-access-token"]
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        try:
            data = jwt.decode(token, application.config["SECRET_KEY"], algorithms = 'HS256')
            sql = """SELECT username, role_id from {} WHERE id = {}""".format(USERTB, data['id'])
            db = Rds_Config(USERDB)
            current_user_details = db.selectOne(sql)
        except Exception as e:
            return jsonify({"Alert!": "Invalid token"}), 401
        
        return func(current_user_details, *args, **kwargs)
    return decorated

"""
IF LOGOUT METHOD IS GOING TO BE IMPLEMENTED THEN CREATE A SEPERATE TABLE FOR LOGOUT TOKENS.
WHEN USER IS ACCESSING A SERVICE CHECK FROM THE LOGOUT TABLE WHETHER THAT TOKEN IS AVAILABLE IN THAT TABLE.
"""
# @application.route('/logout',methods = ['POST'])
# def logout():
#     try:
#         token = request.headers["x-access-token"]
#         data = jwt.decode(token, application.config["SECRET_KEY"], algorithms = 'HS256')
#         data['exp'] = datetime.datetime.utcnow()
#         return jsonify({
#                 "error": 0,
#                 "code": 200,
#                 "data" : "Logout Successfully"
#                 })
    
#     except Exception as e:
#         debug.error_log(MAIN_ERROR_LOG, e, MAIN)
#         return jsonify({
#             "error": 1,
#             "code": 500,
#             "data" : "{0}".format(e)
#             })

"""
GET ALL USERS. THIS METHOD IS ACCESSIBLE ONLY FOR ADMINS ONLY.
"""
@application.route('/all-users', methods = ['GET'])    
@token_required # CHECK WHETHER USER IS LOGGED IN OTHERWISE THROW AN ERROR 
def getAllusers(current_user_details):
    try:
        if not current_user_details['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        sql = "SELECT * FROM User"
        db = Rds_Config(USERDB)
        response = db.selectAll(sql)
        user_details_dict = collections.defaultdict(list)
        for arr in response:
            user_details_dict["data"].append({"id": arr['id'],
                                                "role_id": arr['role_id'],
                                                "username": arr['username'],
                                                "password": arr['password'],
                                                "email": arr['email'],
                                                "name": arr['name'],
                                                "contact": arr['contact'],
                                                "verified": arr['verified'],
                                                "time_logged_in": arr['time_logged_in'],
                                                "created_user": arr['created_user'],
                                                "created_date": arr['created_date'],
                                                })
        
        return jsonify({
            "code" : 200,
            "error" : 0,
            "data" : user_details_dict["data"]
        })

    except Exception as e:
        debug.error_log(MAIN_ERROR_LOG, e, MAIN)
        return jsonify({
            "error": 1,
            "code": 500,
            "data" : "{0}".format(e)
            })

"""
REGISTER USER. THIS SERVICE IS USED TO REGISTER USERS TO CREATE MY COURCE WEB APPLICATION
"""
class Register(Resource):
    def post(self):
        try:
            print("im here")
            print(request.from_values())
            form = RegisterValidation(request.get_json())
            if form.validate():
                name = form.name.data
                username = form.username.data
                email = form.email.data
                contact = form.contact.data
                role = form.role.data
                password = sha256_crypt.hash(str(form.password.data))
                user = User(username, password)
                response = user.register_user(username, email, name, contact, role)
                return response
            return jsonify({
                "status": 1,
                "code": 500,
                "data" : "Validation Error"
                })

        except Exception as e:
            print(e)
            debug.error_log(MAIN_ERROR_LOG, e, MAIN)
            return jsonify({
                "status": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

"""
LOGIN. THIS SERVICE IS USED TO LOG IN USERS TO THE APPLICATION.
IT WILL GIVE A UNIQUE TOKEN TO USERS WITH A PAYLOAD OF USER DETAILS.
"""
class Login(Resource):
    def post(self):
        try:
            username = request.form['username']
            password = request.form['password']
            user = User(username, password)
            res = user.verify_user()
            if res:
                if sha256_crypt.verify(password, str(res['password'])) and res['verified'] == "YES":
                    token = jwt.encode({
                        'username' : username,
                        'id' : res['id'],
                        'role_id' : res['role_id'],
                        'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=10)
                    },
                    application.config["SECRET_KEY"], algorithm = 'HS256')
                    db = Rds_Config(USERDB)
                    # now = datetime.datetime.now()
                    sql = "UPDATE User SET time_logged_in = {} where id = {}".format(CURRENT_TIMESTAMP, res['id'])
                    db.update(sql)
                    return jsonify({'token': token})
                else:
                    return make_response("User Not Authenticated", 403, {'WWW-Authenticate' : 'Basic realm="Login Required"'})

        except Exception as e:
            debug.error_log(MAIN_ERROR_LOG, e, MAIN)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

api.add_resource(Login,"/login")
api.add_resource(Register,"/register")

if __name__ == "__main__":
    application.run(debug = True)