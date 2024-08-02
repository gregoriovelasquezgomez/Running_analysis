# report_generator.py
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from matplotlib.backends.backend_pdf import PdfPages

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def generate_plot():
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    plt.plot(x, y)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Sine Wave Plot')
    plt.grid(True)
    plot_filename = 'plot.png'
    plt.savefig(plot_filename)  # Save the plot as an image
    plt.close()
    return plot_filename

def process_data(data_filename):
    # Read the data
    #df = pd.read_csv('garmin/Activities.csv')
    df = pd.read_csv(data_filename)
    # Select the needed data only
    df = df[['Date', 'Distance','Calories','Avg HR','Max HR','Avg Run Cadence','Max Run Cadence', 'Avg Pace', 'Best Pace', 
         'Avg Stride Length', 'Elapsed Time','Total Ascent']]
    # deal with empty entries
    df.replace('--', np.nan, inplace=True)
    #convert 'Date', 'Avg Pace', 'Best Pace', 'Elapsed Time' objects to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    df['Avg Pace'] = pd.to_datetime(df['Avg Pace'], format='%M:%S')
    df['Best Pace'] = pd.to_datetime(df['Best Pace'], format='%M:%S')
    df['Elapsed Time'] = pd.to_datetime(df['Elapsed Time'])
    #convert 'Avg Pace', 'Best Pace', 'Elapced Time' objects to the number of minutes per km
    df['Avg Pace'] = df['Avg Pace'].dt.hour*60 + df['Avg Pace'].dt.minute + df['Avg Pace'].dt.second/60
    df['Best Pace'] = df['Best Pace'].dt.hour*60 + df['Best Pace'].dt.minute + df['Best Pace'].dt.second/60
    df['Elapsed Time'] = df['Elapsed Time'].dt.hour*60 + df['Elapsed Time'].dt.minute + df['Elapsed Time'].dt.second/60
    #add 'Avg Speed' and 'Best Speed' columns as km/h
    df['Avg Speed'] = 60 / df['Avg Pace']
    df['Best Speed'] = 60 / df['Best Pace']
    #convert remaining columns of object type to float64
    s = df.select_dtypes(include='object').columns
    df[s] = df[s].astype("float")
    #df.info()
    # Sort by datetime
    df = df.sort_values('Date', ascending=True)
    # Create clasification of short, medium and long distances
    def classify_distance(distance):
        if distance <= 4:
            return 'Short'
        elif 4 < distance <= 7:
            return 'Medium'
        else:
            return 'Long'

    df['Distance_Category'] = df['Distance'].apply(classify_distance)

    return df

