"""
# MAIN CONNECTION API AND STARTING POINT OF BACKGROUND PROCESS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-03
"""

try:
    from flask import Flask, abort, request, jsonify, make_response
    from flask_restful import Api, Resource, request
    import json
    from shutil import rmtree
    from Config.Logger.Logger import Logger
    from Config.Email.EmailService import EmailService
    from Const.const import BACKGROUND_CMD_COMMAND, MAIN_ERROR_LOG, DB_NAME, CURRENT_TIMESTAMP, DB_NAME, USERTB, MAIN_LOG, USER, MAIN
    from werkzeug.utils import secure_filename
    import subprocess
    from Config.Validation.Validation import RegisterValidation
    from Component.User.User import User
    import jwt
    import collections
    from Component.audioExtractor.audioExtractor import Audio_extractor
    from Config.args.args import prepro
    from Component.TextPreprocess.text_preprocess import Text_preprocess
    from Config.Azure_DB_Config.DB_config import Azure_Config
    import datetime
    from passlib.hash import sha256_crypt
    from functools import wraps
    logger = Logger()
    db = Azure_Config(DB_NAME)
except Exception as e:
    from Config.Logger.Logger import Logger
    logger = Logger()
    logger.error_log(MAIN_ERROR_LOG, e)

application = Flask(__name__)
# THIS IS USED TO AUTHENTICATE THE JWT TOKEN THAT IS GENERATED.
application.config["SECRET_KEY"] = '2d39db5c766544a8869a8cd0df37a274'
api = Api(application)

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
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, application.config["SECRET_KEY"], algorithms='HS256')
            sql = """SELECT id, username, role_id, email from {} WHERE id = {}""".format(USERTB, data['id'])
            # db = Azure_Config(DB_NAME)
            current_user_details = db.selectOne(sql)
        except Exception as e:
            return jsonify({"Alert!": "Invalid token"}), 401

        return func(current_user_details, *args, **kwargs)
    return decorated


@application.route('/video/upload_video', methods=['POST'])
@token_required
def uploadVideo(current_user_details):
    if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
    logger = Logger()
    if 'video_file' not in request.files:
        logger.error_log(MAIN_ERROR_LOG, "Upload error.. Empty upload")
        return "Upload error.. Empty upload"
    else:
        try:
            video_file = request.files['video_file']
            lec_name = request.form['lec_name']
            subject_name = request.form['subject']
            description = request.form['description']
            user_id = current_user_details[0]['id']
            username = current_user_details[0]['username']
            destination_email_address = current_user_details[0]['email']
            logger.debug(MAIN, MAIN_LOG, subject_name)
            # lec_id = 1
            # Convert File Name To A Secure File Name
            filename = secure_filename(video_file.filename)
            lec_name = secure_filename(lec_name)
            subject_name = secure_filename(subject_name)
            format = filename.split(".", 1)[1]  # CHECK FILE FORMAT
            if format != "mp4":
                fileFormat = format
            else:
                fileFormat = "mp4"
            audio_extract_obj = Audio_extractor(lec_name, filename, subject_name, description, user_id, username)
            original_video_file_path, lec_id = audio_extract_obj.storeVideo(video_file)  # STORE VIDEO FILE
            # ON WINDOWS use start /min. On Linux nohup

            """
            From this point everything should be run on background
            command = BACKGROUND_CMD_COMMAND + self.path + self.filename + ' ' + self.path + out_file
            subprocess.run(command, shell=True)
            """
            command = "start /min python -u "+ BACKGROUND_CMD_COMMAND + " " + filename + " " + str(fileFormat) + " " + lec_name + " " + destination_email_address + " " + original_video_file_path + " " + subject_name + " " + str(user_id) + " " + description + " " + username + " " + str(lec_id) +" &"
            subprocess.run(command, shell = True)
            print(command)

        except Exception as e:
            logger.error_log(MAIN_ERROR_LOG, e)
            logger.debug(MAIN, MAIN_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    return jsonify({"data": "Dear user you will be notified once video segmentation is done by an email"})


"""GET LECTURE TOPICS"""
@application.route('/video/lectureTopics', methods=['GET'])
@token_required
def lectureTopics(current_user_details):
    try:
        cource_dict = collections.defaultdict(list)
        subject_dict = collections.defaultdict(list)
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        
        sql_lecture = """SELECT DISTINCT Lecture.lecture_name, Lecture.subject_name, Lecture.lec_id, video_segmentation.lec_id, video_segmentation.topic_name, video_segmentation.file_url 
                        FROM Lecture
                        JOIN video_segmentation 
                        ON Lecture.lec_id = video_segmentation.lec_id"""
        output_lecture = db.selectOne(sql_lecture)
        for arr in output_lecture:
            cource_dict["data"].append({"topic_name": arr['topic_name'],
                                              "subject_name": arr['subject_name'],
                                              "cource_name": arr['lecture_name'],
                                              "file_url": arr['file_url']
                                        })
        return jsonify({
            "code": 200,
            "error": 0,
            "data": cource_dict["data"]
        })
        
    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })

@application.route('/email/send', methods=['POST'])
@token_required
def sendEmail(current_user_details):
    try:
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        logger = Logger()
        req = request.get_json()
        message = req['msg']
        subject = req['subject']
        destination_address = req['destination_address']
        EmailService(message, subject, destination_address)
    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })

###################################################################################### USER COMPOENENT ######################################################################################

"""
IF LOGOUT METHOD IS GOING TO BE IMPLEMENTED THEN CREATE A SEPERATE TABLE FOR LOGOUT TOKENS.
WHEN USER IS ACCESSING A SERVICE CHECK FROM THE LOGOUT TABLE WHETHER THAT TOKEN IS AVAILABLE IN THAT TABLE.
"""
@application.route('/logout',methods = ['POST'])
def logout():
    try:
        token = request.headers["x-access-token"]
        data = jwt.decode(token, application.config["SECRET_KEY"], algorithms = 'HS256')
        data['exp'] = datetime.datetime.utcnow()
        return jsonify({
                "error": 0,
                "code": 200,
                "data" : "Logout Successfully"
                })

    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e, MAIN)
        return jsonify({
            "error": 1,
            "code": 500,
            "data" : "{0}".format(e)
            })

"""
GET ALL USERS. THIS METHOD IS ACCESSIBLE ONLY FOR ADMINS ONLY.
"""
@application.route('/user/getAllUsers', methods=['GET'])
@token_required  # CHECK WHETHER USER IS LOGGED IN OTHERWISE THROW AN ERROR
def getAllusers(current_user_details):
    try:
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        sql = "SELECT id, role_id, username, email, name, contact, verified, time_logged_in, created_user, updated_user, created_date, updated_date FROM User WHERE verified = 'NO'"
        # db = Azure_Config(DB_NAME)
        response = db.getAll(sql)
        user_details_dict = collections.defaultdict(list)
        for arr in response:
            user_details_dict["data"].append({"id": arr['id'],
                                              "role_id": arr['role_id'],
                                              "username": arr['username'],
                                              "email": arr['email'],
                                              "name": arr['name'],
                                              "contact": arr['contact'],
                                              "verified": arr['verified'],
                                              "time_logged_in": arr['time_logged_in'],
                                              "created_user": arr['created_user'],
                                              "created_date": arr['created_date'],
                                              })

        return jsonify({
            "code": 200,
            "error": 0,
            "data": user_details_dict["data"]
        })

    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })

"""GET TOPICS for EACH LECTURE"""
@application.route('/user/lectureCourse', methods=['GET'])
@token_required
def lectureCourse(current_user_details):
    try:
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        
        lecturer_id = current_user_details[0]['id']
        cource_dict = collections.defaultdict(list)
        sql_lecture = """SELECT subject_name, lecture_name FROM lecture where user_id = {}""".format(lecturer_id)
        output_lecture = db.selectOne(sql_lecture)
        for arr in output_lecture:
            cource_dict[arr['lecture_name']].append({"subject_name": arr['subject_name']})
            
        return jsonify({
            "code": 200,
            "error": 0,
            "data": cource_dict
        })
        
    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })


