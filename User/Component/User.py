"""
# HANDLING USERS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-July-25
"""

from Config.RDS_Config.DB_Config import Rds_Config
from Config.Logger.Logger import Logger
from flask import jsonify
from Const.const import USERDB, USERTB, CURRENT_TIMESTAMP, USER, USER_LOG, USER_ERROR_LOG

class User():
    def __init__(self, username, password):
        self.debug = Logger()
        self.username = username
        self.password = password
        self.rds = Rds_Config(USERDB)
        self.tb_name = USERTB
        self.role_id = None

    def verify_user(self):
        try:
            sql = """SELECT id, password, role_id, verified FROM {} WHERE username = '{}' """.format(self.tb_name, self.username)
            response = self.rds.selectOne(sql)
            self.debug.debug(USER, USER_LOG,"verify_user|Sql statment executed successfully for username " + self.username) 
            return response
        
        except Exception as e:
            self.debug.error_log(USER_ERROR_LOG, e, USER)
            return jsonify({
                "error": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })

    def register_user(self, username, email, name, contact, role):
        try:
            if 'IT' in username or 'it' in username and role == "Student":
                self.role_id = 30
                ACCEPTED = "YES"
                self.debug.debug(USER, USER_LOG,"register_user|Student role assigned for username: " + username) 
                
            elif role == "Lecturer":
                self.role_id = 20
                ACCEPTED = "NO"
                self.debug.debug(USER, USER_LOG,"register_user|Lecturer role assigned for username: " + username)
                
            elif role == "Admin": # ********************* IMPORTANT Dont show it in the FE *********************
                self.role_id = 10
                ACCEPTED = "NO"

            sql = """INSERT INTO {}(role_id, username, password, email, name, contact, verified, created_user, updated_user, updated_date) 
                    values({}, '{}', '{}', '{}', '{}', {}, '{}', '{}','{}', {})""".format(self.tb_name, self.role_id, self.username, self.password, email, name, contact, ACCEPTED, self.username, self.username, CURRENT_TIMESTAMP)                                                      
            response = self.rds.insert(sql)
            self.debug.debug(USER, USER_LOG,"register_user|User registered successfully for username: " + username)
            return response

        except Exception as e:
            self.debug.error_log(USER_ERROR_LOG, e, USER)
            return jsonify({
                "status": 1,
                "code": 500,
                "data" : "{0}".format(e)
                })
    