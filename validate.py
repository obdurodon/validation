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
    subdir = False
    extended_path = ''
    url = ''
    file_path = path.split('/')
            
    if options.userdir:
        user = ''
        index = 0;
        for path in file_path:
            if subdir:
                extended_path = extended_path + '/' + path
            if path == 'home':
                user = file_path[index + 1]
            if path == 'public_html':
                subdir = True
            index = index + 1
            
        url = 'http://www.obdurodon.org/~' + user + extended_path
    else:
        for path in file_path:
            if subdir:
                extended_path = extended_path + '/' + path
            if path == dir_name:
                subdir = True
            
        url = 'http://www.obdurodon.org/' + dir_name + extended_path
    
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
        
        if not options.debug:
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
            formatted_output = output
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
    
    if not options.debug:
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
                
    else :
        formatted_output = output
    
    print formatted_output
    
    file_output = file_output + formatted_output

# validate links for html pages
# need to filter out mailto links and settings displayed on each command
def check_links(file):
    global file_output
    man_domains = ['gutenberg']
    exclude_domains = ['mailto']
    output = ''
    formatted_output = ''
    error_output = ''
    redirect_output = ''
    command = 'checklink -s ' + file
    output = run_command(command)
    
    if not options.debug:
        lines = output.split('\n')
        #lines = [line for line in output.split('\n') if line.strip() != '']
        
        count = 0
        
        found_broken = False
        
        while count < len(lines) and not found_broken:
            if 'List of broken links' in lines[count]:
                found_broken = True
                count = count + 2
                while ((count < len(lines)) and ('redirect' not in lines[count]) and ('Anchors' not in lines[count])):
                    # boolean to check link not in forbidden domains
                    forbidden = False
                    exclude = False
                    
                    link = lines[count]
                    
                    if '->' in lines[count+1]:
                        link = link + '\n' + lines[count+1]
                        count = count + 1
                        
                    if 'file:///' in link:
                        link = link[7:]
                        
                    line_info = lines[count+1]
                    code = lines[count+2]
                    
                    td_count = count + 2
                    #to_do = ''
                    while (lines[td_count + 1] != '') and ('Anchors' not in lines[td_count + 1]) and ('redirect' not in lines[td_count + 1]):
                        td_count = td_count + 1
                        #line = lines[td_count].strip('\n')
                        #to_do = to_do + line
                    #to_do = re.sub( '\s+', ' ', to_do).strip()
                    
                    
                    count = td_count
                    
                    for domain in man_domains:
                        if domain in link:
                            forbidden = True
                            break
                    for domain in exclude_domains:
                        if domain in link:
                            exclude = True
                            break
                    if not exclude:
                        if not forbidden:
                            if 'robots.txt' in code:
                                url = ''
                                if '->' in link:
                                    new_line_ind = link.find('\n')
                                    new_line_ind = new_line_ind + 4
                                    url = link[new_line_ind:]
                                else:
                                    url = link
                                try:
                                    open_link = urllib2.urlopen(url)
                                    url_code = open_link.getcode()
                                except urllib2.HTTPError, e:
                                    url_code = e.code
                                if url_code != 200:
                                    error_output = error_output + link + '\n' + line_info + '\n'
                                    error_output = error_output + '  Code: ' + str(url_code) + '\n'
                                    
                            else:
                                error_output = error_output + link + '\n' + line_info + '\n' + code + '\n'
                        else:
                            error_output = error_output + link + '\n' + line_info + '\n'
                            error_output = error_output + ' To do: Must check manually. Site forbids validator.\n'
                    
                    count = count + 1
                    
                    if lines[count] == '':
                        count = count + 1;
                    
                if 'List of redirects' in lines[count]:
                    count = count + 2
                    
                while ((count < len(lines)) and ('Anchors' not in lines[count])):
                    link = lines[count]
                    if '->' in lines[count+1]:
                        link = link + '\n' + lines[count+1]
                        count = count + 1
                        
                    line_info = lines[count+1]
                    code = lines[count+2]
                    
                    td_count = count + 2
                    #to_do = ''
                    while (lines[td_count + 1] != '') and ('Anchors' not in lines[td_count + 1]):
                        td_count = td_count + 1
                        #line = lines[td_count].strip('\n')
                        #to_do = to_do + line
                    #to_do = re.sub( '\s+', ' ', to_do).strip()
                    
                    redirect_output = redirect_output + link + '\n' + line_info + '\n' + code + '\n'
                    
                    count = td_count + 1
                    
                    if lines[count] == '':
                        count = count + 1                    
            elif 'List of redirects' in lines[count]:
                count = count + 2
                
                while ((count < len(lines)) and ('Anchors' not in lines[count])):
                    link = lines[count]
                    if '->' in lines[count+1]:
                        link = link + '\n' + lines[count+1]
                        count = count + 1
                        
                    line_info = lines[count+1]
                    code = lines[count+2]
                    td_count = count + 2
                    #to_do = ''
                    while (lines[td_count + 1] != '') and ('Anchors' not in lines[td_count + 1]):
                        td_count = td_count + 1
                        #line = lines[td_count].strip('\n')
                        #to_do = to_do + line
                    #to_do = re.sub( '\s+', ' ', to_do).strip()
                    
                    redirect_output = redirect_output + link + '\n' + line_info + '\n' + code + '\n'
                    
                    count = td_count + 1
                    
                    if lines[count] == '':
                        count = count + 1
            else:
                count = count + 1
        
        if error_output and redirect_output:
            formatted_output = formatted_output + "LINK CHECKING: \n"
            formatted_output = formatted_output + 'List of broken links:\n----------------------\n' + error_output
            formatted_output = formatted_output + '\nList of redirects:\n----------------------\n' + redirect_output
        elif error_output:
            formatted_output = formatted_output + "LINK CHECKING: \n"
            formatted_output = formatted_output + 'List of broken links:\n----------------------\n' + error_output
        elif redirect_output:
            formatted_output = formatted_output + "LINK CHECKING: \n"
            formatted_output = formatted_output + 'List of redirects:\n----------------------\n' + redirect_output
        else:
            formatted_output = formatted_output + "LINK CHECKING: Valid links. \n"
    else:
        formatted_output = output
        
    print formatted_output
    
    file_output = file_output + formatted_output
    
