#/bin/bash

# REPLACE with you python 3 directory
export python3_path='/usr/bin/python3'
# REPLACE with you svn repository url
export svn_repo_url='https://svn_url_example/'

# create an Imaclim checkout, and get all file type, a list then hardcoded to run_svnblame_R.py
# before delete manually trunk_v2.0/ and all checkouts if it exists
svn checkout --ignore-externals $svn_repo_urlImaclim/ImaclimRWorld/trunk_v2.0/
$python3_path 1.get_all_file_type.py

# parse svn log to create a revision|date database
mkdir outputs
svn log $svn_repo_url > outputs/svn_log.txt
$python3_path 2.parse_svn_log.py

# run svn blame on a list of selected revisions
# 32144 is the first revision ofd 2024
file_path_revision="../data/svn_destinations_v2.txt"
for rev in 32144 31503 30583 29874
do
    while IFS= read -r destination; do
        svn checkout -r$rev --ignore-externals $svn_repo_url$destination checkout_$rev/$destination
    done < "$file_path_revision"
    $python3_path 3.run_svnblame_R.py $rev checkout_$rev/
done

file_path_revision="../data/svn_destinations_v1.txt"
for rev in 11075 754 1098 2825 7360 11301 15217 18707 21187 23377 25230 27467 28820 #29874 30583 31503
do
    while IFS= read -r destination; do
        svn checkout -r$rev --ignore-externals $svn_repo_url$destination checkout_$rev/$destination
    done < "$file_path_revision"
    $python3_path 3.run_svnblame_R.py $rev checkout_$rev/
done

# compute contribution with different sensibility threshold for the Levenshtein distance
mkdir -p log
for lvparam in 0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.08 0.09 0.1 0.12 0.15 0.2 0.3 0.4 0.5 0.6
do
    nohup nice $python3_path 4.1.extract_contribution.py $lvparam 32144 > log/run_r32144_$lvparam.log 2>&1 &
    nohup nice $python3_path 4.2.compute_contribution.py $lvparam 32144 &
done

# compute contribution of different revision for on sensibility threshold for the Levenshtein distance (0.1)
for lvparam in 0.1
do
    for rev in 754 1098 2825 7360 11301 15217 18707 21187 23377 25230 27467 28820 29874 30583 31503 #32144
    do
        nohup nice $python3_path 4.1.extract_contribution.py $lvparam $rev > log/run_r$rev_$lvparam.log 2>&1 &
        nohup nice $python3_path 4.2.compute_contribution.py $lvparam $rev &
    done
done

nohup nice $python3_path 5.plot_aggregate_results.py

