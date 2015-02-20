#!/usr/bin/python

# Devon Broglie
# script to run validators on project directories for Computational Methods in the Humanities

import os
import sys
import subprocess32
import urllib
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup, Doctype
import xml.etree.cElementTree as ET
import re
from optparse import OptionParser

# global variables
directory = ''
dir_name = ''
paths = []
file_output = ''
save_output = None

# ****************************** AUXILLARY METHODS ***********************

# get base URL for project site
def get_url(path):
    global dir_name
    url = ''
    file_path = path.split('/')
            
    if options.userdir:
        user = ''
        index = 0;
        for path in file_path:
            if path == 'home':
                user = file_path[index + 1]
            index = index + 1
            
        filename = file_path[-1]
        url = 'http://www.obdurodon.org/~' + user + '/' + filename
    else:
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
    
# method taken from answer to StackOverflow question
# http://stackoverflow.com/questions/2499358/get-document-doctype-with-beautifulsoup
def get_doctype(soup):
    items = [item for item in soup.contents if isinstance(item, Doctype)]
    return items[0] if items else None
    
# method uses techniques from link below to run command line processes
# http://stackoverflow.com/questions/4760215/running-shell-command-from-python-and-capturing-the-output
def run_command(command):
    output = ''
    output = subprocess32.check_output(command, stderr=subprocess32.STDOUT, shell=True)
    return output
    
# validate html files
def validate_html(file):
    global file_output
    html_5 = 'html'
    html_5_legacy = 'html SYSTEM "about:legacy-compat"'
    formatted_output = 'HTML VALIDATION: '
    
    # use BeautifulSoup to check doctype before validating
    html = open(file).read()
    soup = BeautifulSoup(html)
    
    doctype = ''
    doctype = get_doctype(soup)
    
    if (not options.legacy and (doctype == html_5 or doctype == html_5_legacy)) or options.legacy:      
        output = ''
        base_url = 'http://validator.w3.org/check'
        file_url = get_url(file)
        
        data = {}
        data['uri'] = file_url
        # only override if legacy switch is on, otherwise let detect and throw error if not html 5?
        if options.legacy:
            data['doctype'] = 'HTML5'
        data['output'] = 'soap12'
        url_values = urllib.urlencode(data)
        
        url = base_url + '?' + url_values
        response = urllib2.urlopen(url)
        
        output = response.read()
        
        root = ET.fromstring(output)
        
        error_count = int(root.find('.//{http://www.w3.org/2005/10/markup-validator}errorcount').text)
        warning_count = int(root.find('.//{http://www.w3.org/2005/10/markup-validator}warningcount').text)
        
        error_output = ''
        warning_output = ''
        
        if error_count > 0:
            for error in root.findall('.//{http://www.w3.org/2005/10/markup-validator}error'):
                line = error.find('.//{http://www.w3.org/2005/10/markup-validator}line')
                if line is not None:
                    error_output = error_output + line.text.strip()
                    col = error.find('.//{http://www.w3.org/2005/10/markup-validator}}col')
                    if col is not None:
                        error_output = error_output + ', '
                        error_output = error_output + col.text.strip()
                    error_output = error_output + ': '
                error_output = error_output + error.find('.//{http://www.w3.org/2005/10/markup-validator}message').text.strip()
                error_output = error_output + '\n'
              
        if warning_count > 0:
            for warning in root.findall('.//{http://www.w3.org/2005/10/markup-validator}warning'):
                line = warning.find('.//{http://www.w3.org/2005/10/markup-validator}line')
                if line is not None:
                    warning_output = warning_output + warning.find('.//{http://www.w3.org/2005/10/markup-validator}line').text.strip()
                    col = warning.find('.//{http://www.w3.org/2005/10/markup-validator}col')
                    if col is not None:
                        warning_output = warning_output + ', '
                        warning_output = warning_output + col.text.strip()
                    warning_output = warning_output + ': '
                message = warning.find('.//{http://www.w3.org/2005/10/markup-validator}message').text.strip()
                warning_output = warning_output + message.replace('\n', ' ').replace('\r', '')
                warning_output = warning_output + '\n'
        
        if not error_output and not warning_output:
            formatted_output = formatted_output + 'No errors. No warnings.\n'
        elif not error_output:
            formatted_output = formatted_output + '\nNo errors.\n'
            warning_output = '\nWarnings\n----------------------\n' + warning_output
            formatted_output = formatted_output + warning_output
        elif not warning_output:
            error_output = '\nErrors\n----------------------\n' + error_output
            formatted_output = formatted_output + error_output
            formatted_output = formatted_output + '\nNo warnings.\n'            
        else:
            error_output = '\nErrors\n----------------------\n' + error_output
            formatted_output = formatted_output + error_output
            warning_output = '\nWarnings\n----------------------\n' + warning_output
            formatted_output = formatted_output + warning_output
    else:
        formatted_output = formatted_output + 'Must have an HTML 5 doctype to validate or use legacy option.\n'
        
    print formatted_output
    
    file_output = file_output + formatted_output

# validate css files
def validate_css(file):
    # encode URL
    # make GET call to http://jigsaw.w3.org/css-validator/validator?uri= ENCODED URL &warning=0&profile=css3
    # process SOAP response
    global file_output
    formatted_output = 'CSS VALIDATION: '
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
        
    error_count = int(root.find('.//{http://www.w3.org/2005/07/css-validator}errorcount').text)
    warning_count = int(root.find('.//{http://www.w3.org/2005/07/css-validator}warningcount').text)
    
    error_output = ''
    warning_output = ''
    
    if error_count > 0:
        for error in root.findall('.//{http://www.w3.org/2005/07/css-validator}error'):
            error_output = error_output + error.find('.//{http://www.w3.org/2005/07/css-validator}line').text.strip()
            error_output = error_output + ': '
            context = error.find('.//{http://www.w3.org/2005/07/css-validator}context').text.strip()
            context = context.replace('\n', ' ').replace('\r', '')
            error_output = error_output + re.sub("\s\s+", " ", context)
            error_output = error_output + '\n'
            message = error.find('.//{http://www.w3.org/2005/07/css-validator}message').text.strip()
            message = message.replace('\n', ' ').replace('\r', '')
            error_output = error_output + re.sub("\s\s+", " ", message)
            error_output = error_output + '\n'
        
    if warning_count > 0:
        for warning in root.findall('.//{http://www.w3.org/2005/07/css-validator}warning'):
            warning_output = warning_output + warning.find('.//{http://www.w3.org/2005/07/css-validator}line').text.strip()
            warning_output = warning_output + ': '
            message = warning.find('.//{http://www.w3.org/2005/07/css-validator}message').text.strip()
            warning_output = warning_output + message.replace('\n', ' ').replace('\r', '')
            warning_output = warning_output + '\n'
        
    if not error_output and not warning_output:
        formatted_output = formatted_output + 'No errors. No warnings.\n'
    elif not error_output:
        formatted_output = formatted_output + '\nNo errors.\n'
        warning_output = '\nWarnings\n----------------------\n' + warning_output
        formatted_output = formatted_output + warning_output
    elif not warning_output:
        error_output = '\nErrors\n----------------------\n' + error_output
        formatted_output = formatted_output + error_output
        formatted_output = formatted_output + '\nNo warnings.\n'            
    else:
        error_output = '\nErrors\n----------------------\n' + error_output
        formatted_output = formatted_output + error_output
        warning_output = '\nWarnings\n----------------------\n' + warning_output
        formatted_output = formatted_output + warning_output
            
    print formatted_output
    
    file_output = file_output + formatted_output

# validate links for html pages
# need to filter out mailto links and settings displayed on each command
def check_links(file):
    global file_output
    domains = ['gutenberg']
    output = ''
    formatted_output = ''
    error_output = ''
    command = 'checklink -s ' + file
    output = run_command(command)
    if 'Valid links' in output:
        formatted_output = formatted_output + "LINK CHECKING: Valid links. \n"
    else:
        formatted_output = formatted_output + "LINK CHECKING: \n"
        
        lines = [line for line in output.split('\n') if line.strip() != '']
        
        count = 0
        
        while count < len(lines):
            if 'List of broken links' in lines[count]:
                count = count + 1
                while ((count < len(lines)) and ('redirect' not in lines[count]) and ('Anchors' not in lines[count])):
                    # boolean to check link not in forbidden domains
                    forbidden = False
                    
                    link = lines[count]
                    line_info = lines[count+1]
                    code = lines[count+2]
                    to_do = lines[count+3]
                    
                    for domain in domains:
                        if domain in link:
                            forbidden = True
                    
                    if not forbidden:
                        if 'robots.txt' in code:
                            url = urllib2.urlopen(link)
                            url_code = url.getcode()
                            
                            if url_code != 200:
                                error_output = error_output + link + '\n' + line_info + '\n'
                                error_output = error_output + '\tCode:' + url_code + '\n'
                                # put some message 
                                
                        else:
                            error_output = error_output + link + '\n' + line_info + '\n' + code + '\n' + to_do + '\n'
                    else:
                        error_output = error_output + link + '\n'+ line_info + '\n'
                        error_output = error_output + '\tTo do: Must check manually. Site forbids validator.\n'
                    
                    count = count + 4
            else:
                count = count + 1;
                
        formatted_output = formatted_output + '\n' + 'List of broken links: \n' + error_output 
        
    print formatted_output
    
    file_output = file_output + formatted_output
    
# ****************************** MAIN LOGIC ******************************    

# setup command line argument parser
parser = OptionParser()

parser.add_option('-o', '--output', action='store_true', dest='save_output', default=False, help='save output to a log file in current directory')
parser.add_option('-d', '--directory', dest='directory', help='run validator in DIRECTORY', metavar='DIRECTORY')
parser.add_option('-l', '--legacy', action='store_true', dest='legacy', default=False, help='override doctype declaration as html5')
parser.add_option('-u', '--userdir', action='store_true', dest='userdir', default=False, help='run validator in a public_html user directory')
parser.add_option('-s', '--skiplinks', action='store_true', dest='skiplinks', default=False, help='skip link checking')
(options, args) = parser.parse_args()

# check if path was specified
# check for trailing /

if options.directory is not None:
    directory = options.directory
    if directory[-1] == '/':
        directory = directory[:-1]
else:
    directory = os.getcwd()

# get just directory name
dir_path = directory.split('/')
dir_name = dir_path[-1]


# get file paths for directory
paths = get_filepaths(directory)

# loop over files for html/link validation
for path in paths:
    if (path.endswith('.html') or path.endswith('.xhtml')):
        if '/include/' not in path and '/inc/' not in path:
            print '*' * 80
            print 'FILE: ' + path + '\n'
            file_output = file_output + '\nFILE: ' + path + '\n'
            validate_html(path)
            if not options.skiplinks:
                check_links(path)
                
# loop over files for css validation
for path in paths:
    if path.endswith('.css'):
        print '*' * 80
        print 'FILE: ' + path + '\n'
        file_output = file_output + '\nFILE: ' + path + '\n'
        validate_css(path)
            
if options.save_output:
    # create file name
    date = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = 'validation-' + dir_name+ '-' + date + '.txt'
    # open file
    f = open(filename, 'wb')
    # write output to file
    f.write(file_output)
    # close file
    f.close()