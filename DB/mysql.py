'''
Created on Jan 4, 2013

@author: Liam Brown
'''
import MySQLdb
import subprocess

class mysql(object):
    '''
    Simple wrapper for the MySQLdb functionality needed for the deployer.
    '''
    _connector = None
    _cursor = None

    def __init__(self,params):
        '''
        Constructor
        '''
        
    def connect_db(self, host, uname, password, database=None):
        if self._connector is None:
            if database is None:
                self._connector = MySQLdb.connect(host, uname, password)
            else:
                self._connector = MySQLdb.connect(host, uname, password, database)
    
    def create_db(self, db_name, replace=False):
        if replace:
            self.drop_db(db_name)
        query_string = "CREATE DATABASE IF NOT EXISTS "+db_name
        self.query(query_string)
        
    def drop_db(self, db_name):
        query_string = "DROP DATABASE IF EXISTS "+db_name
        self.query(query_string)
    
    def create_user(self, user_name, pwd, host="localhost"):
        self.grant_user(user_name, pwd, "*.*", "USAGE", host)
        self.drop_user(user_name, host)
        query_string = "CREATE USER '"+user_name+"'@'"+host+"' IDENTIFIED BY '"+pwd+"'"
        self.query(query_string)
    
    def drop_user(self, user_name, host="localhost"):
        query_string = "DROP USER '"+user_name+"'@'"+host+"'"
        self.query(query_string)
    
    def grant_user(self, user_name, pwd, target, privileges, host="localhost"):
        query_string = "GRANT "+privileges+" ON "+target+" TO '"+user_name+"'@'"+host+"'"
        print(query_string)
        self.query(query_string)
        
    def host_exists(self, host):
        return True
        
    def importDump(self, user_name, pwd, target, dump_file):
        proc = subprocess.Popen(["mysql", "--user=%s" % user_name, "--password=%s" % pwd, "database"], stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
        out, err = proc.communicate(file(dump_file).read())
        return out
        
    def query(self, query_string):
        if self._cursor is None:
            self._cursor = self._connector.cursor()
        self._cursor.execute(query_string)
        return True