"""
UPDATE VERIFICATION INFORMATION OF REGISTERED USERS
"""
@application.route('/user/updateVerification', methods=['POST'])
@token_required
def updateVerification(current_user_details):
    try:
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        req = request.get_json()
        user_id = req['id']
        verified_status = req['verified']
        admin_user = current_user_details[0]['username']
        # db = Azure_Config(DB_NAME)
        sql = "UPDATE User SET verified = '{}' , updated_user = '{}' , updated_date = {} where id = {}".format(verified_status, admin_user, CURRENT_TIMESTAMP, user_id)
        print(sql)
        db.Update(sql)
        return jsonify({
            "code": 200,
            "error": 0,
            "data": "Update Successful"
        })
    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })
        
        
"""
DELETE VERIFICATION INFORMATION OF REGISTERED USERS
"""
@application.route('/user/deleteVerification', methods=['POST'])
@token_required
def deleteVerification(current_user_details):
    try:
        if not current_user_details[0]['role_id'] == 10:
            return "Trespassing web page. This is acessible only to admins."
        req = request.get_json()
        user_id = req['id']
        sql = "DELETE FROM User WHERE id = {}".format(user_id)
        db.Update(sql)
        return jsonify({
            "code": 200,
            "error": 0,
            "data": "Delete Successful"
        })
    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
        })
    
"""
REGISTER USER. THIS SERVICE IS USED TO REGISTER USERS TO CREATE MY COURCE WEB APPLICATION
"""
@application.route('/user/register', methods=['POST'])
def register():
    try:
        form = RegisterValidation(request.form)
        if form.validate():
            name = form.name.data
            username = form.username.data
            email = form.email.data
            contact = form.contact.data
            role = form.role.data
            password = sha256_crypt.hash(str(form.password.data))
            user = User(username, password)
            response = user.register_user(username, email, name, contact, role)
            return jsonify({
                "code": 200,
                "error": 0,
                "data": "Register Successful"
            })
        return jsonify({
            "status": 1,
            "code": 500,
            "data": "Validation Error"
        })

    except Exception as e:
        logger.error_log(MAIN_ERROR_LOG, e)
        logger.debug(MAIN, MAIN_LOG, e)
        return jsonify({
            "error": 1,
            "code": 500,
            "data": "{0}".format(e)
            })

"""
LOGIN. THIS SERVICE IS USED TO LOG IN USERS TO THE APPLICATION.
IT WILL GIVE A UNIQUE TOKEN TO USERS WITH A PAYLOAD OF USER DETAILS.
"""
@application.route('/user/login', methods=['POST'])
def login():
        try:
            username = request.form['username']
            password = request.form['password']
            user = User(username, password)
            res = user.verify_user()
            if res:
                if sha256_crypt.verify(password, str(res['password'])) and res['verified'] == "YES":
                    print(username)
                    token = jwt.encode({
                        'username': username,
                        'id': res['id'],
                        'role_id': res['role_id'],
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=10)
                    },
                        application.config["SECRET_KEY"], algorithm='HS256')

                    # now = datetime.datetime.now()
                    sql = "UPDATE User SET time_logged_in = {} where id = {}".format(CURRENT_TIMESTAMP, res['id'])
                    db.Update(sql)
                    return jsonify({'token': token})
                else:
                    return make_response("User Not Authenticated", 403, {'WWW-Authenticate': 'Basic realm="Login Required"'})

        except Exception as e:
            logger.error_log(MAIN_ERROR_LOG, e)
            logger.debug(MAIN, MAIN_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

if __name__ == "__main__":
    application.run(debug=True)
