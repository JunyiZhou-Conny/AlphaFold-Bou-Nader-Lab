import pandas as pd
import matplotlib.pyplot as plt

# Read the target names from both datasets
af3_targets = set(pd.read_excel('af3_target_names.xlsx')['Target_Names'])
afp_targets = set(pd.read_excel('afp_target_names.xlsx')['Target_Names'])

# Calculate overlaps
overlap = af3_targets.intersection(afp_targets)
only_af3 = af3_targets - afp_targets
only_afp = afp_targets - af3_targets

# Create a Venn diagram
plt.figure(figsize=(10, 6))
plt.pie([len(only_af3), len(overlap), len(only_afp)],
        labels=['Only AF3', 'Overlap', 'Only AFP'],
        autopct='%1.1f%%',
        colors=['#ff9999','#66b3ff','#99ff99'])
plt.title('Overlap between AF3 and AFP Target Proteins')
plt.axis('equal')

# Save the plot
plt.savefig('target_overlap.png')
plt.close()

# Create a bar chart
plt.figure(figsize=(10, 6))
categories = ['Only AF3', 'Overlap', 'Only AFP']
counts = [len(only_af3), len(overlap), len(only_afp)]
plt.bar(categories, counts, color=['#ff9999','#66b3ff','#99ff99'])
plt.title('Number of Target Proteins in Each Category')
plt.ylabel('Count')
for i, count in enumerate(counts):
    plt.text(i, count, str(count), ha='center', va='bottom')
plt.savefig('target_counts.png')
plt.close()

# Save overlap information to Excel
overlap_df = pd.DataFrame({
    'Category': ['Only AF3', 'Overlap', 'Only AFP'],
    'Count': [len(only_af3), len(overlap), len(only_afp)],
    'Proteins': [
        ', '.join(sorted(only_af3)),
        ', '.join(sorted(overlap)),
        ', '.join(sorted(only_afp))
    ]
})
overlap_df.to_excel('overlap_analysis.xlsx', index=False)

print("Analysis complete! Generated files:")
print("1. target_overlap.png - Pie chart showing overlap")
print("2. target_counts.png - Bar chart showing counts")
print("3. overlap_analysis.xlsx - Detailed overlap information") 