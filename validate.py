# Devon Broglie
# script to run validators on project directories for Computational Methods in the Humanities

import os
import sys
import subprocess32
from multiprocessing import Process
import time

# global variables
directory = ''
paths = []
html_output = 'HTML VALIDATION\n'
css_output = 'CSS VALIDATION\n'

# ****************************** AUXILLARY METHODS ***********************

# get base URL for project site
def get_url(path):
    dir_path = directory.split('/')
    dir_name = dir_path[-1]
    file_path = path.split('/')
    filename = file_path[-1]
    url = 'http://' + dir_name + '.obdurodon.org/' + filename
    return url

# method taken from answer to StackOverflow question at link below, MAY WANT TO MODIFY TO ONLY DO HTML AND INCLUDES
# http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory-in-python
def get_filepaths(dir):
    file_paths = []  # List which will store all of the full file paths

    # Walk the tree.
    for root, directories, files in os.walk(dir):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths

# method uses techniques from link below to run command line processes
# http://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output
def run_command(command):
    output = ''
    output = subprocess32.check_output(command, stderr=subprocess32.STDOUT, shell=True)
    return output
    
# validate html files
# https://www.npmjs.com/package/html-validator
def validate_html(file):
    url = get_url(file)
    command = "html-validator " + url + " --validator='http://html5.validator.nu'"
    output = run_command(command)
    return output

# validate css files
def validate_css(file):
    # encode URL
    # make GET call to http://jigsaw.w3.org/css-validator/validator?uri= ENCODED URL &warning=0&profile=css3
    # process SOAP response
    output = ''
    return output

# validate links for html pages
def check_links(file):
    output = ''
    return output
    
# ****************************** MAIN LOGIC ******************************    

# check if path was specified
if (len(sys.argv) > 1):
    directory = sys.argv[1]
else:
    directory = os.getcwd()
    
# get file paths for directory
paths = get_filepaths(directory)

# loop over files
for path in paths:
    if (path.endswith('.html') or path.endswith('.xhtml')):
        if 'include' not in path:
            # append path name
            html_output = html_output + '\n' + path
            # run html validator and append output
            html_output = html_output + '\n' + validate_html(path)
        # run css validator and append output
        css_output = html_output + '\n' + validate_css(path)
        # check links and append output
        html_output = html_output + '\n' + check_links(path)
        
        
# print output
print html_output
print css_output