"""
# CLEANING BACKGROUND NOISE FROM AUDIO
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jun-30
"""

from Config.S3_Config.S3_Config import S3_Config
from scipy.io.wavfile import read, write
import noisereduce as nr
import subprocess
import os
# from Config.RDS_Config.DB_Config import Rds_Config
# import json
# from werkzeug.utils import secure_filename
from flask import jsonify
from Config.Logger.Logger import Logger
from Const.const import (AUDIO_UPLOAD_PATH, VIDEO_UPLOAD_PATH, CLEAN_AUDIO_PATH, AUDIO_FORMAT, WITHOUT_AUDIO_PATH, CLEANED_AUDIO_WITH_VIDEO, 
                        FFMPEG_COMMAND, FFMPEG_COMMAND_PARAS, TS_FORMAT, MP4_FORMAT, FREQ_MASK_SMOOTH_HZ, SIGMOID_SLOPE_NONSTATIONARY, 
                        THRESH_N_MULT_NONSTATIONARY, N_STD_THRESH_STATIONARY, N_FFT, NOISE_CHUNK_SIZE, PADDING, TIME_MASK_SMOOTH_MS, MAIN_UPLOAD_FOLDER, AUDIO,
                         AUDIO_SEGMENTATION_LOG, AUDIO_SEGMENTATION_ERROR_LOG, N_JOBS, ORIGINAL)
from moviepy.editor import VideoFileClip, AudioFileClip

