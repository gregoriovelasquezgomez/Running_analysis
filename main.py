from report_generator import create_pdf, process_data, generate_garmin_plots
from email_sender import send_email

def main():
    # Define parameters/filenames
    #plot_filename = generate_plot()
    img_filename = 'output/example_img.jpg'
    pdf_filename = 'output/report.pdf'
    garmin_data_filename = 'garmin/Activities.csv'
    
    # Process the data with the function in report_generator
    processed_data_df = process_data(garmin_data_filename)

    # Generate plots from garmin data
    plot_filename = generate_garmin_plots(processed_data_df)

    create_pdf(pdf_filename, plot_filename)
    #send_email(pdf_filename, img_filename)

if __name__ == '__main__':
    main()
