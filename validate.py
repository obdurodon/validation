#!/usr/bin/python

# Devon Broglie
# script to run validators on project directories for Computational Methods in the Humanities

import os
import sys
import subprocess32
import urllib
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET

# global variables
directory = ''
dir_name = ''
paths = []
file_output = ''
save_output = None
namespaces = {'m':'http://www.w3.org/2005/07/css-validator'}

# ****************************** AUXILLARY METHODS ***********************

# get base URL for project site
def get_url(path):
    global dir_name
    file_path = path.split('/')
    filename = file_path[-1]
    url = 'http://www.obdurodon.org/' + dir_name + '/' + filename
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
def validate_html(file):
    global file_output
    '''
    url = get_url(file)
    command = "html-validator " + url + " --validator='http://html5.validator.nu'"
    output = run_command(command)
    file_output = file_output + "HTML VALIDATION: \n" + output + "\n\n"
    '''
    formatted_output = ''
    output = ''
    base_url = 'http://validator.w3.org/check'
    file_url = get_url(file)
    
    data = {}
    data['uri'] = file_url
    data['doctype'] = 'HTML5'
    data['output'] = 'soap12'
    url_values = urllib.urlencode(data)
    
    url = base_url + '?' + url_values
    response = urllib2.urlopen(url)
    
    output = response.read()
    
    #print output 
    
    root = ET.fromstring(output)
    
    
    formatted_output = 'Errors\n----------------------\n\n'
    
    error_count = int(root.find('.//{http://www.w3.org/2005/10/markup-validator}errorcount').text)
    
    if error_count == 0:
        formatted_output = formatted_output + "No errors.\n"
    else:
        for error in root.findall('.//{http://www.w3.org/2005/10/markup-validator}error'):
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/10/markup-validator}line').text.strip()
            col = error.find('.//{http://www.w3.org/2005/10/markup-validator}}col')
            if col is not None:
                formatted_output = formatted_output + ', '
                formatted_output = formatted_output + col.text.strip()
            formatted_output = formatted_output + ': '
            '''
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/10/markup-validator}}source').text.strip()
            formatted_output = formatted_output + '\n'
            '''
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/10/markup-validator}message').text.strip()
            formatted_output = formatted_output + '\n\n'
        
    formatted_output = formatted_output + '\nWarnings\n----------------------\n\n'
    
    warning_count = int(root.find('.//{http://www.w3.org/2005/10/markup-validator}warningcount').text)
    
    if warning_count == 0:
        formatted_output = formatted_output + 'No warnings.\n'
    else:
        for warning in root.findall('.//{http://www.w3.org/2005/10/markup-validator}warning'):
            line = warning.find('.//{http://www.w3.org/2005/10/markup-validator}line')
            if line is not None:
                formatted_output = formatted_output + warning.find('.//{http://www.w3.org/2005/10/markup-validator}line').text.strip()
            
                col = warning.find('.//{http://www.w3.org/2005/10/markup-validator}col')
                if col is not None:
                    formatted_output = formatted_output + ', '
                    formatted_output = formatted_output + col.text.strip()
                formatted_output = formatted_output + ': '
                '''
                formatted_output = formatted_output + warning.find('.{//http://www.w3.org/2005/10/markup-validator}source').text.strip()
                formatted_output = formatted_output + '\n'
                '''
                formatted_output = formatted_output + warning.find('.//{http://www.w3.org/2005/10/markup-validator}message').text.strip()
                formatted_output = formatted_output + '\n\n'
                
            else:
                if warning_count == 1:
                    formatted_output = formatted_output + 'No warnings.\n'
        
    print formatted_output
    
    file_output = file_output + "HTML VALIDATION: \n" + formatted_output + "\n\n"

# validate css files
def validate_css(file):
    # encode URL
    # make GET call to http://jigsaw.w3.org/css-validator/validator?uri= ENCODED URL &warning=0&profile=css3
    # process SOAP response
    global file_output
    formatted_output = ''
    output = ''
    base_url = 'http://jigsaw.w3.org/css-validator/validator'
    file_url = get_url(file)
    
    data = {}
    data['uri'] = file_url
    data['output'] = 'soap12'
    data['profile'] = 'css3'
    data['warning'] = 'no'
    url_values = urllib.urlencode(data)
    
    url = base_url + '?' + url_values
    response = urllib2.urlopen(url)
    
    output = response.read()
    root = ET.fromstring(output)
    
    formatted_output = 'Errors\n----------------------\n\n'
    
    error_count = int(root.find('.//{http://www.w3.org/2005/07/css-validator}errorcount').text)
    
    if error_count == 0:
        formatted_output = formatted_output + "No errors.\n"
    else:
        for error in root.findall('.//{http://www.w3.org/2005/07/css-validator}error'):
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/07/css-validator}line').text.strip()
            formatted_output = formatted_output + ': '
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/07/css-validator}context').text.strip()
            formatted_output = formatted_output + '\n'
            formatted_output = formatted_output + error.find('.//{http://www.w3.org/2005/07/css-validator}message').text.strip()
            formatted_output = formatted_output + '\n\n'
        
    formatted_output = formatted_output + '\nWarnings\n----------------------\n\n'
    
    warning_count = int(root.find('.//{http://www.w3.org/2005/07/css-validator}warningcount').text)
    
    if warning_count == 0:
        formatted_output = formatted_output + "No warnings.\n"
    else:
        for warning in root.findall('.//{http://www.w3.org/2005/07/css-validator}warning'):
            formatted_output = formatted_output + warning.find('.//{http://www.w3.org/2005/07/css-validator}line').text.strip()
            formatted_output = formatted_output + ': '
            formatted_output = formatted_output + warning.find('.//{http://www.w3.org/2005/07/css-validator}message').text.strip()
            formatted_output = formatted_output + '\n\n'
        
    print formatted_output
    
    file_output = file_output + "CSS VALIDATION: \n" + formatted_output + "\n\n"

# validate links for html pages
# need to filter out mailto links and settings displayed on each command
def check_links(file):
    global file_output
    output = ''
    command = 'checklink -s ' + file
    output = run_command(command)
    if 'Valid links' in output:
        file_output = file_output + "CHECKING LINKS: \n Valid links. \n\n"
        print 'Valid links.\n\n'
    else:
        file_output = file_output + "CHECKING LINKS: \n" + output + "\n\n"
        print output
    
# ****************************** MAIN LOGIC ******************************    

# check if path was specified
# check for trailing /
if (len(sys.argv) > 1):
    directory = sys.argv[1]
    if directory[-1] == '/':
        directory = directory[:-1]
    if (len(sys.argv) > 2):
        if sys.argv[2] == '-s':
            save_output = True
else:
    directory = os.getcwd()

# get just directory name
dir_path = directory.split('/')
dir_name = dir_path[-1]


# get file paths for directory
paths = get_filepaths(directory)

# loop over files
for path in paths:
    if (path.endswith('.html') or path.endswith('.xhtml')):
        if '/include/' not in path and '/inc/' not in path:
            print '*' * 80
            print 'FILE: ' + path + '\n\n'
            file_output = file_output + '\nFILE: ' + path + '\n\n'
            print 'HTML VALIDATION: \n'
            validate_html(path)
            print 'CSS VALIDATION: \n'
            validate_css(path)
            print '\nCHECKING LINKS: \n'
            check_links(path)
            
if save_output:
    # create file name
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = 'validation-' + dir_name+ '-' + date + '.txt'
    # open file
    f = open(filename, 'wb')
    # write output to file
    f.write(file_output)
    # close file
    f.close()