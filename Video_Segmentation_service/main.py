"""
# MAIN CONNECTION API AND STARTING POINT OF BACKGROUND PROCESS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-03
"""

try:
    from flask import Flask, abort, request, jsonify
    from flask_restful import Api, Resource, request
    import json
    from shutil import rmtree
    from Config.Logger.Logger import Logger
    from Config.Email.EmailService import EmailService
    from Const.const import BACKGROUND_CMD_COMMAND, MAIN_ERROR_LOG
    from werkzeug.utils import secure_filename
    import subprocess
    from Component.audioExtractor.audioExtractor import Audio_extractor
    from Config.args.args import prepro
    from Component.TextPreprocess.text_preprocess import Text_preprocess
    # from Config.RDS_Config.DB_Config import Rds_Config
    # rds = Rds_Config()
    # res = rds.cursor
except Exception as e:
    from Config.Logger.Logger import Logger
    logger = Logger()
    logger.error_log(MAIN_ERROR_LOG, e)
# from Config.Aws.DB_Config import cursor

application = Flask(__name__)
api = Api(application)

class Video(Resource):
    def post(self):
        logger = Logger()
        if 'video_file' not in request.files:
            logger.error_log(MAIN_ERROR_LOG, "Upload error.. Empty upload")
            return "Upload error.. Empty upload"
        else:
            try:
                video_file = request.files['video_file']
                lec_name = request.form['lec_name']
                destination_email_address = request.form['email_address']
                subject_name = request.form['subject']
                lec_id = 1
                filename = secure_filename(video_file.filename) # Convert File Name To A Secure File Name 
                lec_name = secure_filename(lec_name)
                subject_name = secure_filename(subject_name)
                format = filename.split(".", 1)[1] # CHECK FILE FORMAT
                if format != "mp4":
                    fileFormat = format
                else:
                    fileFormat = False
                
                audio_extract_obj = Audio_extractor(lec_id, lec_name, filename, subject_name)
                original_video_file_path = audio_extract_obj.storeVideo(video_file) # STORE VIDEO FILE  
                # ON WINDOWS use start /min. On Linux nohup
                
                """
                From this point everything should be run on background
                command = BACKGROUND_CMD_COMMAND + self.path + self.filename + ' ' + self.path + out_file
                subprocess.run(command, shell=True)
                """
                command = "start /min python -u "+ BACKGROUND_CMD_COMMAND + " " + filename + " " + fileFormat + " " + lec_name + " " + str(lec_id) + " " + destination_email_address + " " + original_video_file_path + " " + subject_name + " &"
                subprocess.run(command, shell = False)

            except Exception as e:
                logger.error_log(MAIN_ERROR_LOG, e)
                return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

        return jsonify({"data" : "Dear user you will be notified once video segmentation is done by an email"})
    
class ConvertToMp4(Resource):
    def post(self):
        try:
            logger = Logger()
            req_data = request.get_json()
            filename = req_data['filename']
            lec_name = req_data['lec_name']
            lec_id = req_data['lec_id']
            audioE = Audio_extractor(lec_id, lec_name, filename)  
            out_file_name = audioE.convertVideoToMp4()
            return jsonify({
                "error": 0,
                "code": 200,
                "data" : {
                "data": out_file_name,
            }})
        except Exception as e:
            logger.error_log(MAIN_ERROR_LOG, e)

class SendEmail(Resource):
    def post(self):
        try:
            logger = Logger()
            req = request.get_json()
            message = req['msg']
            subject = req['subject']
            destination_address = req['destination_address']
            EmailService(message, subject, destination_address)
        except Exception as e:
            logger.error_log(MAIN_ERROR_LOG, e)
            
class CleanAudio(Resource):
    def post(self):
        try:
            logger = Logger()
            req_data = request.get_json()
            filename = req_data['filename']
            lec_name = req_data['lec_name']
            lec_id = req_data['lec_id']
            audioE = Audio_extractor(lec_id, lec_name, filename)  
            path = audioE.clean_audio()
            rmtree(path)
            jsonify(path)
            
        except OSError as e:
            logger.error_log(MAIN_ERROR_LOG, "Error: %s - %s." % (e.filename, e.strerror))
        except Exception as e:
            logger.error_log(MAIN_ERROR_LOG, e)

class Preprocess_text(Resource):
    def post(self):
        args = prepro.parse_args()
        lec_id = args['lec_id']
        lec_name = args['lec_name']
        lec_name = lec_name.replace(" ", "_")
        preprocess = Text_preprocess(lec_id, lec_name)
        preprocess.train_lda_model()
        lda_file_path = preprocess.lda_topic_preprocess()
        keyword_file_path = preprocess.keyword_extraction()
        if keyword_file_path and lda_file_path:
            return jsonify({
                "error": 0,
                "data" : {
                "keyword_path": keyword_file_path,
                "lda_file_path": lda_file_path
            }})
        else:
            return jsonify({
                "error": 500,
                "data" : "path not available"})

api.add_resource(Preprocess_text, "/preprocess_text")
api.add_resource(Video, "/extract_audio")
api.add_resource(ConvertToMp4, "/convertToMp4")
api.add_resource(CleanAudio, "/cleanAudio")

if __name__ == "__main__":
    application.run(debug = True)