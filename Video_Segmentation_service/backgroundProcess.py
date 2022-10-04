"""
# BACKGROUND PROCESS AND VIDEO SEGMENTATION MODULE
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-05
"""

import requests
import sys
import json
from shutil import rmtree
from Component.audioExtractor.audioExtractor import Audio_extractor
from Component.TextPreprocess.text_preprocess import Text_preprocess
from Config.Logger.Logger import Logger
from Component.VideoSegmentation.video_segmentation import VideoSegmentation
from Const.const import (BACK_GROUND_FILE_PROCESS_ERROR_LOG, BACK_GROUND_FILE_PROCESS_LOG, BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_ERROR_LOG, BACKGROUND_PROCESS, 
                        ORIGINAL, SEGMENT, SUCCESS_EMAIL_BODY, EMAIL_SUBJECT, DB_NAME)
from Config.Email.EmailService import EmailService
# from Config.S3_Config.S3_Config import S3_Config
from Config.Blob_Config.Blob_Config import Blob_config
from Config.Azure_DB_Config.DB_config import Azure_Config

def audioPreprocess(lec_name, filename, fileFormat, subject_name, description, user_id, username):
    try:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "audioPreprocess|" + "upload_video|in progress")
        audioE = Audio_extractor(lec_name, filename, subject_name, description, user_id, username)  
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, filename + " " + fileFormat)
        if fileFormat != 'mp4':
            audioE.convertVideoToMp4()
        main_path, clean_audio_video_file_path = audioE.extract_clean_audio()
        return main_path, clean_audio_video_file_path

    except Exception as e:
        # logger.error_log(BACK_GROUND_FILE_PROCESS_ERROR_LOG, e, BACKGROUND_PROCESS)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)

def textPreprocess(lec_id, lec_name):
    try:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "textPreprocess|" + "upload_video|in progress")
        lec_name = lec_name.replace(" ", "_")
        text_preprocess_obj = Text_preprocess(lec_id, lec_name)
        text_preprocess_obj.train_lda_model()
        lda_file_path = text_preprocess_obj.lda_topic_preprocess()
        keyword_file_path = text_preprocess_obj.keyword_extraction()
        return lda_file_path, keyword_file_path

    except Exception as e:
        # logger.error_log(BACK_GROUND_FILE_PROCESS_ERROR_LOG, e, BACKGROUND_PROCESS)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)
        return False

def videoSegmentation(lda_topic_list, key_token, lec_name, lec_id, video_file_path, subject_name):
    try:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "videoSegmentation|" + "upload_video|in progress")
        video_segment_obj = VideoSegmentation(lda_topic_list, key_token, lec_name, lec_id, video_file_path, subject_name)
        video_segment_obj.change_fps_of_video()
        response = video_segment_obj.extract_videoFrame()
        if response:
            lecture_segmentation_folder_path, remove_segment_folder_path = video_segment_obj.segment_video()
            return lecture_segmentation_folder_path, remove_segment_folder_path

    except Exception as e:
        # logger.error_log(BACK_GROUND_FILE_PROCESS_ERROR_LOG, e, BACKGROUND_PROCESS)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)
        return False

def upload_video(lec_name, subject_name, video_file_path, type, lec_id = None):
    try:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "upload_video|in progress")
        blob = Blob_config(lec_name, subject_name)
        blob_file_url = blob.upload_video(video_file_path, type, lec_id) # UPLOADING ORIGINAL FILE TO S3 
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "upload_video|finished")
        return blob_file_url
    except Exception as e:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)

def sql_query_for_original_video(original_saved_path, lec_id):
    try:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "sql_query_for_original_video|in progress")
        db = Azure_Config(DB_NAME)
        sql = '''UPDATE Lecture SET original_lecture_path = '{}' where id = {}'''.format(original_saved_path, lec_id)
        db.insert(sql)
        # sql_select = "select lec_id from Lecture where subject_name = '{}' and lecture_name = '{}'".format(subject_name, lec_name)
        # out_put_query = db.selectOne(sql_select)
        # lec_id = out_put_query['lec_id']
        return True
    
    except Exception as e:
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)

def main():
    try:
        filename = sys.argv[1]
        fileFormat = sys.argv[2]
        lec_name = sys.argv[3]
        destination_email_address = sys.argv[4]
        original_video_file_path = sys.argv[5]
        subject_name = sys.argv[6]
        user_id = sys.argv[7]
        description = sys.argv[8]
        username = sys.argv[9]
        lec_id = sys.argv[10]
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "main|" + filename + " " + lec_name + " " + lec_id)
        # s3_obj = S3_Config(lec_id, lec_name, subject_name)
        
        blob_file_url = upload_video(lec_name, subject_name, original_video_file_path, ORIGINAL, lec_id) # STORE ORIGINAL VIDEO TO BLOB
        sql_query_for_original_video(blob_file_url, lec_id)
        
        main_path, clean_audio_video_file_path = audioPreprocess(lec_name, filename, fileFormat, subject_name, description, user_id, username)
        # Have to send a audio saved path in s3 to "Transcription model and get back the transcript text file"

        lda_file_path, keyword_file_path = textPreprocess(lec_id, lec_name)
        # lda_file_path = "topics_files/LDA_topics/MOLM_LDA_keywordList.txt"
        # keyword_file_path = "topics_files/Key_words/MOLM_1_keywordList.txt"
        # clean_audio_video_file_path = "uploads\MOLM_1\Cleaned_audio_with_video\cleaned_Eduscope.mp4"
        lecture_segmentation_folder_path, remove_segment_folder_path = videoSegmentation(lda_file_path, keyword_file_path, lec_name, lec_id, clean_audio_video_file_path, subject_name)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "main|" + "Uploading segments to blob in process..")
        upload_video(lec_name, subject_name, lecture_segmentation_folder_path, SEGMENT, lec_id) # UPLOADING VIDEO SEGMENT FILES TO S3 BUCKET
        # blob.upload_video(lecture_segmentation_folder_path, type = SEGMENT) # UPLOADING VIDEO SEGMENT FILES TO S3 BUCKET

        EmailService(SUCCESS_EMAIL_BODY, EMAIL_SUBJECT, destination_email_address) # SEND EMAILS
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "main|" + "email sent")
        rmtree(main_path)
        rmtree(remove_segment_folder_path)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "main|" + "Background process Finished..")

        # AFTER COMPLETING EVERYTHING DELETE THE VIDEOS AND AUDIOS IN THE DIRECTORY
        # file path to to the files = path

    except OSError as e:
            # logger.error_log(BACK_GROUND_FILE_PROCESS_ERROR_LOG, "Error: %s - %s." % (e.filename, e.strerror), BACKGROUND_PROCESS)
            logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "Error: %s - %s." % (e.filename, e.strerror))
    except Exception as e:
        # logger.error_log(BACK_GROUND_FILE_PROCESS_ERROR_LOG, e, BACKGROUND_PROCESS)
        logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, e)

if __name__ == "__main__":
    logger = Logger()
    logger.debug(BACKGROUND_PROCESS, BACK_GROUND_FILE_PROCESS_LOG, "Background Process started.")
    main()