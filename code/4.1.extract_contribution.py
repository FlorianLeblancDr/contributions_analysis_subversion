#author: Florian Leblanc
#purpose: Script to ????

import subprocess
import re
import os
import difflib
import sys
import copy
import Levenshtein

# Configuration
output_dir = "outputs/"  # Directory to store the contributions database

# UPDATE IF NECESSARY THE REVISION YOU WANT TO DO THE COMPARISONS ON
list_rev_compare = [754,11075,30583]

#--------------------------------------------------------------------------------------------------------------------------
def create_svn_blame_database( file_path):
    database = {}
    lines_list = []
    database['revision'] = []
    database['author'] = []
    # Define a regular expression pattern to match the elements
    pattern = re.compile(r'^\s*(\d+)\s+(\S+)\s+(.*)$')
    with open(file_path, 'r') as file:
        for line in file:
            match = pattern.match(line)
            revision, author, rest_of_line = match.groups()
            # Append each line to the list (remove newline characters if needed)
            database['revision'].append(revision)
            database['author'].append(author)
            lines_list.append( rest_of_line.strip())
    database['lines'], database['revision'], database['author'] = clean_lines(lines_list, database['revision'], database['author'])
    #database['lines'] = clean_lines( clean_lines(lines_list))
    database['ascii_lines'] = [[ord(char) for char in lines] for lines in database['lines']]
    database['ascii_sum'] = [sum(ascii_lines) for ascii_lines in  database['ascii_lines']]
    database['ascii_cat'] = []
    database['modified'] = [False for ascii_lines in range(len(database['ascii_lines']))]
    for ascii_lines in database['ascii_lines']:
        if len(ascii_lines)>0:
            database['ascii_cat'].append( int(''.join(map(str, ascii_lines))))
        else:
            database['ascii_cat'].append( 0)
    #    database['ascii_cat'] = [ [0,int(''.join(map(str, ascii_lines)))][ len(ascii_lines)>0] for ascii_lines in database['ascii_lines']]
    database['ascii_len'] = [len(ascii_lines) for ascii_lines in  database['ascii_lines']]
    return database
#--------------------------------------------------------------------------------------------------------------------------
def clean_lines(line, rev, auth):
    # clean a line to make it more comparable
    # remove space and tabulation, and do not selecte commentary
    line = [l.replace(' ','').replace('\t','') for l in line]
    line_out = []
    rev_out = []
    auth_out = []
    begin_com_C = False
    begin_com_py = False
    for il, l in enumerate(line):
        if len(l)==0:
            continue
        if len(l)>=1:
            if l[0] == '#' or (l[0] == '*' and not begin_com_C):
                continue
        if len(l)>=2:
            if l[0:2] == '//':
                continue
            if l[0:2] == '/*':
                begin_com_C = True
            if l[0:2] == '*/':
                begin_com_C = False
                continue
            if l[0:2] == '"""' and not begin_com_py:
                begin_com_C = True
            if l[0:2] == '"""' and begin_com_py:
                begin_com_C = False
        # next lines commented, because the code is poluted
        #if begin_com_py or begin_com_C:
        #    continue
        line_out.append(l)
        rev_out.append(rev[il])
        auth_out.append(auth[il])
    print(len(line), len(line_out))
    return line_out, rev_out, auth_out  
