
import sys
from datetime import datetime

#---------------------------------------------------------------
def sort_database_main( database_main):
    rev_list = list(set(database_main['revision']))
    auth_list = list(set(database_main['author']))
    # initialization of dict
    dict_result = {}
    for auth in auth_list:
        dict_result[auth] = {k:0 for k in rev_list}
    for i, line in enumerate(database_main['lines']):
        dict_result[ database_main['author'][i]][ database_main['revision'][i]] += len(line)
    # remove zeros
    for auth in auth_list:
        dict_result[auth] = {k:v for k,v in dict_result[auth].items() if v!=0}
    return dict_result
#---------------------------------------------------------------
# Define a function to convert French date string to datetime
def french_date_to_datetime(date_string):
    # Parse the French date string using the specified format
    return datetime.strptime(date_string, '%d-%m-%Y')
#---------------------------------------------------------------
def find_interval_position(date, date_intervals):
    date_obj = datetime.strptime(date, '%d-%m-%Y')

    for i, (start_date, end_date) in enumerate(date_intervals, 1):
        start_obj = datetime.strptime(start_date, '%d-%m-%Y')
        end_obj = datetime.strptime(end_date, '%d-%m-%Y')
        if start_obj <= date_obj <= end_obj:
            return i-1  # Return the position if the date is within the interval

    return None  # Return None if the date is not within any interval
#---------------------------------------------------------------

output_dir = "outputs/"
Levenshtein_thsld = float(sys.argv[1])
#Levenshtein_thsld = 0.1
main_rev = int(sys.argv[2])
#main_rev = 32129 #1098

file_path = output_dir + "contrib_database_r"+str(main_rev)+"_Levenshtein"+str(Levenshtein_thsld)+".csv"

# construct and import database
database_main = {}
database_main['lines'] = []
database_main['author'] = []
database_main['revision'] = []

with open(file_path, 'r') as file:
    for i, line in enumerate(file):
        if i==0:
            continue
        author = line.split('|')[0]
        rev = line.split('|')[1]
        lines = '|'.join(line.strip().split('|')[2:])
        #author, rev, lines = line.strip().split('|')
        database_main['lines'].append(lines)
        database_main['author'].append(author)
        database_main['revision'].append(rev)


# ----------------------------------------
# manaully convert the first contribution (rozenberg-754)
# this should account for th elenght of the lines
i_roz_754 = [i for i, auth_i in enumerate(database_main['author']) if auth_i=='rozenberg' and database_main['revision'][i] == '754']
total_lenght_line = sum([ len(database_main['lines'][i]) for i in i_roz_754])
line_35_percent = 0.35*total_lenght_line
line_15_percent = 0.15*total_lenght_line
line_10_percent = 0.10*total_lenght_line

# Manually set the author of first revision
# as the model was not under subversion before that
auth_1 = 'author_1'
auth_2 = 'author_2'
auth_3 = 'author_3'
auth_4 = 'author_4'
auth_5 = 'author_5'

total_attributed = 0
if main_rev >= 29156:
    for i, index in enumerate(i_roz_754):
        if total_attributed <= line_35_percent:
            database_main['author'][index] = auth_1
        elif total_attributed <= 2*line_35_percent:
            database_main['author'][index] = auth_2
        elif total_attributed <= 2*line_35_percent + line_15_percent:
            database_main['author'][index] = auth_3
        else:
            database_main['author'][index] = auth_4
        total_attributed += len(database_main['lines'][index])
else:
    for i, index in enumerate(i_roz_754):
        if total_attributed <= line_35_percent:
            database_main['author'][index] = auth_1
        elif total_attributed <= 2*line_35_percent:
            database_main['author'][index] = auth_2
        elif total_attributed <= 2*line_35_percent + line_10_percent:
            database_main['author'][index] = auth_3
        elif total_attributed <= 2*line_35_percent + 2*line_10_percent:
            database_main['author'][index] = auth_5
        else:
            database_main['author'][index] = auth_4
        total_attributed += len(database_main['lines'][index])

#TODO: ça plus fait qu'on a 2 fois end à la fin

# ----------------------------------------
# compute contributions
results = sort_database_main( database_main)
res_by_author = {k: sum(v.values()) for k,v in results.items()}
res_by_author_percent = {k: v/sum(res_by_author.values()) *100 for k,v in res_by_author.items()}

# export contribution by author
with open(output_dir + "contrib_author_percent_r"+str(main_rev)+"_Levenshtein"+str(Levenshtein_thsld)+'.csv', 'w') as f:
    [f.write('{0},{1}\n'.format(key, value)) for key, value in res_by_author_percent.items()]

# ----------------------------------------
# convert revision to date

# load revision / date dictionnary
rev_date_dict = {}
with open(output_dir + "revision_date.txt", 'r') as file:
    for i, line in enumerate(file):
        if i==0:
            continue
        rev, date = line.strip().split('|')
        rev_date_dict[ rev.replace('r','')] = date # remove the 'r' in revision keys

# check if all rev are in dict
all_rev = []
for dic in results.values():
    for rev in dic.keys():
        all_rev.append(rev)
all_rev = list(set(all_rev))

print("missing rev in rev_date_dict", [r for r in all_rev if not r in rev_date_dict.keys()])

# convert revision to date in results
results_date = {}
# init results_date before completing it, as some revision have the same date
for author in results.keys():
    results_date[author] = {rev_date_dict[k]:0 for k in results[author].keys()}
    for k, v in results[author].items():
        results_date[author][rev_date_dict[k]] += v

# ----------------------------------------
# convert author-date to employeur

# first create a list of dates for each author, and classify it. Also print min and max date for each author
date_for_author_dict = {}

# usefull to manually generate data/employer_date.csv after
for author in results_date.keys():
    list_date = results_date[ author].keys()
    date_for_author_dict[ author] = sorted( list_date, key=french_date_to_datetime)
    max_d = max( list_date, key=french_date_to_datetime)
    min_d = min( list_date, key=french_date_to_datetime)
    print(author, min_d, max_d)

# load the employee / date database
author_employ_date_dict = {}
for auth in date_for_author_dict.keys():
    author_employ_date_dict[auth] = {'dates':[], 'employers':[]}

employ_list = []
with open( "../data/employer_date.csv", 'r') as file:
    for i, line in enumerate(file):
        if i==0:
            continue
        author, d1, d2, empl = line.strip().split('|') 
        if not author in author_employ_date_dict.keys():
            author_employ_date_dict[author] = {'dates':[], 'employers':[]}
        author_employ_date_dict[author]['dates'].append( (d1, d2))
        author_employ_date_dict[author]['employers'].append( empl)
        employ_list.append(empl)

# convert result by author date to employeur
results_employer = {k:0 for k in list(set(employ_list))}

for auth in results_date.keys():
    for date, val in results_date[auth].items():
        position_date = find_interval_position(date, author_employ_date_dict[auth]['dates'])
        if position_date is not None:
            employeur = author_employ_date_dict[auth]['employers'][ position_date]
            results_employer[ employeur] += val

results_employer_percent = {k: v/sum(results_employer.values()) *100 for k,v in results_employer.items()}

# export contribution by author
with open(output_dir + "contrib_employer_percent_r"+str(main_rev)+"_Levenshtein"+str(Levenshtein_thsld)+'.csv', 'w') as f:
    [f.write('{0},{1}\n'.format(key, value)) for key, value in results_employer_percent.items()]