def generate_garmin_plots(df):

    def plot_weekly_distance(df,dpi=300):
        # Set 'Date' as the index
        dfi = df.copy()
        dfi.set_index('Date', inplace=True)

        # Calculate weekly total distance
        weekly_distance = dfi['Distance'].resample('W').sum()

        plt.figure(figsize=(20, 20))
        # Set Seaborn style
        sns.set_style('whitegrid')
        custom_palette = sns.color_palette(["#3498db", "#e74c3c", "#2ecc71"])
        sns.set_palette(custom_palette)

        # Create a bar plot
        #sns.barplot(x=weekly_distance.index, y=weekly_distance, color='skyblue', edgecolor='black', alpha=0.8, width=5)
        sns.barplot(x=weekly_distance.index, y=weekly_distance, hue=weekly_distance,  dodge=False)
        plt.xlabel('Week', fontsize=15)
        plt.ylabel('Distance (km)', fontsize=15)
        plt.title('Weekly Distance Run', fontsize=20, fontweight='bold')
        plt.xticks(fontsize=10, rotation=45)  # Rotate x-axis labels for readability
        plt.yticks(fontsize=10)
        plt.grid(axis='y', linestyle='--', alpha=0.5)  # Add dashed grid lines
        plt.tight_layout()  # Adjust spacing
        plt.legend().set_visible(False)
        plot_filename = 'output/plot_weekly_distance.png'
        plt.savefig(plot_filename, dpi=dpi)  # Save the plot as an image
        plt.close()
        return plot_filename

    def plot_running_metrics_over_time(df,dpi=300):
        # Create a multi-subplot
        fig, axs = plt.subplots(4, 1, figsize=(20, 20), sharex=True)

        # Plot Avg HR
        axs[0].plot(df['Date'], df['Avg HR'], label='Avg HR', color='blue')
        axs[0].plot(df['Date'], df['Max HR'], label='Max HR', linestyle=':', color='blue')
        axs[0].set_ylabel('HR (bpm)', fontsize=15)
        axs[0].grid(True)
        axs[0].legend(fontsize=15)

        # Plot Avg Pace
        axs[1].plot(df['Date'], df['Avg Pace'], label='Avg Pace', color='red')
        axs[1].plot(df['Date'], df['Best Pace'], label='Best Pace', linestyle=':', color='red')
        axs[1].set_ylabel('Pace (min/km)', fontsize=15)
        axs[1].grid(True)
        axs[1].legend(fontsize=15)

        # Plot Avg Run Cadence
        axs[2].plot(df['Date'], df['Avg Run Cadence'], label='Avg Run Cadence', color='green')
        axs[2].plot(df['Date'], df['Max Run Cadence'], label='Max Run Cadence', linestyle=':', color='green')
        axs[2].set_ylabel('Cadence (spm)', fontsize=15)
        axs[2].xaxis.set_ticks(fontsize=15)  # fix x ticks
        axs[2].grid(True)
        axs[2].legend(fontsize=15)

        # Plot Distance
        axs[3].plot(df['Date'], df['Distance'], label='Distance', color='black')
        axs[3].set_ylabel('Distance (km)', fontsize=15)
        axs[3].set_xlabel('Date', fontsize=15)
        axs[3].tick_params(axis='both', which='major', labelsize=15)
        axs[3].grid(True)

        # Add secondary axis for Total Ascent
        axs2 = axs[3].twinx()  # Create a twin Axes sharing the same x-axis
        axs2.plot(df['Date'], df['Total Ascent'], label='Total Ascent', linestyle=':', color='purple')
        axs2.set_ylabel('Total Ascent (m)', color='purple', fontsize=15)
        axs2.tick_params(axis='y', labelcolor='purple', fontsize=15)
        #axs[3].legend()
        #axs2.legend()
        # Add a title
        plt.suptitle('Running Metrics Over Time')

        # Adjust spacing between subplots
        plt.tight_layout()

        plot_filename = 'output/plot_running_metrics_over_time.png'
        plt.savefig(plot_filename, dpi=dpi)  # Save the plot as an image
        plt.close()
        return plot_filename
    
    def plot_running_metrics_hist(df,dpi=300):
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))

        # Flatten axes array for easier indexing
        axes = axes.flatten()

        # Subplot HR
        sns.histplot(df['Avg HR'], bins=20, ax=axes[0], color='blue', alpha=0.5, label='Avg HR')
        sns.histplot(df['Max HR'], bins=20, ax=axes[0], color='skyblue', alpha=0.5, label='Max HR')
        axes[0].set_title('HR', fontsize=20)
        axes[0].set_xlabel('bpm', fontsize=15)
        axes[0].set_ylabel('')
        axes[0].yaxis.set_ticks([], fontsize=15)  # Remove y-axis ticks
        axes[0].xaxis.set_ticks(fontsize=15)  # Remove y-axis ticks
        axes[0].legend()

        # Subplot Pace
        sns.histplot(df['Avg Pace'], bins=20, ax=axes[1], color='blue', alpha=0.5, label='Avg Pace')
        sns.histplot(df['Best Pace'], bins=20, ax=axes[1], color='skyblue', alpha=0.5, label='Max Pace')
        axes[1].set_title('Pace', fontsize=20)
        axes[1].set_xlabel('min/km', fontsize=15)
        axes[1].set_ylabel('')
        axes[1].yaxis.set_ticks([], fontsize=15)  # Remove y-axis ticks
        axes[1].xaxis.set_ticks(fontsize=15)  # Remove y-axis ticks
        axes[1].legend()

        # Subplot Cadence
        sns.histplot(df['Avg Run Cadence'], bins=20, ax=axes[2], color='blue', alpha=0.5, label='Avg Cadence')
        sns.histplot(df['Max Run Cadence'], bins=20, ax=axes[2], color='skyblue', alpha=0.5, label='Max Cadence')
        axes[2].set_title('Cadence', fontsize=20)
        axes[2].set_xlabel('spm', fontsize=15)
        axes[2].set_ylabel('')
        axes[2].yaxis.set_ticks([], fontsize=15)  # Remove y-axis ticks
        axes[2].xaxis.set_ticks(fontsize=15)  # Remove y-axis ticks
        axes[2].legend()

        # Subplot Distance
        sns.histplot(df['Distance'], bins=20, ax=axes[3], color='blue', alpha=0.3, label='km')
        #axes[2].hist(df['Max Run Cadence'], bins=20, color='skyblue', alpha=0.5, label='Max Cadence')
        axes[3].set_title('Distance', fontsize=20)
        axes[3].set_xlabel('spm', fontsize=15)
        axes[3].set_ylabel('')
        axes[3].yaxis.set_ticks([], fontsize=15)  # Remove y-axis ticks
        axes[3].xaxis.set_ticks(fontsize=15)  # Remove y-axis ticks
        axes[3].legend()

        # Adjust layout
        plt.tight_layout()

        # Save plot
        plot_filename = 'output/plot_running_metrics_hist.png'
        plt.savefig(plot_filename, dpi=dpi)  # Save the plot as an image
        plt.close()
        return plot_filename

    
    # Run all the plot functions and collect the filenames to generate an output
    filenames = []
    
    filenames.append(plot_weekly_distance(df))
    filenames.append(plot_running_metrics_over_time(df))
    filenames.append(plot_running_metrics_hist(df))
    #filenames.append(plot_3())
    
    return filenames

def create_pdf(pdf_filename, plot_filenames, dpi=300):
    """c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(1 * inch, 10.5 * inch, "My Report")

    # Insert plot image
    c.drawImage(plot_filename, 1 * inch, 6 * inch, width=6 * inch, height=4 * inch)

    c.showPage()
    c.save()"""

    with PdfPages(pdf_filename) as pdf:
        for filename in plot_filenames:
            fig = plt.figure()
            img = plt.imread(filename)
            plt.imshow(img)
            plt.axis('off')  # Hide axes
            pdf.savefig(fig, dpi=dpi)  # Save the current figure to the PDF
            plt.close(fig)  # Close the figure to free memory
