import pandas as pd

csv_file = 'fanfic_sentiment_analysis.csv'
df = pd.read_csv(csv_file)

# Rename stuff to use in Supabase
df.rename(columns={'ID': 'id'}, inplace=True)
df.rename(columns={'Title': 'title'}, inplace=True)
df.rename(columns={'Author': 'author'}, inplace=True)
df.rename(columns={'Fandom': 'fandom'}, inplace=True)
df.rename(columns={'Url': 'url'}, inplace=True)
df.rename(columns={'Kudos': 'kudos'}, inplace=True)
df.rename(columns={'Average_Sentiment': 'average_sentiment'}, inplace=True)
df.rename(columns={'Vector': 'vector'}, inplace=True)

# Select relevant columns for the final dataframe
final_df = df[['id', 'title', 'author', 'fandom', 'url', 'kudos', 'average_sentiment', 'vector']]

# Save the final dataframe to a new CSV file
final_df.to_csv('final_fanfics_edited.csv', index=False)