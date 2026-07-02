import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_merged_data_with_months():
    data = pd.read_csv("temp/merged_data.csv")
    data['date_time'] = pd.to_datetime(data['occ_date_time'])
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    data['Month'] = pd.Categorical(data['date_time'].dt.month_name(), categories=month_order, ordered=True)
    return data

def plot_top_10_crimes(data):
    crime_type_counts = data.groupby('crime_type').size().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=crime_type_counts.values, y=crime_type_counts.index, ax=ax, palette='Set2')
    ax.set_title("Top 10 Crime Types in the City of Austin in 2025")
    ax.set_xlabel("Count")
    ax.set_ylabel("")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("temp/top_10_crimes.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_monthly_counts(data):
    monthly_counts = data.groupby('Month').size().reset_index(name='Event Count')
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x='Month', y='Event Count', data=monthly_counts, ax=ax, palette='Set2')
    ax.set_title("Monthly Crime Counts")
    ax.set_xlabel("Month")
    ax.set_ylabel("Event Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("temp/monthly_counts.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_monthly_counts_separated(data):
    f_violence_mask = data['family_violence'] == 'Y'
    family_violence_data = data[f_violence_mask]
    no_family_violence_data = data[~f_violence_mask]

    monthly_counts_fv = family_violence_data.groupby('Month').size().reset_index(name='Event Count')
    monthly_counts_nfv = no_family_violence_data.groupby('Month').size().reset_index(name='Event Count')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.barplot(x='Month', y='Event Count', data=monthly_counts_fv, ax=axes[0], palette='Set2')
    axes[0].set_title("Monthly Crime Counts (Family Violence)")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Event Count")
    axes[0].tick_params(axis='x', rotation=45)

    sns.barplot(x='Month', y='Event Count', data=monthly_counts_nfv, ax=axes[1], palette='Set2')
    axes[1].set_title("Monthly Crime Counts (No Family Violence)")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Event Count")
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig("temp/monthly_counts_separated.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_monthly_counts_by_block(data):
    monthly_counts = data.groupby(['Month', 'geoid']).size().reset_index(name='Event Count')
    fig, ax = plt.subplots(figsize=(10,6))
    sns.boxplot(x='Month', y='Event Count', data=monthly_counts, ax=ax, palette='Set2')
    ax.set_title("Distribution of Crime Counts Per Block Group by Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Event Count per Block Group")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("temp/monthly_block_counts.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_monthly_counts_by_block_separated(data):
    f_violence_mask = data['family_violence'] == 'Y'
    family_violence_data = data[f_violence_mask]
    no_family_violence_data = data[~f_violence_mask]

    monthly_counts_fv = family_violence_data.groupby(['Month', 'geoid']).size().reset_index(name='Event Count')
    monthly_counts_nfv = no_family_violence_data.groupby(['Month', 'geoid']).size().reset_index(name='Event Count')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    sns.boxplot(x='Month', y='Event Count', data=monthly_counts_fv, ax=axes[0], palette='Set2')
    axes[0].set_title("Distribution of Crime Counts Per Block Group by Month\n(Family Violence)")
    axes[0].set_xlabel("Month")
    axes[0].set_ylabel("Event Count per Block Group")
    axes[0].tick_params(axis='x', rotation=45)
    

    sns.boxplot(x='Month', y='Event Count', data=monthly_counts_nfv, ax=axes[1], palette='Set2')
    axes[1].set_title("Distribution of Crime Counts Per Block Group by Month\n(No Family Violence)")
    axes[1].set_xlabel("Month")
    axes[1].set_ylabel("Event Count per Block Group")
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig("temp/monthly_block_counts_separated.png", dpi=300, bbox_inches='tight')
    plt.close()

month_data = load_merged_data_with_months()
plot_monthly_counts_by_block(month_data)
plot_monthly_counts_by_block_separated(month_data)
plot_monthly_counts_separated(month_data)
plot_monthly_counts(month_data)
plot_top_10_crimes(month_data)