class Audio_extractor:
    
    """
    # DEFAULT CONSTRUCTOR
    # lec_id = Unique Id of the lecture video
    # lec_name = Name of the lecture
    # filename = Name of the video file
    """
    def __init__(self, lec_id, lec_name, filename, subject_name):
        try:
            self.s3 = S3_Config(lec_id, lec_name, subject_name)
            self.lec_id = str(lec_id)
            self.subject_name = subject_name
            self.lec_name = str(lec_name)
            self.main_path = self.lec_name + "_" + self.lec_id
            self.filename = filename # VIDEO FILE NAME
            self.debug = Logger()
            # self.db = Rds_Config("video_segmentation")
            if os.path.exists(MAIN_UPLOAD_FOLDER):
                self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG,"Audio_extraction|Started|File exsist " + MAIN_UPLOAD_FOLDER)
            else:
                os.mkdir(MAIN_UPLOAD_FOLDER)
            if os.path.exists(MAIN_UPLOAD_FOLDER + self.main_path):
                self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG,"Audio_extraction|Started|File exsist " + MAIN_UPLOAD_FOLDER + self.main_path)
            else:    
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path)
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path + VIDEO_UPLOAD_PATH)
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path + CLEAN_AUDIO_PATH)
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path + AUDIO_UPLOAD_PATH)
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path + WITHOUT_AUDIO_PATH)
                os.mkdir(MAIN_UPLOAD_FOLDER + self.main_path + CLEANED_AUDIO_WITH_VIDEO)
            # ................................................... PATHS .........................................................
            
            self.save_clean_file_format = MAIN_UPLOAD_FOLDER + self.main_path + CLEAN_AUDIO_PATH + "cleaned_" + self.lec_name + "_" + self.lec_id + AUDIO_FORMAT # PATH WHERE CLEAN AUDIO FILE GETS STORED
            self.path = MAIN_UPLOAD_FOLDER + self.main_path + VIDEO_UPLOAD_PATH + self.lec_name # VIDEO SAVED PATH
            # self.path = MAIN_UPLOAD_FOLDER + self.main_path + VIDEO_UPLOAD_PATH # VIDEO SAVED PATH
            self.video_audio_extract_path = MAIN_UPLOAD_FOLDER + self.main_path + AUDIO_UPLOAD_PATH + self.main_path + AUDIO_FORMAT # SAVING PATH FOR EXTRACTED AUDIO FILES FROM VIDEO
        except Exception as e:
            self.debug = Logger()
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO)
            return jsonify({
                "error": 1,
                "code": 500,
                "error" : "{0}".format(e)
                })
                
    """
    # STORING VIDEO FILE INTO PATH
    """
    def storeVideo(self, video_file): 
        try:
            self.debug = Logger()
            if os.path.exists(self.path):
                pass
            else:
                os.mkdir(self.path)
            video_file.save(os.path.join(self.path, self.filename))
            # sql = '''insert into %s(video_file_name) values('%s')
            # ''' % ("video_segmentation",
            #        self.filename,
            #        )
            # self.db.insertValues(sql)
            self.s3.upload_video(self.path + "/" + self.filename, ORIGINAL)
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "File " + self.filename + " stored completed")
            return self.path + "/"  + self.filename

        except Exception as e:
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO) # AUDIO_SEGMENTATION_ERROR_LOG
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
            

    def convertVideoToMp4(self):
        try:
            self.debug = Logger()
            out_file_name = self.filename.replace(TS_FORMAT, MP4_FORMAT)
            command = FFMPEG_COMMAND + self.path + '/' + self.filename + ' ' + self.path + '/' + out_file_name
            path = self.path + '/' + out_file_name
            subprocess.run(command, shell=True)
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Converting tsv to mp4 completed")
            self.filename = out_file_name

        except Exception as e:
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
            
    """
    # EXTRACT AUDIO FROM VIDEO FUNCTION
    # CLEAN BACKGROUND NOISE FROM AUDIO
    """
    def extract_clean_audio(self):
        try:
            self.debug = Logger()
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Extract Clean Audio in progress...")
            self.non_audio_path = MAIN_UPLOAD_FOLDER + self.main_path + WITHOUT_AUDIO_PATH + self.filename # SAVING PATH FOR NON AUDIO VIDEO FILE
            command = FFMPEG_COMMAND + self.path + "/" + self.filename + FFMPEG_COMMAND_PARAS + self.video_audio_extract_path # EXTRACT AUDIO FROM VIDEO
            subprocess.call(command, shell = True)
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Extract Clean Audio Complete")

            videoclip = VideoFileClip(self.path + "/" + self.filename) # REMOVE AUDIO FROM VIDEO
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Removing audio from video in progress")

            new_clip = videoclip.without_audio()
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Wrting non audio video file to " + self.non_audio_path)
            
            new_clip.write_videofile(self.non_audio_path, fps=30, threads = 2, codec="libx264") # WRITE VIDEO FILE WITHOUT AUDIO
            res = self.clean_audio()  # CLEAN AUDIO
            videoclip.close()
            if res:
                clean_audio_video_file_path = self.add_audio_to_video()
                self.s3.upload_video(clean_audio_video_file_path, ORIGINAL)
                self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Cleaned video uploaded to s3.")
            
            return MAIN_UPLOAD_FOLDER + self.main_path, clean_audio_video_file_path

        except Exception as e:
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    """
    # CLEAN BACKGROUND NOISE FROM AUDIO
    # https://github.com/timsainb/noisereduce
    """
    def clean_audio(self):
        try:
            self.debug = Logger()
            rate, data = read(self.video_audio_extract_path) # LOAD DATA
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Cleaning Audio in progress")
            reduced_noise = nr.reduce_noise(
            y = data,   
            sr = rate,
            freq_mask_smooth_hz = FREQ_MASK_SMOOTH_HZ,
            sigmoid_slope_nonstationary = SIGMOID_SLOPE_NONSTATIONARY,
            thresh_n_mult_nonstationary = THRESH_N_MULT_NONSTATIONARY, 
            n_std_thresh_stationary = N_STD_THRESH_STATIONARY,
            n_fft = N_FFT,
            # n_jobs = N_JOBS,
            use_tqdm = True, 
            chunk_size = NOISE_CHUNK_SIZE, 
            padding = PADDING, 
            time_mask_smooth_ms = TIME_MASK_SMOOTH_MS)
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Cleaning Audio Complete")
            write(self.save_clean_file_format, rate, reduced_noise)
            return True

        except Exception as e:
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
            
    """
    # ADD CLEAN AUDIO TO VIDEO
    """
    def add_audio_to_video(self):
        try:
            self.debug = Logger()
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Adding Clean Audio to Video in Progress...")
            clip = VideoFileClip(self.non_audio_path) # LOAD VIDEO CLIP
            audioclip = AudioFileClip(self.save_clean_file_format) # LOAD AUDIO CLIP
            videoclip = clip.set_audio(audioclip) # ADDING AUDIO TO THE VIDEO CLIP
            videoclip.write_videofile(MAIN_UPLOAD_FOLDER + self.main_path + CLEANED_AUDIO_WITH_VIDEO + "cleaned_" + self.filename, fps = 30, threads = 2, codec="libx264") # WRITE AUDIO TO VIDEO
            audioclip.close()
            clean_audio_video_file_path = MAIN_UPLOAD_FOLDER + self.main_path + CLEANED_AUDIO_WITH_VIDEO + "cleaned_" + self.filename
            self.debug.debug(AUDIO, AUDIO_SEGMENTATION_LOG, "Adding Clean Audio to Video Complete")
            return clean_audio_video_file_path

        except Exception as e:
            self.debug.error_log(AUDIO_SEGMENTATION_ERROR_LOG, e, AUDIO)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
