
import pandas as pd
import os

result_folder = 'outputs/'

#---------------------------------------------------------------
def load_res_lev( f_path, ind):
    lev_param = float('.'.join( f_path.split('/')[-1].split('_')[-1].replace('Levenshtein','').split('.')[0:-1]))
    rev_param =  int(f_path.split('/')[-1].split('_')[-2].replace('r',''))
    if ind=='lev':
        df = pd.read_csv(f_path, names = [lev_param])
    if ind=='rev':
        df = pd.read_csv(f_path, names = [rev_param])
        with open('outputs/contrib_database_r'+str(rev_param)+'_Levenshtein0.1.csv') as fp:
            x = len(fp.readlines())
        df_line = pd.DataFrame([x], index=["zzz_lines"], columns=[rev_param])
        df = pd.concat( [df,df_line])
    return df
#---------------------------------------------------------------

###########
# sensitivity regarding the Levenshtein parameter

list_employer_res = [f for f in os.listdir(result_folder)  if 'contrib_employer_percent_r32129' in f]
list_author_res = [f for f in os.listdir(result_folder)  if 'contrib_author_percent_r32129' in f]

df_emp = pd.concat( [ load_res_lev(result_folder+f, ind='lev') for f in list_employer_res], axis=1)
df_emp = df_emp.sort_index(axis=1).sort_index(axis=0) 
df_aut = pd.concat( [ load_res_lev(result_folder+f, ind='lev') for f in list_author_res], axis=1)
df_aut = df_aut.sort_index(axis=1).sort_index(axis=0) 

df_emp.to_csv(result_folder+'agg_contrib__employer__Levenshtein.csv', sep='|')
df_aut.to_csv(result_folder+'agg_contrib__author__Levenshtein.csv', sep='|')

###########
# sensitivity regarding the revision number for a Levenshtein parameter = 0.1

list_employer_res = [f for f in os.listdir(result_folder)  if 'contrib_employer_percent_r' in f and 'Levenshtein0.1.' in f]
list_author_res = [f for f in os.listdir(result_folder)  if 'contrib_author_percent_r' in f and 'Levenshtein0.1.' in f]

df_emp = pd.concat( [ load_res_lev(result_folder+f, ind='rev') for f in list_employer_res], axis=1)
df_emp = df_emp.sort_index(axis=1).sort_index(axis=0)
df_aut = pd.concat( [ load_res_lev(result_folder+f, ind='rev') for f in list_author_res], axis=1)
df_aut = df_aut.sort_index(axis=1).sort_index(axis=0)

df_emp.to_csv(result_folder+'agg_contrib__employer__revision.csv', sep='|')
df_aut.to_csv(result_folder+'agg_contrib__author__revision.csv', sep='|')

