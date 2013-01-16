'''
Created on Jan 4, 2013

@author: lima
'''
from main import main
import sys

if __name__=='__main__':
    sugarDeployer = main.deployer(None)
    sugarDeployer.deploy(sys.argv[1:])