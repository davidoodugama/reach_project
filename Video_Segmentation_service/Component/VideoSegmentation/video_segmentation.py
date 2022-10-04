"""
# VIDEO SEGMENTATION ACCORDING TO TOPICS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-05
"""

import cv2
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import easyocr
from nltk.tokenize import word_tokenize
import collections
from Config.Logger.Logger import Logger
from moviepy.editor import VideoFileClip
import os
import ast
from flask import jsonify
# from Config.S3_Config.S3_Config import S3_Config
from Const.const import FPS, CHANGED_FPS_VIDEO_SAVING_PATH, VIDEO, VIDEO_SEGMENTATION_LOG, MP4_FORMAT, SEGMENT_FOLDER, VIDEO_SEGMENTATION_ERROR_LOG, CODEC, SEGMENT

"""
# THIS IS VIDEO SEGMENTATION CLASS 
# 
# THE FOLLOWING TASK ARE IMPLEMENTED IN THIS CLASS
# IMAGE PROCESSING
# TEXT EXTRACTION FROM IMAGE FRAME
# DECREASE FPS
# SEGMENTING VIDEO
"""
class VideoSegmentation:
    def __init__(self, lda_topic_list, key_token, lec_name, lec_id, video_file_path, subject_name):
        try:
            self.debug = Logger()
            # self.s3 = S3_Config(lec_id, lec_name, subject_name)
            self.reader = easyocr.Reader(['en'], gpu = True)
            self.lemmatizer = WordNetLemmatizer()
            self.stopwords = stopwords.words('english')
            self.name = "Introduction" # BEGINING OF THE VIDEO
            self.subject_name = subject_name
            self.start_time = 0.0
            self.end_time = 0.0
            self.desc_a = np.zeros(shape=(500, 32))
            self.desc_b = np.zeros(shape=(500, 32))
            self.lec_name = lec_name
            self.lec_id = lec_id
            self.cleaned_video_file_path = video_file_path
            self.lec_after_fps_changed_folder_name = str(lec_id) + "_" + lec_name
            self.changed_fps_video_name = str(lec_id) + "_" +lec_name + MP4_FORMAT

            if os.path.exists(CHANGED_FPS_VIDEO_SAVING_PATH): # CHECK FPS CHANGED VIDEO FILE SAVE FOLDER EXIST
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File exsist " + CHANGED_FPS_VIDEO_SAVING_PATH)
            else:
                os.mkdir(CHANGED_FPS_VIDEO_SAVING_PATH)
            
            if os.path.exists(SEGMENT_FOLDER): # CHECK SEGMENT FOLDER EXIST FOR STORING VIDEO SEGMENTS
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File exsist " + SEGMENT_FOLDER)
            else:
                os.mkdir(SEGMENT_FOLDER) # self.subject_name

            if os.path.exists(SEGMENT_FOLDER + self.subject_name): # CHECK WHETHER SUBJECT FOLDER IS ALREADY THERE
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File exsist " + SEGMENT_FOLDER + self.subject_name)
                self.remove_segment_folder_path = SEGMENT_FOLDER + self.subject_name
            else:
                os.mkdir(SEGMENT_FOLDER + self.subject_name) # CREATE SUBJECT FOLDER
                self.remove_segment_folder_path = SEGMENT_FOLDER + self.subject_name
            
            if os.path.exists(SEGMENT_FOLDER + self.subject_name + "/" + self.lec_after_fps_changed_folder_name): # CHECK UNDER SEGMENT FOLDER FOR THE CURRENT LECTURE THERE IS A FOLDER
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File exsist " + SEGMENT_FOLDER + self.subject_name + "/" + self.lec_after_fps_changed_folder_name)
                self.lecture_segmentation_folder_path = SEGMENT_FOLDER + self.subject_name + "/" + self.lec_after_fps_changed_folder_name
            else:
                os.mkdir(SEGMENT_FOLDER + self.subject_name + "/" + self.lec_after_fps_changed_folder_name) # CREAETE LECTURE FOLDER INSIDE THE SUBJECT FOLDER
                self.lecture_segmentation_folder_path = SEGMENT_FOLDER + self.subject_name + "/" + self.lec_after_fps_changed_folder_name
            
            if os.path.exists(CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name): # UNDER THE CURRENT SUBJECT FPS CHANGED VIDEO FILE SAVE FOLDER EXIST
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File exsist " + CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name)
                self.full_fps_changed_video_file_path = CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name
            else:
                os.mkdir(CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name)
                self.full_fps_changed_video_file_path = CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name # FULL PATH TO THE CHANGED FPS VIDEO FILE
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"File created in " + CHANGED_FPS_VIDEO_SAVING_PATH + self.lec_after_fps_changed_folder_name)
            
            self.topic_details = collections.defaultdict(list)
            with open(lda_topic_list, "r") as lda: # READ PREPROCESSED LDA TOPIC LIST
                self.topic_list = lda.read()
            self.topic_list = ast.literal_eval(self.topic_list)

            with open(key_token, "r") as keyTokens: # READ PREPROCESSED TOPIC LIST
                self.key_token = keyTokens.read()
            self.key_token = ast.literal_eval(self.key_token)
            
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })

    """
    # THIS FUNCTION IS USED TO IDENTIFY THE TOPIC IN THE IMAGE FRAME
    """
    def findName(self, result):
        try:
            first_result_top_x = result[0][0][0][1]
            first_topic_name = result[0][1]
            name = first_topic_name
            
            for i in range(len(result)-1):
                i += 1
                height_of_word = result[i][0][2][1] - result[i][0][1][1]

                if abs(first_result_top_x - result[i][0][0][1]) in range(0,20): # FIND NAMES THAT IS IN THE FIRST LINE
                    if abs(height_of_word) in range(35,200):
                        name = name + " " + result[i][1]
            return name
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })
    
    """
    THIS FUNCTION IS USED TO IDENTIFY THE SEGMENT BOUNDERY TIME
    """
    def check_topic(self, word, time):
        try:
            name = ""
            self.end_time = time
            if word != None: # CHECK IF EXTRACTED WORD EXSIT IN TOPIC MODEL LIST
                token = word_tokenize(word)
                for w in token:
                    w = w.lower()
                    w = self.lemmatizer.lemmatize(w)
                    if w not in self.stopwords:
                        if w in self.topic_list:
                            name = word
                            self.topic_list.remove(w)
                            self.key_token.remove(w) if w in self.key_token else False
                        elif w in self.key_token:
                            name = word
                            self.key_token.remove(w)
                            self.topic_list.remove(w) if w in self.topic_list else False
                
                if name != "" and self.start_time != self.end_time and len(word) > 2:
                    
                    self.topic_details["topic"].append({ "topic": self.name,
                                                        "start_time": self.start_time,
                                                        "end_time": self.end_time})
                    self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "extract_videoFrame|Topic list " + str(self.topic_details["topic"]))
                    self.name = name.strip()
                    self.start_time = self.end_time
                elif self.name == name:
                    pass
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })

    """
    THIS FUNCTION IS USED TO CALCULATE THE SIMILARITY SCORE BETWEEN 2 EXTRACTED FRAMES
    """
    def orb_sim(self, img1, img2):
        try:
            orb = cv2.ORB_create()
            kp_a, desc_a = orb.detectAndCompute(img1, None)
            p_b, desc_b = orb.detectAndCompute(img2, None)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = True)
            if type(desc_a) == np.ndarray and type(desc_b) == np.ndarray:
                matches = bf.match(desc_a, desc_b)
                similar_regions = [i for i in matches if i.distance < 30]
                if len(matches) == 0:
                    return 0
                return len(similar_regions) / len(matches)
            else:
                return None
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })
    
    """
    THIS FUNCTION IS USED TO PREPROCESS THE EXTRACTED FRAME FROM THE VIDEO
    """
    def mask(self, frame):
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) # PROCESSING FRAME
            lower_blue = np.array([0, 0, 0])
            upper_blue = np.array([179, 208, 49])
            mask = cv2.inRange(hsv, lower_blue, upper_blue)
            mask = cv2.resize(mask,(800,500))
            return mask
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })
    
    """
    THIS FUNCTION IS USED TO MESSURE THE SIMILARITY AND RETURN WHETHER THE 2 FRAMES ARE SIMILARY OR NOT
    """
    def comapre_imgs(self, img1, img2):
        try:
            orb_similarity = self.orb_sim(img1, img2)
            if orb_similarity != None:
                if orb_similarity < 0.90:
                    return True
            else:
                return False
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })
    
    """
    THIS FUNCTION IS USED TO DECREASE THE FPS OF THE VIDEO INORDER TO MAKE THE READING FASTER
    """
    def change_fps_of_video(self):
        try:
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "change_fps_of_video|In progress...")
            clip = VideoFileClip(self.cleaned_video_file_path) # PATH OF THE CLEANED AUDIO VIDEO FILE
            new_clip = clip.set_fps(FPS)
            new_clip.write_videofile(self.full_fps_changed_video_file_path + "/" + self.changed_fps_video_name)
            self.fps_changed_video_path = self.full_fps_changed_video_file_path + "/" + self.changed_fps_video_name
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "change_fps_of_video|FPS changed in video " + self.cleaned_video_file_path + " to " + self.fps_changed_video_path)
            clip.close()
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })

    def extract_videoFrame(self):
        try:
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "extract_videoFrame|In progress...")
            cap = cv2.VideoCapture(self.fps_changed_video_path)
            self.frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.fps   = cap.get(cv2.CAP_PROP_FPS)
            self.endTime = self.frames / self.fps
            count = 0
            img2 = np.array([])
            while(cap.isOpened()):
                ret ,frame = cap.read()
                count +=1
                Time  = count/self.fps
                if ret == True:
                    img1 = self.mask(frame)
                    if not np.any(img2):
                        result = self.reader.readtext(img1)
                        if len(result):
                            name   = self.findName(result)
                            self.check_topic(name, Time)
                        else:
                            pass
                    else:
                        pass
                    if img2.size != 0:
                        res = self.comapre_imgs(img1, img2)
                        if res:
                            result = self.reader.readtext(img1)
                            if len(result):
                                name   = self.findName(result)
                                self.check_topic(name, Time)
                            else:
                                pass

                    img2 = img1
                    key = cv2.waitKey(1)
                    if key == 27 & 0xFF == ord('q'):
                        break
                else:
                    break
            cap.release()
            self.topic_details["topic"].append({"topic": self.name,
                                                "start_time": self.start_time,
                                                "end_time": self.endTime})
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "extract_videoFrame|Final topic list " + str(self.topic_details["topic"]))
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, "extract_videoFrame|Finished.")
            return True
        
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })

    def segment_video(self):
        try:
            vid = VideoFileClip(self.cleaned_video_file_path) # ACTUAL CLEANED AUDIO VIDEO FILE PATH
            for i in self.topic_details["topic"]: 
                start_time = i["start_time"] 
                end_time = i["end_time"]
                trim_vid = vid.subclip(start_time, end_time)
                trim_vid.write_videofile(self.lecture_segmentation_folder_path + "/" + i["topic"] + MP4_FORMAT, codec = CODEC) # STORING SEGMENT VIDEOS IN THE PATH
                self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG,"segment_video| " + self.lecture_segmentation_folder_path + "/" + i["topic"] + MP4_FORMAT + " file saved complete")
                
            # UPLOAD SEGMENTS TO S3
            # self.s3.upload_video(self.lecture_segmentation_folder_path + "/", SEGMENT)
            return self.lecture_segmentation_folder_path, self.remove_segment_folder_path
                
        except Exception as e:
            # self.debug = Logger()
            # self.debug.error_log(VIDEO_SEGMENTATION_ERROR_LOG, e, VIDEO)
            # return False
            self.debug.debug(VIDEO, VIDEO_SEGMENTATION_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })