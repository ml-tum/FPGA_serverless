# Interestingly, this script is not needed as the original data set is already sorted in order of start_timestamp (which is not included but
# can be calculated as start_timestamp = end_timestamp - duration). This script is kept here for reference.

import csv

# Read the CSV file
input_file = '../AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt'
with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    header = next(reader)  # Read the header row
    rows = [row for row in reader]

# Calculate start_timestamp for each row and store it as a tuple (start_timestamp, row)
rows_with_start_timestamps = [(float(row[2]) - float(row[3]), row) for row in rows]

# Sort rows by start_timestamp
sorted_rows_with_start_timestamps = sorted(rows_with_start_timestamps, key=lambda x: x[0])

# Extract sorted rows
sorted_rows = [x[1] for x in sorted_rows_with_start_timestamps]

# Write the sorted rows to a new CSV file
output_file = '../AzureFunctionsInvocationTraceForTwoWeeksJan2021_sorted.csv'
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)
    writer.writerows(sorted_rows)

print(f'Sorted CSV saved as {output_file}')