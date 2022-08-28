"""
# HANDLING LOG FILES
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jun-26
"""


import logging
import os
from Const.const import (AUDIO_SEGMENTATION_LOG_FILE, TEXT_PREPROCESS_LOG_FILE, VIDEO_SEGMENTATION_LOG_FILE, FORMATTER, AUDIO, VIDEO, 
                        TEXT_PREPROCESS, AUDIO_SEGMENTATION_ERROR_LOG_FILE, TEXT_PREPROCESS_ERROR_LOG_FILE, VIDEO_SEGMENTATION_ERROR_LOG_FILE,
                        MAIN_LOG_FILE, MAIN_ERROR_LOG_FILE, MAIN, BACK_GROUND_FILE_PROCESS_LOG_FILE, BACK_GROUND_FILE_PROCESS_ERROR_LOG_FILE, BACKGROUND_PROCESS,
                        EMAIL, EMAIL_LOG_FILE, EMAIL_ERROR_LOG_FILE, S3_LOG_FILE, S3_ERROR_LOG_FILE, S3, RDS, RDS_LOG_FILE, RDS_ERROR_LOG_FILE, LOG_FOLDER, LOG_PATH_FOLDER,
                        USE_OWN_LOGS, ERROR_LOG_PATH_FOLDER)

class Logger():
    def __init__(self):
            self.formatter = logging.Formatter(FORMATTER)
            self.logger = None
            self.file_handler_debug = None
            self.file_handler_error = None
            self.error_logger = None
            self.use_own_logs = USE_OWN_LOGS
            if self.use_own_logs == True:
                if os.path.exists(LOG_FOLDER) == False: # MAIN LOG FOLDER
                    os.mkdir(LOG_FOLDER)
                if os.path.exists(LOG_PATH_FOLDER) == False: # NORMAL LOG FOLDER CREATION INSIDE MAIN LOG FOLDER
                    os.mkdir(LOG_PATH_FOLDER)
                if os.path.exists(ERROR_LOG_PATH_FOLDER) == False: # ERROR_LOG_PATH_FOLDER FOLDER CREATION INSIDE MAIN LOG FOLDER
                    os.mkdir(ERROR_LOG_PATH_FOLDER)
    
    def debug(self, name, log_name, msg):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        if name == AUDIO:
            self.file_handler_debug = logging.FileHandler(AUDIO_SEGMENTATION_LOG_FILE) # AUDIO SEGMENTATION LOG FILE
        elif name == VIDEO:
            self.file_handler_debug = logging.FileHandler(VIDEO_SEGMENTATION_LOG_FILE) # VIDEO SEGMENTATION LOG FILE
        elif name == TEXT_PREPROCESS:
            self.file_handler_debug = logging.FileHandler(TEXT_PREPROCESS_LOG_FILE) # TEXT PREPROCESSING LOG FILE
        elif name == BACKGROUND_PROCESS:
            self.file_handler_debug = logging.FileHandler(BACK_GROUND_FILE_PROCESS_LOG_FILE) # BACKGROUND PREPROCESSING LOG FILE
        elif name == MAIN:
            self.file_handler_debug = logging.FileHandler(MAIN_LOG_FILE) # MAIN LOG FILE
        elif name == EMAIL:
            self.file_handler_debug = logging.FileHandler(EMAIL_LOG_FILE) # EMAIL LOG FILE
        elif name == S3:
            self.file_handler_debug = logging.FileHandler(S3_LOG_FILE) # AWS S3 LOG FILE
        elif name == RDS:
            self.file_handler_debug = logging.FileHandler(RDS_LOG_FILE) # AWS RDS LOG FILE

        self.file_handler_debug.setFormatter(self.formatter)
        if (self.logger.hasHandlers()):
            self.logger.handlers.clear()

        self.logger.addHandler(self.file_handler_debug)
        self.logger.debug(msg)
    
    def error_log(self, log_name, msg, name = MAIN):
        self.error_logger = logging.getLogger(log_name)
        self.error_logger.setLevel(logging.ERROR)

        if name == AUDIO:
            self.file_handler_error = logging.FileHandler(AUDIO_SEGMENTATION_ERROR_LOG_FILE) # AUDIO SEGMENTATION ERROR LOG FILE
        elif name == VIDEO:
            self.file_handler_error = logging.FileHandler(VIDEO_SEGMENTATION_ERROR_LOG_FILE) # VIDEO SEGMENTATION ERROR LOG FILE
        elif name == TEXT_PREPROCESS:
            self.file_handler_error = logging.FileHandler(TEXT_PREPROCESS_ERROR_LOG_FILE) # TEXT PREPROCESSING ERROR LOG FILE
        elif name == BACKGROUND_PROCESS:
            self.file_handler_error = logging.FileHandler(BACK_GROUND_FILE_PROCESS_ERROR_LOG_FILE) # BACKGROUND PREPROCESSING ERROR LOG FILE
        elif name == MAIN:
            self.file_handler_error = logging.FileHandler(MAIN_ERROR_LOG_FILE) # MAIN ERROR LOG FILE
        elif name == EMAIL:
            self.file_handler_error = logging.FileHandler(EMAIL_ERROR_LOG_FILE) # EMAIL ERROR LOG FILE
        elif name == S3:
            self.file_handler_error = logging.FileHandler(S3_ERROR_LOG_FILE) # AWS S3 ERROR LOG FILE
        elif name == RDS:
            self.file_handler_error = logging.FileHandler(RDS_ERROR_LOG_FILE) # AWS RDS ERROR LOG FILE

        self.file_handler_error.setFormatter(self.formatter)
        if (self.error_logger.hasHandlers()):
            self.error_logger.handlers.clear()
            
        self.error_logger.addHandler(self.file_handler_error)
        self.error_logger.exception(msg)
        