#--------------------------------------------------------------------------------------------------------------------------
def compare_two_database( database_main, database_2_compare, log, main_remove=False):
    do_log = False
    original_size = len(database_main['modified']) - sum(database_main['modified'])
    #find clothest ascii_sum
    list2find = database_2_compare['ascii_sum']
    modified_lines = []
    for i, sumi in enumerate(database_main['ascii_sum']):
        if i<60000 and short_test or database_main['modified'][i]:
            continue
        # 1. Comparing ascii_sum: does not work well
        # Using the min() function along with enumerate() and a custom key function
        #min_j, j = min(((value, index) for index, value in enumerate(list2find)),
        #                   key=lambda x: abs(x[0] - sumi))
        #sumj = list2find[j]
        #if abs((sumi-sumj)/sumi) < 0.1:
        #    print(i,j,sumi,sumj,'\n',database_main['lines'][i],'\n',database_2_compare['lines'][j],'\n')

        # 2. Comparing ascii_cat: does not work well
        
        # 3. Compare using ascii_lines

        # 4. Use Levenshtein distance
        for j, jsum in enumerate(database_2_compare['ascii_sum']):
            distance = Levenshtein.distance(database_main['lines'][i], database_2_compare['lines'][j])
            #if distance < 0.15*len(database_main['lines'][i]) and distance>=0.1*len(database_main['lines'][i]):
            #    print(distance, '\n',database_main['lines'][i],'\n',database_2_compare['lines'][j],'\n')
            if distance < Levenshtein_thsld * len(database_main['lines'][i]) and not (main_remove and i==j):
                database_main, modified_lines = assign_line( database_main, database_2_compare, i, j, modified_lines)
                #modified_lines.append(i) # we store modified line afterwards, as we still want to allow for changes with one revision
                if do_log:
                    log += database_main['lines'][i] + '\n' + '     ----- replaced by ----' + '\n' + database_2_compare['lines'][j] + '\n\n'
        if i%1000==0:
            print("I: ",i)

    if main_remove:
        final_size = len(database_main['modified']) - len(set(modified_lines))
    else:
        final_size = len(database_main['modified']) - sum(database_main['modified'])

    if main_remove: # case we compare the main with himself to simplify it
        database_main = remove_self( database_main, modified_lines)
        #print( len(set(modified_lines)), " len(modified_lines)")
    else:
        for i in modified_lines:
            database_main['modified'][i] = True

    #print("modified_lines",sum(database_main['modified']))
    print('\n','    Sizes: ', original_size, final_size, '\n')
    return database_main, log
#--------------------------------------------------------------------------------------------------------------------------
def assign_line( database_main, database_2_compare, i, j, modified_lines):
    #print(i,' ',j,' ',database_main['author'][i],'-',database_main['revision'][i], " replaced by ",database_2_compare['author'][j],'-',database_2_compare['revision'][j],'\n')
    if database_main['revision'][i] > database_2_compare['revision'][j]:
        modified_lines.append(i) # we store modified line afterwards, as we still want to allow for changes with one revision
        for elt in ['revision','author','lines','ascii_lines','ascii_sum','ascii_cat','modified']:
            database_main[elt][i] = database_2_compare[elt][j]
    return database_main, modified_lines
#--------------------------------------------------------------------------------------------------------------------------
def remove_self( database_main, modified_lines):
    for i in sorted(set(modified_lines), reverse=True): #index2remove:
        for elt in ['revision','author','lines','ascii_lines','ascii_sum','ascii_cat','modified']:
            removed_item = database_main[elt].pop(i)
    return database_main
#--------------------------------------------------------------------------------------------------------------------------
def export_database( database_main, output_file_path):
    with open(output_file_path, "w") as db_file:
        db_file.write("author|revision|line\n")
        for i in range(len(database_main['lines'])):
            db_file.write(database_main['author'][i] + '|' + database_main['revision'][i] + '|' + database_main['lines'][i] + '\n')
    return 0
#--------------------------------------------------------------------------------------------------------------------------



short_test = False #True
#Levenshtein_thsld = 0.10 # Levenshtein threshold, as a part of total lenght of the string
Levenshtein_thsld = float(sys.argv[1]) # Levenshtein threshold, as a part of total lenght of the string

#main_rev = 32129
#main_rev = 32144
main_rev = int(sys.argv[2]) 

# increase the limit (4300 digits) for integer string conversion
sys.set_int_max_str_digits(int(1e5)) #4300

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# create database of each file
database_revisions = {}
for rev in [r for r in list_rev_compare if r<main_rev] + [main_rev]:
    file_blame = 'outputs/svnblame_imaclim_r'+str(rev)+'.txt'
    database_revisions[rev] = create_svn_blame_database( file_blame)

# create main database as a result
database_main = copy.deepcopy(database_revisions[main_rev])

# compare database successively
log = ''
database_main, log = compare_two_database( database_main, database_revisions[rev], log, main_remove=True)
for rev in [r for r in list_rev_compare if r<main_rev] + [main_rev]:
    database_main, log = compare_two_database( database_main, database_revisions[rev], log)

# Export result
output_file_path = output_dir + "contrib_database_r"+str(main_rev)+"_Levenshtein"+str(Levenshtein_thsld)+".csv"
export_database( database_main, output_file_path)

# export log
with open( output_dir + "log_r"+str(main_rev)+"_Levenshtein"+str(Levenshtein_thsld)+".log", "w") as db_file:
    db_file.write(log)

