# %%
# Import the necessary libraries and data

import os, locale, warnings
from datetime import datetime, timedelta
import OTP # type: ignore

# Set the locale for the script
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# Ignore warnings
warnings.filterwarnings('ignore')

# Get the current working directory
if 'home_path' not in locals():
    home_path = os.getcwd()

# Define the output folder
out_folder = os.path.join(home_path, datetime.now().strftime('output_%y%m%d'))
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

# Read the data using the OTP.read_otp function
data_path = os.path.join(home_path, 'otp-raw')
data_df = OTP.read_otp(data_path)

# Pick only the service_type needed for the analysis
service_type = ['G', 'J']
data_df = data_df[data_df['Service Type'].isin(service_type)]
print(f'Picked up {len(data_df)} flights of specific service type.')


# %%
# Define the question and ask the GPT model

# Define the question to ask
question = f'How many JX802 flights departed? How many of them were delayed? Please tell me the answer for each month in 2023 by outputing a file "otp_stat_2023.csv"'
print(f'Ask: {question}')

# Define the terms in the DataFrame
definition1 = '\
    otp_by_period(data_df, YYYY, MM=None, FLT=None) is a Python function \
    for calculating on-time performance (OTP) of Starlux flights. \
    YYYY is the 4-digits string of year. \
    MM is the 2-digits string of month, quarter (i.e. Q1 to Q4), or half-year (i.e. H1 to H2). \
    FLT is the string of flight number (i.e. JX802). \
    MM and FLT are optional, which should be None if not specified. \
    data_df, of course, the raw data that contains all informations we need. \
    The returned values are the total number of flights, the number of delayed flights, \
    and the ratio betweeb these two (delay rate). \
    '

# Define the request to ask the question
request1 = '\
    Please provide the Python script used to calculate the answer using otp_by_period. \
    Pack the script into a function named otp_genpy(data_df). \
    Must remember to import the necessary libraries. \
    To call otp_by_period function, OTP must be imported. \
    DO NOT response anything which is not part of python code. \
    IMPORTANT: Remove all texts which are not part of Python code!!!!!! \
    Make sure the script is correct and can be run without any errors. \
    Overwrite the existing file if it already exists. \
    No additional calculation in otp_genpy is needed. \
    Please directly return the three values returned by otp_by_period. \
    '

# Define the rules for the question
rules = ''

# Define the prompt to ask the question
prompt1 = f'{definition1} {question} {rules} {request1}'

# Ask the question using the OTP.ask_gpt function
answer, tokens, latency = OTP.ask_gpt(prompt1)
answer1 = '\n'.join(line for line in answer.split('\n') if not line.startswith('```'))

# Print the answer, tokens used, and latency
print(f'Token used: {tokens} \nLatency: {latency} seconds')

# Save the answer as a Python script
with open('otp_genpy.py', 'w') as f:
    f.write(answer1)


# %%
# Answer the question in a fluent and concise manner

from otp_genpy import otp_genpy # type: ignore

# Call the otp_result function with the data_df DataFrame
otp_result = otp_genpy(data_df)

# Define the prompt to ask the question
request2 = '\
    The three values of answer mean the total number of flights, the number of delayed flights, \
    and the ratio betweeb these two (delay rate), respectively. \
    Please refine the whole answer to make it more fluent and concise. \
    Please answer the delay rate in percentage format. \
    DO NOT response anything that is not related to the answer. \
    DO NOT response anything in code block. \
    If there are more than one period, DO NOT response any number. \
    '
prompt2 = f'{question} The answer is {otp_result}. {request2}'

# Ask the question using the OTP.ask_gpt function
answer2, tokens, latency = OTP.ask_gpt(prompt2)

# Print the answer, tokens used, and latency
print(f'Answer: {answer2}')
print(f'Token used: {tokens} \nLatency: {latency} seconds')


# %%
