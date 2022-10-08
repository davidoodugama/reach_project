"""
# AZURE BLOB CONFIGURATIONS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Sep-28
"""

from Const.const import (FILE_NOT_EXIST, ORIGINAL, SEGMENT, DB_NAME, STORAGE_ACCOUNT_KEY, STORAGE_ACCOUNT_NAME, CONNECTION_STRING, CONTAINER_NAME,
                         AZURE_BLOB_ERROR_LOG_FILE, AZURE_BLOB_ERROR_LOG_FILE, AZURE_BLOB, AZURE_BLOB_LOG, FILE_URL)
from flask import jsonify
from Config.Azure_DB_Config.DB_config import Azure_Config
import subprocess
from werkzeug.utils import secure_filename
from datetime import date
import time
from Config.Logger.Logger import Logger
import os
from azure.storage.filedatalake import DataLakeServiceClient
# from azure.core._match_conditions import MatchConditions
# from azure.storage.filedatalake._models import ContentSettings
# from azure.storage.blob import BlobServiceClient, BlobType, StandardBlobTier, BlobClient

# import boto3 BlobType
# from boto3.s3.transfer import TransferConfig
# from Config.RDS_Config.DB_Config import Rds_Config
# from botocore.client import Config


class Blob_config:
    def __init__(self, lec_name, subject_name):
        try:
            self.debug = Logger()
            # self.lec_id = lec_id
            # self.db = Rds_Config(DB_NAME)
            self.db = Azure_Config(DB_NAME)
            # self.service_name = S3
            # self.region_name = REGION
            # self.aws_access_key_id = ACCESS_KEY
            # self.aws_secret_access_key = SECRET_KEY

            """ AZURE BLOB CONFIGURATIONS """
            self.storage_account_key = STORAGE_ACCOUNT_KEY
            self.storage_account_name = STORAGE_ACCOUNT_NAME
            self.connection_string = CONNECTION_STRING
            self.container_name = CONTAINER_NAME
            self.lec_name = lec_name
            """ AZURE BLOB CONFIGURATIONS """
            self.current_date = date.today()
            self.subject_name = subject_name
            self.blob_main_video_directory = self.subject_name + "/" + self.lec_name
            self.con()
            self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "Started|azure blob Connection success")

        except Exception as e:
            self.debug.error_log(AZURE_BLOB_ERROR_LOG_FILE, e, AZURE_BLOB)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def con(self):
        try:
            '''# self.s3_1 = boto3.resource(
            #             service_name = self.service_name,
            #             region_name = self.region_name,
            #             aws_access_key_id = self.aws_access_key_id,
            #             aws_secret_access_key = self.aws_secret_access_key,
            #             # config = self.s3_config
            #         )'''
            # self.s3_2 = boto3.client(
            #     service_name=self.service_name,
            #     region_name=self.region_name,
            #     aws_access_key_id=self.aws_access_key_id,
            #     aws_secret_access_key=self.aws_secret_access_key,
            #     # config = self.s3_config
            # )
            # self.blob_service_client = BlobClient.from_connection_string(
            #     self.connection_string)
            self.service_client = DataLakeServiceClient(account_url="https://{}.dfs.core.windows.net".format(self.storage_account_name), credential="sp=racwdlmeop&st=2022-10-01T06:08:40Z&se=2023-01-01T14:08:40Z&sv=2021-06-08&sr=c&sig=0VMKh%2FLxdazU9%2Bf2J5Wn5578iNp0D6WW2g%2FVnWog7Ys%3D")
            self.file_system_client = self.service_client.get_file_system_client(self.container_name)

        except Exception as e:
            self.debug.error_log(AZURE_BLOB_ERROR_LOG_FILE, e, AZURE_BLOB)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def upload_video(self, path, type, lec_id = None):
        try:
            if type == ORIGINAL:
                file_name = os.path.basename(path)  
                self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, file_name)
                file_url = self.blob_upload(path, type)
                self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "upload_video|Video file name: " + file_name + " uploaded to BLOB. Full file path: " + file_url)
                return file_url

            elif type == SEGMENT:
                self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "paths: ")
                self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, os.listdir(path))
                for path in os.listdir(path):
                    path = secure_filename(path)
                    path = "segments/" + self.subject_name + "/" + lec_id + "_" + self.lec_name + "/" + path
                    self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "path :" + str(path))
                    
                    file_name = os.path.basename(path) 
                    self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "fileName : " + str(file_name)) 
                    
                    file_url = self.blob_upload(path, type)
                    sql = """INSERT INTO video_segmentation(lec_id, topic_name, file_url) values({}, '{}', '{}')""".format(lec_id, file_name, file_url)
                    self.db.insert(sql)

                    self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "upload_video|Video file name: " + file_name + " uploaded to AZURE BLOB. Full file path: " + file_url)

        except Exception as e:
            self.debug.error_log(AZURE_BLOB_ERROR_LOG_FILE, e, AZURE_BLOB)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    def blob_upload(self, path, type):
        try:
            self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, "Uploading to blob in progress..")
            file_name = os.path.basename(path)
            self.file_system_client.create_directory(self.subject_name)
            self.file_system_client.create_directory(self.blob_main_video_directory)
            self.file_system_client.create_directory(self.blob_main_video_directory + "/" + type)
            self.debug.debug(AZURE_BLOB, AZURE_BLOB_LOG, self.blob_main_video_directory + "/" + type)
            self.file_system_client = self.service_client.get_file_system_client(file_system=self.container_name)
            directory_client = self.file_system_client.get_directory_client(self.blob_main_video_directory + "/" + type)
            
            file_client = directory_client.get_file_client(file_name)
            local_size = os.path.getsize(path)
            print("uploading in progress....")
            with open(path,'rb') as local_file:
                file_client.upload_data(data=local_file, overwrite=True, length=local_size)
            
            return FILE_URL + self.blob_main_video_directory + "/" + type + "/" + file_name

        except Exception as e:
            self.debug.error_log(AZURE_BLOB_ERROR_LOG_FILE, e, AZURE_BLOB)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })
