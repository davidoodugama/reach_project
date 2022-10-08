"""
# RDS DATABASE CONFIGURATIONS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Jul-21
"""

import pymysql
from Const.const import HOST, USER, PASS, RDS, RDS_ERROR_LOG, RDS_LOG
from Config.Logger.Logger import Logger
from flask import jsonify

"""
THIS CLASS HANDLES THE DATABASE CONNECTIONS AND UPDATES
"""
class Rds_Config:
    def __init__(self, db_name):
        try:
            self.debug = Logger()
            self.host = HOST
            self.username = USER
            self.password = PASS
            self.db_name = db_name
            self.__con__()
            self.__useDB__()
            self.debug.debug(RDS, RDS_LOG,"Started|Rds Connection success")
            
        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    """
    RDS CONNECTION
    """
    def __con__(self):
        self.db = pymysql.connect(host = self.host, user = self.username, password = self.password)
        self.cursor = self.db.cursor()
    
    """
    USE DATABASE
    """
    def __useDB__(self):
        sql = '''use %s''' % (self.db_name)
        self.cursor.execute(sql)

    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    
    """
    GET ALL DATA FOR THE SPECIFIC TABLE
    """
    def getAll(self, sql):
        try:
            self.cursor.execute(sql)
            out_put = self.cursor.fetchall()
            return out_put

        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def Update(self, sql):
        try:
            # sql = '''update %s
            #          set pre_status = '%s', score = %i
            #          where workOrderID = %i AND imageName = '%s'
            #         ''' % (
            #     tb_name,
            #     str(status),
            #     int(score),
            #     int(workOrderID),
            #     imageName
            # )
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

