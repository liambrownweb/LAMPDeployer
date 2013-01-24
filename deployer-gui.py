'''
Created on Jan 18, 2013

@author: lima
'''

import main.main, Tkinter, tkFileDialog, tkMessageBox

class deployerGui(main.main.view):
    '''
    classdocs
    '''
    _fields = None
    _tk = None
    _status_box = None

    def __init__(self):
        '''
        Constructor
        '''
        self._fields = {"-s":{
             "field":"_mysql_server",
             "label":"MySQL Server Hostname",
             "tk_type":"Entry",
             "func":lambda x: (len(x) and self._mysql_control.host_exists(x) and x) or None,
             "question": "Please enter the address of the MySQL server to use: ",
             "error":lambda x: "There is something wrong with that value. Please try again."},
            "-c":{
             "field":"_number_of_instances",
             "label":"Number of Instances",
             "tk_type":"Entry",
             "func":lambda x: int(''.join([i for i in x if i.isdigit()])),  # [i in "0123456789" for i in x] and int(x),
             "question":"Please enter the number of instances you want to deploy: ",
             "error":lambda x: "Invalid input, please enter a number between 1 and infinity."},
            "-u":{
             "field":"_mysql_admin_user_name",
             "label":"MySQL Admin Username",
             "tk_type":"Entry",
             "func":lambda x: len(x) and x,
             "question":"Please enter the MySQL administrator user name: ",
             "error":lambda x: "Invalid input, please enter a valid user name."},
            "-p":{
             "field":"_mysql_admin_user_password",
             "label":"Mysql Admin Password",
             "tk_type":"Entry",
             "func":lambda x: len(x) and x,
             "question":"Please enter the password for the MySQL administrator user: ",
             "error":lambda x: "Invalid input, please enter a valid password."},
            "-r":{
             "field":"_web_root",
             "label":"Web DocumentRoot",
             "tk_type":"dir_chooser",
             "func":lambda x: os.path.exists(x) and x,
             "question":"Please enter the location of the Web server document root: ",
             "error":lambda x: "The path " + x + " seems to have problems. Please check the path and try again."},
            "-i":{
             "field":"_instance_name",
             "label":"Instance Base Name",
             "tk_type":"Entry",
             "func":lambda x: len(x) and x,
             "question":"Please enter the base name you'd like to use for your new instances: ",
             "error":lambda x: "Invalid input, please enter a valid instance name."},
            "-f":{
             "field":"_tarfile_name",
             "label":"Output Archive",
             "tk_type":"Entry",
             "func":lambda x: os.path.isfile(x) and x,
             "question":"Please enter the name of the archive file to use for this install: ",
             "error":lambda x: "Invalid input, please enter a valid file name."}}

    def start(self):
        if self._controller == None:
            self._controller = main.main.deployer({'view':self})
        if self._tk == None:
            self._tk = Tkinter.Tk()
            self._tk.title("Deployer")
        col = 0
        for key, current_field in self._fields.iteritems():
            current_field["frame"] = Tkinter.Frame(self._tk)
            current_frame = Tkinter.Frame(current_field["frame"])
            Tkinter.Label(current_frame, text=current_field["label"], width=20).grid()
            current_frame.grid()
            if current_field["tk_type"]=="Entry":
                current_field["object"]=Tkinter.Entry(current_field["frame"])
            else:
                if current_field["tk_type"]=="dir_chooser":
                    current_field["object"]=Tkinter.Entry(current_field["frame"])
                    current_field["object"].choose = lambda: tkFileDialog.askdirectory(parent=self, initialdir="~", title="Select Directory") 
                    Tkinter.Button(current_field["frame"], text="Select", command=current_field["object"].choose).grid()                    
            current_field["object"].grid(row=0, column=1)
            current_field["frame"].grid(row = col / 2, column = col % 2)
            col += 1
        F = Tkinter.LabelFrame(self._tk, text="Output")        
        self._status_box = Tkinter.Text(F)
        self._status_box.config(state='disabled')
        F.grid(columnspan=2)
        self._status_box.grid()
        B = Tkinter.Button(self._tk, text="Execute", command=self.tryDeploy)
        B.grid()    
        self._tk.mainloop()
        
    def testMessage(self):
        self._controller.error("This is a test. Hello!", False)
        
    def tryDeploy(self):
        options = {}
        for current_key, current_field  in self._fields.iteritems():
            options[current_key]=current_field["object"].get()
        self._controller.deploy(options)
        
    def userMessage(self, message):
        self._status_box.config(state='normal')
        self._status_box.insert("end", message)
        self._status_box.config(state='disabled')
        
if __name__ == "__main__":
    interface = deployerGui()
    interface.start()