# ****************************** MAIN LOGIC ******************************    

# setup command line argument parser
parser = OptionParser()

parser.add_option('-s', '--save', action='store_true', dest='save_output', default=False, help='save output to a log file in current directory')
parser.add_option('-p', '--path', dest='directory', help='run validator in directory specified in PATH', metavar='PATH')
parser.add_option('-o', '--override', action='store_true', dest='legacy', default=False, help='override doctype declaration as html5')
parser.add_option('-u', '--userdir', action='store_true', dest='userdir', default=False, help='run validator in a public_html user directory')
parser.add_option('-w', '--web', action='store_true', dest='skiphtml', default=False, help='skip web (html) validation')
parser.add_option('-l', '--links', action='store_true', dest='skiplinks', default=False, help='skip link checking')
parser.add_option('-c', '--css', action='store_true', dest='skipcss', default=False, help='skip css validation')
parser.add_option('-d', '--debug', action='store_true', dest='debug', default=False, help='display unformatted output for debugging purposes')
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

divider = '*' * 80
# loop over files for html/link validation
for path in paths:
    if (path.endswith('.html') or path.endswith('.xhtml')):
        if '/include/' not in path and '/inc/' not in path:
            print divider
            print 'FILE: ' + path + '\n'
            file_output = file_output + divider + '\nFILE: ' + path + '\n'
            if not options.skiphtml:
                validate_html(path)
            if not options.skiplinks:
                check_links(path)
                
# loop over files for css validation
if not options.skipcss:
    for path in paths:
        if path.endswith('.css'):
            print divider
            print 'FILE: ' + path + '\n'
            file_output = file_output + divider + '\nFILE: ' + path + '\n'
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