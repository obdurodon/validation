#!/usr/bin/python

import multiprocessing
import time
import os
import sys
import urllib
import urllib2
import subprocess32

dir_name = ''

def get_filepaths(dir):
    file_paths = []  # List which will store all of the full file paths

    # Walk the tree.
    for root, directories, files in os.walk(dir):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths
    
def get_url(path):
    global dir_name
    subdir = False
    extended_path = ''
    url = ''
    file_path = path.split('/')
    
    for path in file_path:
        if subdir:
            extended_path = extended_path + '/' + path
        if path == dir_name:
            subdir = True
        
    url = 'http://www.obdurodon.org/' + dir_name + extended_path
    
    return url
    
def run_command(command):
    output = ''
    output = subprocess32.check_output(command, stderr=subprocess32.STDOUT, shell=True)
    return output
    
def html_validation(file):
    timeout_length = 120    
    output = ''
    base_url = 'http://validator.w3.org/check'
    file_url = get_url(file)
    
    data = {}
    data['uri'] = file_url
    data['doctype'] = 'HTML5'
    data['output'] = 'soap12'
    url_values = urllib.urlencode(data)
    
    url = base_url + '?' + url_values
    
    try:
        response = urllib2.urlopen(url, timeout = timeout_length)
    except urllib2.URLError:  
        print 'Connection timed out. Please try again in a few minutes.\n'
        return
       
    output = response.read()
    
    print 'Validated ' + file # + ' at ' + str(time.clock())
    
    return
    
def check_links(file):
    global file_output
    hosts_to_check = ['gutenberg']
    excluded_schemes = ['mailto:', 'about:legacy-compat', 'creativecommons']
    output = ''
    formatted_output = ''
    error_output = ''
    redirect_output = ''
    command = 'checklink -s ' + file
    output = run_command(command)
    
    print 'Checked links for ' + file
    
    return
    
if __name__ == '__main__':
    jobs = []
    directory = os.getcwd()
    
    dir_path = directory.split('/')
    dir_name = dir_path[-1]
    
    paths = get_filepaths(directory)
    
    start_time = time.time()
    print 'Starting multiprocessing...'
    
    for path in paths:
        if (path.endswith('.html') or path.endswith('.xhtml')):
            if '/include/' not in path and '/inc/' not in path:
                p = multiprocessing.Process(target=check_links, args=(path,))
                jobs.append(p)
                p.start()
    for j in jobs:
        j.join()
    
    end_time = time.time()
    duration = end_time - start_time
    print 'Ending multiprocessing at ' + str(duration)
    
    start_time = time.time()
    print 'Starting regular processing...'
    
    for path in paths:
        if (path.endswith('.html') or path.endswith('.xhtml')):
            if '/include/' not in path and '/inc/' not in path:
                check_links(path)
    
    end_time = time.time()
    duration = end_time - start_time
    print 'Ending regular processing at ' + str(duration)
        