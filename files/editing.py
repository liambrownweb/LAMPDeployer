'''
Created on Jan 4, 2013

@author: Liam Brown
'''
import re

class editor(object):
    '''
    classdocs
    '''
    _file_control = None
    _file_contents = None

    def __init__(self):
        '''
        Constructor
        '''
    def openFile(self, filename):
        '''
        Opens a file for reading and writing.
        
        Accepts the file name as a parameter. This must be a correct relative or 
        absolute filename or it will not open. All other methods in this class
        require that this be done first, as it assigns the class's _file_control
        member.
        '''
        self._file_control = open(filename, 'r+')
        return True
    
    def readWholeFile(self):
        '''
        Reads the whole file as a single string.
        
        Assumes the openFile method has already been called, and reads the file
        directly into memory.
        '''
        self._file_control.seek(0)
        self._file_contents = self._file_control.read()
    
    def replaceText(self, expression, replacement):
        '''
        Replaces a regular expression with something else in the (already loaded) file.
        
        Requires two parameters, expression and replacement. Both are regular expressions
        in keeping with the conventions used in the Python re module. Consult that 
        module for further information.
        '''
        self._file_contents = re.sub(expression.encode('string-escape'),
                                     replacement.encode('string-escape'),
                                     self._file_contents)
        return True
    
    def saveFile(self):
        '''
        Saves the loaded file and closes the handler.
        '''
        filename = self._file_control.name
        self._file_control = open(filename, 'w')
        self._file_control.write(self._file_contents)
        self._file_control.close()
        return True    