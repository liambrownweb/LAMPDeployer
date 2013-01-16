'''
Created on Jan 4, 2013

@author: Liam Brown
'''
import DB, files, getopt, os, sys, tarfile

class deployer(object):

    _mysql_control = None
    _mysql_editor = None
    _mysql_user_params = {"name": None, "password": None}
    _mysql_dump_file = "database.sql"
    _mysql_server = None
    _new_user_params = {"name": None, "password": None}
    _number_of_instances = None
    _web_root = None
    _file_destination = None
    _config_file_name = None
    _instance_name = None
    _inputs_required = None
    
    def __init__(self, params):
        '''
        Constructor
        '''
        self._mysql_control = DB.mysql.mysql(None)
        self._file_editor = files.editing.editor()
        self._inputs_required = [{"param":"-s", 
                                  "field":"_mysql_server",
                                  "func":lambda x: (len(x) and self._mysql_control.host_exists(x)) or None, 
                                  "question": "Please enter the address of the MySQL server to use: ",
                                  "error":lambda x: "The server "+x+" does not respond. Please try again."},
                                 {"param":"-c",
                                  "field":"_number_of_instances",
                                  "func":lambda x: [i in "0123456789" for i in x] and int(x),
                                  "question":"Please enter the number of instances you want to deploy: ",
                                  "error":lambda x: "Invalid input, please enter a number between 1 and infinity."}]

    def error(self, message):
        '''
        Standardizes error messages and provides a clean exit for any error.
        
        Takes message, a string (or something stringable) to print to stdout.
        '''
        if not type(message) == 'str':
            msg = str(message)
        else:
            msg = message
        print "\n" + msg + "\n"
        sys.exit(2)
    
    def importDatabase(self, instance_name, dump_file, user, password):
        '''
        Imports the database dump into a new DB
    
        Takes a string, instance_name, as its parameter. Creates a new MySQL database with instance_name as its name, imports the database dump into it, and grants the training DB user all permissions to the new database.
        '''
        self._mysql_control.create_db(instance_name, True)
        self._mysql_control.importDump(user, password, instance_name, dump_file)
        return True
    
    def loop(self):
        '''
        The loop for batch setups. Typically called by deploy().
        '''
        count = self._number_of_instances
        self._mysql_control.connect_db(self._mysql_server, self._mysql_user_params["user"], self.mysql_user_params["password"])
        self._mysql_control.create_user(self._new_user_params["name"], self._new_user_params["password"])
        for i in range(0, count):
            instance_name = "sugarcrm_training_" + str(i)
            self.unzipFiles(self._file_destination)
            self.importDatabase(instance_name, self._mysql_dump_file, self._mysql_user_params["user"], self._mysql_user_params["password"])
            self.grantAccess(self._new_user_params["name"], self._new_user_params["password"], instance_name + ".*", "ALL")
            self.updateFiles(self._instance_name)
    
    def deploy(self, argv):
        '''
        The main function of the deployment program.
        '''
        try:
            opts, args = getopt.getopt(argv, "hc:s:u:p:r:i:")
        except getopt.GetoptError:
            print(opts)
            self.usage()
            sys.exit(2)
        options = dict(opts)
        if "-h" in options:
            self.usage()
        else:
            try:
                self._new_user_params["name"] = "sugartraining"
                self._new_user_params["password"] = "sugar12345"
                if "-s" in options:
                    self._mysql_server = options["-s"]
                else:
                    self._mysql_server = self.safeInput(self._inputs_required[0])
                if "-c" in options:
                    self._number_of_instances = options["-c"]
                else:
                    self._mysql_server = self.safeInput(self._inputs_required[1])
                if "-r" in options:
                    self._web_root = options["-r"]
                else:
                    while self._web_root == None:
                        user_in = raw_input("Please enter the location of the html document root: ")
                        if os.path.exists(user_in):
                            self._web_root = user_in
                        else: 
                            print("The path " + user_in +" seems to have problems. Please check the path and try again.")
                if "-i" in options:
                    self._instance_name = options["-i"]
                else:
                    while self._instance_name == None:
                        user_in = raw_input("Please enter the base name you'd like to use for your new instances: ")
                        if len(user_in) > 0:
                            self._instance_name = user_in
                        else:
                            print("That input is invalid. Please try again.")                            
                self._file_destination = self._web_root + self._instance_name
                self.loop()
            except Exception as e:
                self.error(e.message)
    
    def grantAccess(self, user, pwd, db, host="localhost"):
        self._mysql_control.grant_user(user, pwd, db, "ALL", host)
        
    def safeInput(self, param):
        user_in = None
        user_out = None
        while user_out == None:
            user_in = raw_input(param["question"])
            try:
                test = param["func"]
                user_out = test(user_in) or None
                if not user_out:
                    print(param["error"](user_in))                     
            except Exception:
                print(param["error"](user_in))  
    
    def unzipFiles(self, dest_path):
        '''
        Unzips the archive into a directory.
    
        This only works on tar files currently, because I don't want to muddle 
        permissions or other garbage, and tar files preserve the rather important 
        Linux permissions. Returns True if successful, false otherwise.
        '''
        zip_file_name = "sugarcrm.tar.gz"
        try:
            file_handler = tarfile.open(zip_file_name, 'r:*')
            file_handler.extractall(dest_path)
        except IOError as e:
            self.error(e.strerror + ": " + e.filename)
        except tarfile.ReadError as e:
            self.error(e.message + ": " + zip_file_name)
        return True
    
    def updateFiles(self, instance_name):
        replacements = {"uname":self._new_user_params["name"], "pwd":self._new_user_params["pwd"]}
        if self._file_editor.openFile(self._file_destination + "/" + self._config_file_name):
            self._file_editor.readWholeFile()
        for expression, replacement in replacements:
            self._file_editor.replaceText(expression, replacement)
        self._file_editor.saveFile()
        return True
    
def usage():
    print "Correct usage: " + __file__ + " -h | -c[count] -s [MySQL server] -u [MySQL username] -p [MySQL password]"
    
if __name__ == '__main__':
    sugarDeployer = deployer(None)
    sugarDeployer.deploy(sys.argv[1:])
