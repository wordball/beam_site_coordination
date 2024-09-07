# Written by Aditya Murali


import pandas as pd



# Data Processing Functions
# Some of these functions hopefully won't be used if the google forms are standardized properly
import re
def standardize_time(time):
    time = re.sub(r"11-12pm", "11:00am-12:00pm", time)
    time = re.sub(r"12-1pm", "12:00-1:00pm", time)
    time = re.sub(r"1-2pm", "1:00-2:00pm", time)
    time = re.sub(r"2-3pm", "2:00-3:00pm", time)
    time = re.sub(r"3-4pm", "3:00-4:00pm", time)
    time = re.sub(r"4-5pm", "4:00-5:00pm", time)
    time = re.sub(r"5-6pm", "5:00-6:00pm", time)
    time = re.sub(r"am", "AM", time)
    time = re.sub(r"pm", "PM", time)
    return time

#Assuming a person's availabilities are written one after another with commas as separators
#This function also accounts for people who only are available at one time(Grrrrr)
def extract_times(text, sep = ","):
    if ',' not in text:
        times = [text]
    else:
        times = text.split(sep = ',')
    times = [standardize_time(time.strip()) for time in times]
    return times

#Orders a list of decal people by how busy they are (most busy to least busy)
def order_by_availabilities(lst_of_people):
    ordered = sorted(lst_of_people, key = lambda x: len(x.availabilities))
    return ordered