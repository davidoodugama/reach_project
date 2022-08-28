"""
# S3 BUCKET CONFIGURATIONS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-07
"""

import os
import boto3
from Const.const import S3, S3_ERROR_LOG, S3_LOG, BUCKET_NAME, FILE_URL, FILE_NOT_EXIST, REGION, ACCESS_KEY, SECRET_KEY, S3_UPLOAD_FILE_URL_FORMAT, ORIGINAL, SEGMENT, DB_NAME
from Config.Logger.Logger import Logger
# from boto3.s3.transfer import TransferConfig
import time
from datetime import date
from werkzeug.utils import secure_filename
import os
import subprocess
from Config.RDS_Config.DB_Config import Rds_Config
# from botocore.client import Config
from flask import jsonify

class S3_Config:
    def __init__(self, lec_id, lec_name, subject_name):
        try:
            self.debug = Logger()
            self.lec_id = lec_id
            self.db = Rds_Config(DB_NAME)
            # self.config = TransferConfig(multipart_threshold = 1024*2, max_concurrency = 15,
            #             multipart_chunksize = 1024*2, use_threads = True)
            # self.s3_config = Config(connect_timeout = 3600, retries = {'max_attempts': 0})
            self.service_name = S3
            self.region_name = REGION
            self.aws_access_key_id = ACCESS_KEY
            self.aws_secret_access_key = SECRET_KEY
            self.current_date = date.today()
            self.subject_name = subject_name
            self.s3_main_video_directory = self.subject_name + \
                "/" + str(self.lec_id) + "." + lec_name
            # self.s3_main_video_directory = str(self.current_date) + '/' + self.subject_name + "/" + str(lec_id) + "." + lec_name
            self.con()
            self.debug.debug(
                S3, S3_LOG, "Started|s3_1, s3_2 Connection success")

        except Exception as e:
            self.debug.error_log(S3_ERROR_LOG, e, S3)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def con(self):
        try:
            # self.s3_1 = boto3.resource(
            #             service_name = self.service_name,
            #             region_name = self.region_name,
            #             aws_access_key_id = self.aws_access_key_id,
            #             aws_secret_access_key = self.aws_secret_access_key,
            #             # config = self.s3_config
            #         )
            self.s3_2 = boto3.client(
                service_name=self.service_name,
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                # config = self.s3_config
            )
        except Exception as e:
            self.debug.error_log(S3_ERROR_LOG, e, S3)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def upload_video(self, path, type):
        try:
            if type == ORIGINAL:
                # file_name = os.path.basename(path)
                # s3_file_upload_path = secure_filename(self.s3_main_video_directory + "/" + file_name + "/" + ORIGINAL)
                file_name = self.s3_upload(path, type)
                s3_path = FILE_URL + self.s3_main_video_directory + '/' + file_name
                self.debug.debug(S3, S3_LOG, "upload_video|Video file name: " +
                                 file_name + " uploaded to S3. Full file path: " + s3_path)

            elif type == SEGMENT:
                for path in os.listdir(path):
                    file_name = self.s3_upload(path, type)
                    s3_path = FILE_URL + self.s3_main_video_directory + '/segment/' + file_name
                    sql = """INSERT INTO video_segmentation(lec_id, topic_name, s3_url) values({}, '{}', '{}', '{}')""".format(
                        self.lec_id, file_name, s3_path)
                    self.db.insert(sql)
                    self.debug.debug(S3, S3_LOG, "upload_video|Video file name: " +
                                     file_name + " uploaded to S3. Full file path: " + s3_path)

            # s3_file_upload_path = secure_filename(self.s3_main_video_directory + "/" + file_name + "/" + SEGMENT)
            # print("Uploading progess... " + s3_file_upload_path)
            # command = "aws s3 cp " + path +  " "+ S3_UPLOAD_FILE_URL_FORMAT + s3_file_upload_path
            # subprocess.run(command, shell = True)
            # print("Uploading Complete. Uploaded to " + self.s3_main_video_directory + "/" + file_name)

            # if os.path.exists(path):
            #     os.remove(path)
            # else:
            #     print(FILE_NOT_EXIST + str(path))

        except Exception as e:
            self.debug.error_log(S3_ERROR_LOG, e, S3)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def s3_upload(self, path, type):
        try:
            file_name = os.path.basename(path)
            s3_file_upload_path = secure_filename(
                self.s3_main_video_directory + f"/{type}/" + file_name)
            print("Uploading in progess... " + s3_file_upload_path)
            command = "aws s3 cp " + path + " " + \
                S3_UPLOAD_FILE_URL_FORMAT + s3_file_upload_path
            subprocess.run(command, shell=True)
            print("Uploading Complete. Uploaded to " +
                  self.s3_main_video_directory + "/" + file_name)

            return file_name

        except Exception as e:
            self.debug.error_log(S3_ERROR_LOG, e, S3)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })
