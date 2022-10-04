import os
from datetime import date
today = date.today()  # CURRENT DATE LOG FILE NAME

""" *************************************************************** MAIN FEATURES ************************************************************** """
AUDIO = "audio"
VIDEO = "video"
TEXT_PREPROCESS = "text"
MAIN = "main"
BACKGROUND_PROCESS = "backgroundProcess"
EMAIL = "email"
RDS = "rds"
AZURE_DB = "azure_db"
AZURE_BLOB = "azure_blob"
CURRENT_TIMESTAMP = "CURRENT_TIMESTAMP"
USER = "user"

""" ************************************************************** AWS S3 SERVICE ************************************************************* """
REGION = "us-east-1"
ACCESS_KEY = 'AKIAZHUZ3LI3XW6WKKWL'
SECRET_KEY = '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'
S3 = 's3'
BUCKET_NAME = "createmycourcevideo"
# S3_UPLOAD_FILE_URL_FORMAT = "s3://" + BUCKET_NAME + "/"
# FILE_URL = 'https://' + BUCKET_NAME + '.s3.amazonaws.com/'
FILE_NOT_EXIST = "The file does not exist"

""" ************************************************************** AZURE BLOB SERVICE ************************************************************* """
STORAGE_ACCOUNT_KEY = "RUUXeqklhmre9XK5xbzQy+mU3IiyEsNlX2L2GbIeUeQPUtyHNGFPIJeZClKGEQDv7hM5Wmath8jV+AStmile3w=="
STORAGE_ACCOUNT_NAME = "createmycourse"
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=createmycourse;AccountKey=x9lQNg6LvfyT+QQ03ux2NS2FF5EN4S8Ntzg5wxL5cer9dBNOwRGpK0WcJGFvav3CT55YwPKK2khX+ASt00M5Ww==;EndpointSuffix=core.windows.net;"
CONTAINER_NAME = "createmycourse"
FILE_URL = "https://createmycourse.blob.core.windows.net/createmycourse/"

""" ************************************************************** EMAIL SERVICE ************************************************************** """
SOURCE_EMAIL = "createmycoursesliit@gmail.com"
ADMIN_MAIL = "davidoodugama1999@gmail.com"
EMAIL_SUBJECT_FOR_ACCEPTENCE = "New user alert pending acceptence.."
PASSWORD = "Hk@gi94pf0d40f"
# os.environ['GMAIL_AUTHENTICATION_PIN'] = "iwflcciewvubqbwu"
GMAIL_AUTHENTICATION_PIN = "iwflcciewvubqbwu"
SUCCESS_EMAIL_BODY = """
Dear valuable user your lecture segmentation process is complete. 

Segmented lecture videos will be available in our page. 

Thank you for using our service.

If you come across some issue please feel free to reach us by sending your emails to createmycoursesliit@gmail.com

Have a nice day.

Thanks,

Best Regards,
Create My Course
"""
EMAIL_SUBJECT = "Lecture video upload complete."

""" ******************************************************************* USER ****************************************************************** """
USERTB = "User"
NEW_USER_MESSAGE = """
New user added to our system and pending for approval from you. 

User details are as follows,

Username: {}
role_id: {}
email: {}
name: {}
contact: {}

Thanks,

Best Regards,
CreateMyCourse
"""

""" ******************************************************************* AWS RDS ****************************************************************** """
# HOST = "lecture.cbhh91yjg4k1.us-east-1.rds.amazonaws.com"
# USER = "admin"
# PASS = "adminpassword"
# DB_NAME = "video_segmentation"

""" ******************************************************************* AZURE MY SQL ****************************************************************** """
HOST = 'rpdb.mysql.database.azure.com'
USER_NAME = "rp_admin"
PASS = "A.dminpassword"
DB_NAME = "CreateMyCource"
SSL = "Video_Segmentation_service/Config/Azure_DB_Config/SSL/DigiCertGlobalRootG2.crt.pem"


""" ************************************************************** AUDIO PREPROCESS ************************************************************** """
# AUDIO TRANSCRIPT SERVICE
AUDIO_FILE = './audio/audio1.wav'
DEEPSPEECH_MODELS_PBMM = './transcribe_models/deepspeech-0.9.3-models.pbmm'
DEEPSPEECH_MODELS_SCORER = './transcribe_models/deepspeech-0.9.3-models.scorer'

# AUDIO SERVICE
AUDIO_FORMAT = ".wav"
VIDEO_UPLOAD_PATH = "/Video_uploads/"
AUDIO_UPLOAD_PATH = "/extracted_audio/"
CLEAN_AUDIO_PATH = "/clean_audio/"
WITHOUT_AUDIO_PATH = "/without_audio/"
CLEANED_AUDIO_WITH_VIDEO = "/Cleaned_audio_with_video/"
PREPROCESSED_FILE_PATH = "/preprocess/"
TS_FORMAT = ".ts"
MP4_FORMAT = ".mp4"
CODEC = 'libx264'
FFMPEG_COMMAND = "C:\\ffmpeg\\ffmpeg -i "
FFMPEG_COMMAND_PARAS = " -vn -ar 16000 -ac 1 "
MAIN_UPLOAD_FOLDER = "uploads/"

# AUDIO CLEANING PARAMETERS
FREQ_MASK_SMOOTH_HZ = 500
SIGMOID_SLOPE_NONSTATIONARY = 2
THRESH_N_MULT_NONSTATIONARY = 3
N_STD_THRESH_STATIONARY = 1.5
N_FFT = 1024
N_JOBS = 2
NOISE_CHUNK_SIZE = 60000
PADDING = 60000
TIME_MASK_SMOOTH_MS = 64

""" ************************************************************* TEXT PREPROCESSING ************************************************************* """
# LDA MODEL PARAMETERS
NUMBER_OF_TOPICS = 10
RANDOME_STATE = 100
CHUNK_SIZE = 100
PASSES = 100

# TOPIC FILE SAVING PATHS

MAIN_TOPIC_FOLDER_PATH = "topics_files"
LDA_TOPIC_FILE_PATH = MAIN_TOPIC_FOLDER_PATH + "/LDA_topics/"
KEY_WORD_FILE_PATH = MAIN_TOPIC_FOLDER_PATH + "/Key_words/"

# TESTING
TRANSCRIPT_PATH = "Component/TextPreprocess/Transcript.txt"

""" ************************************************************* VIDEO SEGMENTATION ************************************************************* """
# VIDEO SEGMENTATION DETAILS
FPS = 10
CHANGED_FPS_VIDEO_SAVING_PATH = "Changed_fps_videos/"
SEGMENT_FOLDER = "segments/"


""" ******************************************************************** LOGS ******************************************************************** """
"""
**************************************************** IMPORTANT ****************************************************
## IF USE SERVER CREATED LOG FILE THEN UPDATE USE_OWN_LOGS TO FALSE AND PUT THE SERVER LOG PATHS FOR THE LOGS FILES.
## IF USE OWN LOGS FILES THEN UPDATE USE_OWN_LOGS TO TRUE.
"""
# USE OWN LOG FOLDER
USE_OWN_LOGS = True

# MAIN LOG FOLDER
LOG_FOLDER = "Logs"

# LOG PATH FOLDER NAME
LOG_PATH_FOLDER = "Logs/logs/"

# ERROR LOG PATH FOLDER NAME
ERROR_LOG_PATH_FOLDER = "Logs/error_logs/"

# MAIN LOG FILE PATHS
USER_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_user.log"
USER_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_user_Error_log.log"

# AUDIO LOG FILE PATHS
AUDIO_SEGMENTATION_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_audio_segmentation.log"
AUDIO_SEGMENTATION_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_audio_segmentation_error_log.log"

# TEXT PREPROCESS LOG FILE PATHS
TEXT_PREPROCESS_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_textPreprocess.log"
TEXT_PREPROCESS_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_textPreprocess_error_log.log"

# VIDEO SEGMENTATION FILE PATHS
VIDEO_SEGMENTATION_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_videoSegmentation.log"
VIDEO_SEGMENTATION_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_videoSegmentation_error_log.log"

# BACKGROUND PROCESS FILE PATHS //
BACK_GROUND_FILE_PROCESS_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_background_file_process.log"
BACK_GROUND_FILE_PROCESS_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_background_file_process_error_log.log"

# MAIN LOG FILE PATHS
MAIN_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_main.log"
MAIN_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_main_Error_log.log"

# EMAIL SERVICE
EMAIL_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_email.log"
EMAIL_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_email_Error_log.log"

# S3 LOG FILE PATHS
S3_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_s3.log"
S3_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_s3_Error_log.log"

# AZURE BLOB LOG FILE PATHS
AZURE_BLOB_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_azure_blob.log"
AZURE_BLOB_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_azure_blob_Error_log.log"

# RDS LOG FILE PATHS
RDS_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_rds.log"
RDS_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_rds_Error_log.log"

# AZURE MYSQL LOG FILE PATHS
AZURE_MYSQL_LOG_FILE = LOG_PATH_FOLDER + str(today) + "_azure_mysql.log"
AZURE_MYSQL_ERROR_LOG_FILE = ERROR_LOG_PATH_FOLDER + str(today) + "_azure_mysql_Error_log.log"

# LOG FORMAT
FORMATTER = '%(asctime)s|%(name)s|%(message)s'

# MAIN LOG NAMES
MAIN_ERROR_LOG = "Main_Error"
MAIN_LOG = "Main"

# MAIN LOG NAMES
USER_ERROR_LOG = "User_Error"
USER_LOG = "UserService"

# AUDIO SEMENTAION LOG NAMES
AUDIO_SEGMENTATION_ERROR_LOG = "Audio_extractor_Error"
AUDIO_SEGMENTATION_LOG = "Audio_extractor"

# TEXT PREPROCESS LOG NAMES
TEXT_PREPROCESS_ERROR_LOG = "Text_preprocess_Error"
TEXT_PREPROCESS_LOG = "Text_preprocess"

# BACKGROUND PROCESS LOG NAMES
BACK_GROUND_FILE_PROCESS_ERROR_LOG = "backgroundProcess_Error"
BACK_GROUND_FILE_PROCESS_LOG = "backgroundProcess"

# VIDEO SEGMENTATION LOG NAMES
VIDEO_SEGMENTATION_ERROR_LOG = "VideoSegmentation_Error"
VIDEO_SEGMENTATION_LOG = "VideoSegmentation"

# EMAIL SERVICE LOG NAMES
EMAIL_ERROR_LOG = "EmailService_Error"
EMAIL_LOG = "EmailService"

# S3 LOG NAMES
S3_ERROR_LOG = "S3_Config_Error"
S3_LOG = "S3_Config"

# AZURE BLOB LOG NAMES
AZURE_BLOB_ERROR_LOG = "azure_blob_Config_Error"
AZURE_BLOB_LOG = "azure_blob_Config"

# RDS LOG NAMES
RDS_ERROR_LOG = "RDS_Config_Error"
RDS_LOG = "RDS_Config"

# AZURE MYSQL LOG NAMES
AZURE_MYSQL_ERROR_LOG = "AZURE_Mysql_Config_Error"
AZURE_MYSQL_LOG = "AZURE_Mysql_Config"

""" ************************************************************* BACKGROUND PROCESS ************************************************************* """
# CMD COMMAND
BACKGROUND_CMD_COMMAND = "backgroundProcess.py"
ORIGINAL = "original"
SEGMENT = "segment"
