import re

def extract_revision_and_date(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'r(\d+) \| ([^|]+) \| (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \+\d{4})')
    matches = pattern.findall(content)

    result = []
    for match in matches:
        revision_number, name, date = match
        result.append({"revision_number": revision_number, "date": date})

    return result

# Replace 'your_file.txt' with the actual path to your text file
file_path = 'outputs/svn_log.txt'
revisions_and_dates = extract_revision_and_date(file_path)

for entry in revisions_and_dates:
    print(f"Revision Number: {entry['revision_number']}, Date: {entry['date']}")

###########################
# cerate a database: rxxxx, date in french format
output_file_path = 'outputs/revision_date.txt'  # Replace with your desired output file path

with open(output_file_path, 'w') as output_file:
    output_file.write('revision|date\n')  # Write to file
    for entry in revisions_and_dates:
        revision = 'r'+entry['revision_number']
        date = entry['date'].split(' ')[0].split('-')
        date.reverse()
        date = '-'.join( date)
        #output_line = f"Revision Number: {entry['revision_number']}, Date: {entry['date']}\n"
        output_line = f"Revision Number: {entry['revision_number']}, Date: {entry['date']}\n"
        print(output_line, end='')  # Print to console
        output_file.write(revision+'|'+date+'\n')  # Write to file

print(f"Output saved to {output_file_path}")


