'''
Created on Jan 4, 2013

@author: Liam Brown
'''
import DB, files, getopt, os, sys, tarfile, traceback

class view():
    '''
    An abstract class for views to connect to the deployer
    '''
    def userMessage(self, output):
        raise NotImplementedError("This is an interface method. You need to implement this.") 
    
class deployer(object):

    _view = None
    _mysql_control = None
    _mysql_editor = None
    _mysql_admin_user_name = None
    _mysql_admin_user_password = None
    _mysql_dump_file = "database.sql"
    _mysql_server = None
    _new_user_params = {"name": None, "password": None}
    _number_of_instances = 1
    _tarfile_name = None
    _web_root = None
    _file_destination = None
    _config_file_name = "config.php"
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
                                  "func":lambda x: (len(x) and self._mysql_control.host_exists(x) and x) or None,
                                  "question": "Please enter the address of the MySQL server to use: ",
                                  "error":lambda x: "There is something wrong with that value. Please try again."},
                                 {"param":"-c",
                                  "field":"_number_of_instances",
                                  "func":lambda x: int(''.join([i for i in x if i.isdigit()])),  # [i in "0123456789" for i in x] and int(x),
                                  "question":"Please enter the number of instances you want to deploy: ",
                                  "error":lambda x: "Invalid input, please enter a number between 1 and infinity."},
                                 {"param":"-u",
                                  "field":"_mysql_admin_user_name",
                                  "func":lambda x: len(x) and x,
                                  "question":"Please enter the MySQL administrator user name: ",
                                  "error":lambda x: "Invalid input, please enter a valid user name."},
                                 {"param":"-p",
                                  "field":"_mysql_admin_user_password",
                                  "func":lambda x: len(x) and x,
                                  "question":"Please enter the password for the MySQL administrator user: ",
                                  "error":lambda x: "Invalid input, please enter a valid password."},
                                 {"param":"-r",
                                  "field":"_web_root",
                                  "func":lambda x: os.path.exists(x) and x,
                                  "question":"Please enter the location of the Web server document root: ",
                                  "error":lambda x: "The path " + x + " seems to have problems. Please check the path and try again."},
                                 {"param":"-i",
                                  "field":"_instance_name",
                                  "func":lambda x: len(x) and x,
                                  "question":"Please enter the base name you'd like to use for your new instances: ",
                                  "error":lambda x: "Invalid input, please enter a valid instance name."},
                                 {"param":"-f",
                                  "field":"_tarfile_name",
                                  "func":lambda x: os.path.isfile(x) and x,
                                  "question":"Please enter the name of the archive file to use for this install: ",
                                  "error":lambda x: "Invalid input, please enter a valid file name."}]

    def connectView(self, view):
        self._view = view
        
    def error(self, message):
        '''
        Standardizes error messages and provides a clean exit for any error.
        
        Takes message, a string (or something stringable) to print to stdout.
        '''
        if not type(message) == 'str':
            msg = str(message)
        else:
            msg = message
        self._view.userMessage("\n" + msg + "\n" + traceback.print_exc(file=sys.stdout))
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
        self._mysql_control.connect_db(self._mysql_server, self._mysql_admin_user_name, self._mysql_admin_user_password)
        self._mysql_control.create_user(self._new_user_params["name"], self._new_user_params["password"])
        for i in range(0, int(self._number_of_instances)):
            self.singleSetup(i)
            
    def singleSetup(self, i):
        self._mysql_control.connect_db(self._mysql_server, self._mysql_admin_user_name, self._mysql_admin_user_password)
        self._mysql_control.create_user(self._new_user_params["name"], self._new_user_params["password"])
        instance_name = self._instance_name + "_" + str(i)
        self._view.userMessage("Setting up instance '" + instance_name + "'")
        if not self._web_root[-1] == "/":
            self._web_root += "/"
        self._file_destination = self._web_root + instance_name            
        self._view.userMessage("Attempting to unpack files to " + self._file_destination)
        self.unzipFiles(self._file_destination)
        self._view.userMessage("Importing database to " + instance_name)
        self.importDatabase(instance_name, self._file_destination + "/" + self._mysql_dump_file, self._mysql_admin_user_name, self._mysql_admin_user_password)
        self._view.userMessage("Granting database permissions to instance DB user")
        self.grantAccess(self._new_user_params["name"], self._new_user_params["password"], instance_name + ".*", "%")
        self._view.userMessage("Updating config files")
        self.updateFiles(instance_name)
            
    def replace(self, options):
        try:
            self._new_user_params["name"] = "sugartraining"
            self._new_user_params["password"] = "sugar12345"
            for current_option in self._inputs_required:
                if current_option["param"] in options:
                    setattr(self, str(current_option["field"]), options[current_option["param"]])
                else:
                    setattr(self, str(current_option["field"]), self._view.safeInput(current_option))
            self._view.userMessage("Starting loop: ")
            '''
            Here _number_of_instances is really instance_number; we're replacing a single instance.
            '''
            self.singleSetup(self._number_of_instances)
        except Exception as e:
            self.error(e.message)
               
    def deploy(self, options):
        try:
            self._new_user_params["name"] = "sugartraining"
            self._new_user_params["password"] = "sugar12345"
            for current_option in self._inputs_required:
                if current_option["param"] in options:
                    setattr(self, str(current_option["field"]), options[current_option["param"]])
                else:
                    setattr(self, str(current_option["field"]), self._view.safeInput(current_option))
            self._view.userMessage("Starting loop: ")
            self.loop()
        except Exception as e:
            self.error(e.message)
    
    def grantAccess(self, user, pwd, db, host="%"):
        self._mysql_control.grant_user(user, pwd, db, "ALL", host)
    
    def unzipFiles(self, dest_path):
        '''
        Unzips the archive into a directory.
    
        This only works on tar files currently, because I don't want to muddle 
        permissions or other garbage, and tar files preserve the rather important 
        Linux permissions. Returns True if successful, false otherwise.
        '''
        zip_file_name = self._tarfile_name
        try:
            file_handler = tarfile.open(zip_file_name, 'r:*')
            file_handler.extractall(dest_path)
        except IOError as e:
            self.error(e.strerror + ": " + e.filename)
        except tarfile.ReadError as e:
            self.error(e.message + ": " + zip_file_name)
        return True
    
    def updateFiles(self, instance_name):
        replacements = {"uname":self._new_user_params["name"],
                        "upwd":self._new_user_params["password"],
                        "hname":self._mysql_server,
                        "dbname":instance_name}
        if self._file_editor.openFile(self._file_destination + "/" + self._config_file_name):
            self._file_editor.readWholeFile()
        for expression, replacement in replacements.iteritems():
            self._file_editor.replaceText(expression, replacement)
        self._file_editor.saveFile()
        return True
        
if __name__ == '__main__':
    sugarDeployer = deployer(None)
    sugarDeployer.deploy(sys.argv[1:])
