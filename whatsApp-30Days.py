import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive before importing pyplot
import pandas as pd
import re
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
import matplotlib.colors as mcolors

def process_data(file_path, last_days=None):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    if last_days:
        # Calculate the date 30 days ago from today
        thirty_days_ago = datetime.now() - timedelta(days=last_days)
        
        # Filter lines for the last 30 days
        lines = [line for line in lines if re.match(r'\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]', line)]
        lines = [line for line in lines if datetime.strptime(re.findall(r'\[(\d{2}/\d{2}/\d{4}), \d{2}:\d{2}:\d{2}\]', line)[0], '%d/%m/%Y') >= thirty_days_ago]
    
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
    try:
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
        plt.savefig('/Users/Aviv/Desktop/whatsapp_analysis_bar_chart_last_30_days.pdf')
        plt.show()
    except KeyboardInterrupt:
        print("Plotting interrupted. PDF file may not have been saved.")

if __name__ == "__main__":
    df_last_30_days = process_data('/Users/Aviv/Desktop/_chat_fifa2.txt', last_days=30)

    # Create bar chart for the last 30 days
    create_bar_chart(df_last_30_days)

    print("PDF file for last 30 days created successfully.")
