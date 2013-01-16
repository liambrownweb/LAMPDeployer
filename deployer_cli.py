'''
Created on Jan 4, 2013

@author: lima
'''
from main import main
import sys, getopt

class cli(main.view):
    def userMessage(self, output):
        print(output)
        
    def initDeployment(self, args):
        '''
        The main function of the deployment program.
        '''
        try:
            opts, args = getopt.getopt(args, "hc:s:u:p:r:i:f:")
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        options = dict(opts)
        if "-h" in options:
            self.usage()
        else:
            sugarDeployer = main.deployer(None)
            sugarDeployer.connectView(self)
            sugarDeployer.deploy(options)    
    
    def safeInput(self, param):
        user_in = None
        user_out = None
        while not user_out:
            user_in = raw_input(param["question"])
            try:
                test = param["func"]
                user_out = test(user_in) or None
                if not user_out:
                    print(param["error"](user_in))                     
            except Exception:
                print(param["error"](user_in))  
        return user_out
    
    def usage(self,):
        print "Correct usage: " + __file__ + " -h | -c[count] -s [MySQL server] -u [MySQL username] -p [MySQL password] -r [web server doc root] -i [instance base name] -f [archive file]"

            

if __name__=='__main__':
    my_cli = cli();
    my_cli.initDeployment(sys.argv[1:])