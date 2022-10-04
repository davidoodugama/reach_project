"""
# AZURE DATABASE CONFIGURATIONS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-Sep-27
"""

import pymysql
from Const.const import HOST, USER_NAME, PASS, RDS, RDS_ERROR_LOG, RDS_LOG, SSL, AZURE_DB, AZURE_MYSQL_ERROR_LOG, AZURE_MYSQL_LOG
from Config.Logger.Logger import Logger
from flask import jsonify
import mysql.connector
from mysql.connector import errorcode

"""
THIS CLASS HANDLES THE DATABASE CONNECTIONS AND UPDATES
"""


# class Rds_Config:
class Azure_Config:
    def __init__(self, db_name):
        try:
            self.debug = Logger()
            # self.host = HOST
            # self.username = USER
            # self.password = PASS
            self.db_name = db_name
            self.azure_db_config = {
                'host': HOST,
                'user': USER_NAME,
                'password': PASS,
                'database': self.db_name,
                'client_flags': [mysql.connector.ClientFlag.SSL],
                'ssl_ca': SSL
            }
            self.__con__()
            # self.__useDB__()
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, "Started|Azure Connection success")
            # self.debug.debug(RDS, RDS_LOG, "Started|Rds Connection success")

        except Exception as e:
            # self.debug.error_log(RDS_ERROR_LOG, e, RDS)
            # self.debug.error_log(AZURE_MYSQL_ERROR_LOG, e, AZURE_DB)
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })

    """
    RDS/AZURE CONNECTION
    """

    def __con__(self):
        """ AZURE MYSQL CONFIGURATION """

        try:
            self.conn = mysql.connector.connect(**self.azure_db_config)
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, "Connection established")
            print("Connection established")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with the user name or password")
                # self.debug.error_log(AZURE_MYSQL_ERROR_LOG, err.errno, AZURE_DB)
                self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, err.errno)
                
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
                # self.debug.error_log(AZURE_MYSQL_ERROR_LOG, err.errno, AZURE_DB)
                self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, err.errno)
                
            else:
                # self.debug.error_log(AZURE_MYSQL_ERROR_LOG, err, AZURE_DB)
                self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, err)
        else:
            self.cursor = self.conn.cursor(dictionary=True)

        """ AZURE MYSQL CONFIGURATION """

        # """ AWS RDS CONFIGURATION """
        # # self.db = pymysql.connect(host = self.host, user = self.username, password = self.password)
        # # self.cursor = self.db.cursor()
        # """ AWS RDS CONFIGURATION """

    """
    USE DATABASE
    """

    # def __useDB__(self):
    #     sql = '''use %s''' % (self.db_name)
    #     self.cursor.execute(sql)

    """
    INSERT QUERY
    """
    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            # self.cursor.close()
            # self.conn.close()

        except Exception as e:
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })
            
    """
    GET DATA FOR THE SPECIFIC USER
    """
    def selectOne(self, sql):
        try:
            self.cursor.execute(sql)
            out_put = self.cursor.fetchall()
            self.conn.commit()
            # self.cursor.close()
            # self.conn.close()
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG,"selectOne|Query executed successfully.")
            return out_put

        except Exception as e:
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, e)
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
            self.conn.commit()
            # self.cursor.close()
            # self.conn.close()
            return out_put

        except Exception as e:
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })
    """
    UPDATE TABLE
    """
    def Update(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            # self.cursor.close()
            # self.conn.close()
            return True
        except Exception as e:
            self.debug.debug(AZURE_DB, AZURE_MYSQL_LOG, e)
            return jsonify({
                "error": 1,
                "code": 500,
                "data": "{0}".format(e)
            })
