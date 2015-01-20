#!/usr/bin/python

# Devon Broglie
# script to run validators on project directories for Computational Methods in the Humanities

import os
import sys
import subprocess32
import urllib
import urllib2


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
    print output
    return output
    
# validate html files
# https://www.npmjs.com/package/html-validator
def validate_html(file):
    url = get_url(file)
    command = "html-validator " + url + " --validator='http://html5.validator.nu'"
    output = run_command(command)
    #return output

# validate css files
def validate_css(file):
    # encode URL
    # make GET call to http://jigsaw.w3.org/css-validator/validator?uri= ENCODED URL &warning=0&profile=css3
    # process SOAP response
    output = ''
    base_url = 'http://jigsaw.w3.org/css-validator/validator'
    file_url = get_url(file)
    
    data = {}
    data['uri'] = file_url
    # data['output'] = 'soap12'
    data['output'] = 'text/plain'
    data['profile'] = 'css3'
    data['warning'] = 'no'
    url_values = urllib.urlencode(data)
    
    url = base_url + '?' + url_values    
    output = urllib2.urlopen(url)
    
    print output.read()

# validate links for html pages
# need to filter out mailto links and settings displayed on each command
def check_links(file):
    output = ''
    command = 'checklink -s ' + file
    output = run_command(command)
    #return output
    
# ****************************** MAIN LOGIC ******************************    

# check if path was specified
# check for trailing /
if (len(sys.argv) > 1):
    directory = sys.argv[1]
else:
    directory = os.getcwd()
    
# get file paths for directory
paths = get_filepaths(directory)

# loop over files
for path in paths:
    if (path.endswith('.html') or path.endswith('.xhtml')):
        if '/include/' not in path and '/inc/' not in path:
            '''
            # append path name
            html_output = html_output + '\n' + path
            # run html validator and append output
            html_output = html_output + '\n' + validate_html(path)
            # check links and append output
            html_output = html_output + '\n' + check_links(path) + '\n'
            '''
            print '*' * 80
            print 'FILE: ' + path + '\n'
            print 'HTML VALIDATION: \n'
            validate_html(path)
            print 'CSS VALIDATION: \n'
            validate_css(path)
            print '\nCHECKING LINKS: \n'
            check_links(path)
        # run css validator and append output
        #css_output = html_output + '\n' + validate_css(path)
        
        
        
# print output
#print html_output
#print css_output