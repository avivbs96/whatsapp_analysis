import pandas as pd
import re
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as mcolors

def process_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    formatted_lines = []
    for line in lines:
        match = re.match(r'\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] (.*?): (.*)', line)
        if match:
            date, user, message = match.groups()
            formatted_lines.append({'Date': pd.to_datetime(date, format='%d/%m/%Y, %H:%M:%S'), 'User': user, 'Message': message})
        else:
            if formatted_lines:
                formatted_lines[-1]['Message'] += line

    df = pd.DataFrame(formatted_lines)
    return df

def create_bar_chart(df):
    # Reverse Hebrew names if necessary
    df['User'] = df['User'].apply(lambda x: x[::-1] if any('\u0590' <= char <= '\u05EA' for char in x) else x)

    # Group by User and count total messages
    user_stats_total = df.groupby(['User']).size().reset_index(name='Total Message Count')

    # Sort data by Total Message Count
    user_stats_total = user_stats_total.sort_values(by='Total Message Count')

    # Assign unique colors to each user
    num_users = len(user_stats_total)
    colors = list(mcolors.TABLEAU_COLORS.values())[:num_users]

    # Calculate total messages and percentage
    total_messages = user_stats_total['Total Message Count'].sum()
    user_stats_total['Percentage'] = (user_stats_total['Total Message Count'] / total_messages) * 100

    # Plot the bar chart
    plt.figure(figsize=(12, 8))
    plt.barh(user_stats_total['User'], user_stats_total['Total Message Count'], color=colors)
    for i, (value, percent) in enumerate(zip(user_stats_total['Total Message Count'], user_stats_total['Percentage'])):
        plt.text(value, i, f'{value} ({percent:.2f}%)', va='center')  # Display message count and percentage
    plt.xlabel('Message Count')
    plt.ylabel('User')
    plt.title(f'Total Messages by Participant\n(from {df["Date"].min().date()} to {df["Date"].max().date()})')
    plt.gca().invert_yaxis()  # Invert y-axis for ascending order
    plt.tight_layout()
    plt.savefig('/Users/Aviv/Desktop/whatsapp_analysis_bar_chart.pdf')
    plt.show()

if __name__ == "__main__":
    df = process_data('/Users/Aviv/Desktop/_chat_fifa2.txt')

    # Create bar chart
    create_bar_chart(df)

    print("PDF file created successfully.")
