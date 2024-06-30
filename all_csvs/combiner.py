import pandas as pd
import os

# List of file names
file_names = [
    'fanfic_titles_1.csv', 'fanfic_titles_2.csv', 'fanfic_titles_3.csv', 'fanfic_titles_4.csv',
    'fanfic_titles_5.csv', 'fanfic_titles_6.csv', 'fanfic_titles_7.csv', 'fanfic_titles_8.csv',
    'fanfic_titles_9.csv', 'fanfic_titles_10.csv'
]

# List to store DataFrames
dfs = []

# Function to read CSV with debug statements
def read_csv_file(file_name):
    if os.path.exists(file_name):
        print(f"File {file_name} exists.")
        try:
            df = pd.read_csv(file_name)
            print(f"Read {len(df)} records from {file_name}.")
            return df
        except pd.errors.EmptyDataError:
            print(f"File {file_name} is empty.")
        except pd.errors.ParserError as e:
            print(f"Parsing error in {file_name}: {e}")
        except Exception as e:
            print(f"An error occurred while reading {file_name}: {e}")
    else:
        print(f"File {file_name} does not exist.")
    return None

# Read each CSV file and append to the list
for file_name in file_names:
    print(f"Processing {file_name}...")
    df = read_csv_file(file_name)
    if df is not None:
        print(f"Successfully read {file_name}")
        dfs.append(df)
    else:
        print(f"Failed to read {file_name}")

# Check if any DataFrames were successfully read
if dfs:
    # Concatenate all DataFrames into one
    combined_df = pd.concat(dfs, ignore_index=True)
    # Save the combined DataFrame to a new CSV file
    combined_df.to_csv('all_fanfics.csv', index=True, index_label='ID')
    print("Combined DataFrame saved to 'all_fanfics.csv'.")
else:
    print("No valid data found in any files.")