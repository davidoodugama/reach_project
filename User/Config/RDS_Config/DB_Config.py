"""
# RDS DATABASE CONFIGURATIONS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-21
"""

import pymysql
from Const.const import HOST, USERNAME, PASS, RDS, RDS_ERROR_LOG, RDS_LOG
from Config.Logger.Logger import Logger
from flask import jsonify
import json

"""
THIS CLASS HANDLES THE DATABASE CONNECTIONS AND UPDATES
"""
class Rds_Config:
    def __init__(self, db_name):
        try:
            self.debug = Logger()
            self.host = HOST
            self.username = USERNAME
            self.password = PASS
            self.db_name = db_name
            self.__con__()
            self.__useDB__()

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    """
    RDS CONNECTION OBJECT
    """
    def __con__(self):
        try:
            self.db = pymysql.connect(host = self.host, user = self.username, password = self.password)
            self.cursor = self.db.cursor(pymysql.cursors.DictCursor)
            self.debug.debug(RDS, RDS_LOG,"__con__|Rds Connection success")

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    
    """
    USE DATABASE
    """
    def __useDB__(self):
        try:
            sql = '''use %s''' % (self.db_name)
            self.cursor.execute(sql)
            self.debug.debug(RDS, RDS_LOG,"__useDB__|Database " + self.db_name + " selected")
            
        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    
    """
    GET DATA FOR THE SPECIFIC USER
    """
    def selectOne(self, sql):
        try:
            self.cursor.execute(sql)
            out_put = self.cursor.fetchone()
            self.debug.debug(RDS, RDS_LOG,"selectOne|Query executed successfully.")
            return out_put

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    
    """
    GET ALL DATA
    """
    def selectAll(self, sql):
        try:
            self.cursor.execute(sql)
            out_put = self.cursor.fetchall()
            self.debug.debug(RDS, RDS_LOG,"selectAll|Query executed successfully.")
            return out_put

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.debug.debug(RDS, RDS_LOG,"insert|Query executed successfully.")

            return jsonify({
                "error": 0,
                "code": 200,
                "data" : "Database updated"
                })

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def update(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            self.debug.debug(RDS, RDS_LOG,"update|Query executed successfully.")

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })