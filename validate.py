# Devon Broglie
# script to run validators on project directories for Computational Methods in the Humanities

import os
import sys
import subprocess

vnu_path = 'vnu/vnu.jar'

# ****************************** AUXILLARY METHODS ***********************

# method taken from answer to StackOverflow question at link below
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
    # instantiate a startupinfo obj so command terminals aren't opened for each process
    startupinfo = subprocess.STARTUPINFO()
    # set the use show window flag, might make conditional on being in Windows
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, startupinfo=startupinfo)
    
    for line in iter(p.stdout.readline, b''):
        output = output + line
    
    return output

# validate html files
def validate_html(file):
    command = 'java -cp ' + vnu_path + ' nu.validator.client.HttpClient ' + file
    output = run_command(command)
    return output

# validate html files
def validate_css(file):
    output = ''
    return output

# validate html files
def check_links(file):
    output = ''
    return output


# ****************************** MAIN LOGIC ******************************    

# global variables
directory = ''
paths = []
html_output = 'HTML VALIDATION\n'
css_output = 'CSS VALIDATION\n'

# set up html validator
port = '8888'
command = 'java -cp ' + vnu_path + ' nu.validator.servlet.Main ' + port
run_command(command)

# check if path was specified
if (len(sys.argv) > 1):
    directory = sys.argv[1]
else:
    directory = os.getcwd()
    
# get file paths for directory
paths = get_filepaths(directory)

# loop over files
for path in paths:
    if path.endswith('.html') || path.endswith('.xhtml'):
        # append path name
        html_output = html_output + '\n' + path
        # run html validator and append output
        html_output = html_output + '\n' + validate_html(path)
        # check links and append output
        html_output = html_output + '\n' + check_links(path)
    if path.endswith('.css'):
        # append path name
        css_output = css_output + '\n' + path
        # run css validator and append output
        css_output = css_output + '\n' + validate_css(path)
        
# print output
print html_output
print css_output