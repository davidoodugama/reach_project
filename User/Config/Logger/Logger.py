"""
# HANDLING LOG FILES
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-July-25
"""

import logging
import os
from Const.const import (FORMATTER, MAIN_LOG_FILE, MAIN_ERROR_LOG_FILE, MAIN, EMAIL, EMAIL_LOG_FILE, EMAIL_ERROR_LOG_FILE, RDS, RDS_LOG_FILE, 
                        RDS_ERROR_LOG_FILE, LOG_FOLDER, LOG_PATH_FOLDER, USE_OWN_LOGS, ERROR_LOG_PATH_FOLDER, USER, USER_LOG_FILE, USER_ERROR_LOG_FILE)

class Logger:
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

        if name == USER:
            self.file_handler_debug = logging.FileHandler(USER_LOG_FILE) # USER LOG FILE
        elif name == MAIN:
            self.file_handler_error = logging.FileHandler(MAIN_LOG_FILE) # MAIN LOG FILE
        elif name == EMAIL:
            self.file_handler_error = logging.FileHandler(EMAIL_ERROR_LOG_FILE) # EMAIL ERROR LOG FILE
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

        if name == USER:
            self.file_handler_error = logging.FileHandler(USER_ERROR_LOG_FILE) # USER ERROR LOG FILE
        elif name == MAIN:
            self.file_handler_error = logging.FileHandler(MAIN_ERROR_LOG_FILE) # MAIN ERROR LOG FILE
        elif name == EMAIL:
            self.file_handler_error = logging.FileHandler(EMAIL_ERROR_LOG_FILE) # EMAIL ERROR LOG FILE
        elif name == RDS:
            self.file_handler_error = logging.FileHandler(RDS_ERROR_LOG_FILE) # AWS RDS ERROR LOG FILE

        self.file_handler_error.setFormatter(self.formatter)
        if (self.error_logger.hasHandlers()):
            self.error_logger.handlers.clear()
            
        self.error_logger.addHandler(self.file_handler_error)
        self.error_logger.exception(msg)
        