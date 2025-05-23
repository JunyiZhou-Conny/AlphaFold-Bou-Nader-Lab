import pandas as pd

# Read the filtered AF3 data
af3_data = pd.read_csv('/data7/Conny/result_csv/AF3_Summary_Stats.csv')
af3_filtered = af3_data[(af3_data['iptm'] >= 0.6) & (af3_data['ptm'] >= 0.5)]

# Extract and capitalize target names
target_names = af3_filtered['target_protein'].str.upper()

# Save to text file
with open('af3_target_names.txt', 'w') as f:
    for name in target_names:
        f.write(f"{name}\n")

# Save to Excel
target_df = pd.DataFrame({'Target_Names': target_names})
target_df.to_excel('af3_target_names.xlsx', index=False)

print("Files have been generated:")
print("1. af3_target_names.txt - Contains list of capitalized target names")
print("2. af3_target_names.xlsx - Excel file with capitalized target names") 