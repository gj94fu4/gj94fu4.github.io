import pandas as pd

def otp_genpy(data_df):
    # Converting columns to datetime objects for accurate operations
    data_df['LTD'] = pd.to_datetime(data_df['LTD'])
    data_df['STD'] = pd.to_datetime(data_df['STD'])
    data_df['Best Departure Time'] = pd.to_datetime(data_df['Best Departure Time'])

    # Extracting the year of departure according to Taipei time (LTD)
    flights_2023 = data_df[data_df['LTD'].dt.year == 2023]

    # Calculating delay in minutes
    flights_2023['delay'] = (flights_2023['Best Departure Time'] - flights_2023['STD']).dt.total_seconds() / 60

    # Filtering flights departing from TPE delayed more than 15 minutes
    delayed_flights = flights_2023[(flights_2023['Dep'] == 'TPE') & (flights_2023['delay'] > 15)]

    # Counting the total number of flights in 2023 and the delayed flights from TPE
    total_flights_2023 = flights_2023.shape[0]
    delayed_flights_count = delayed_flights.shape[0]

    return total_flights_2023, delayed_flights_count

# Example usage:
# data_df = pd.read_csv("flight_data.csv")  # Assuming the DataFrame is read from a CSV file
# total_flights_2023, delayed_flights_count = otp_genpy(data_df)
# print(total_flights_2023, delayed_flights_count)