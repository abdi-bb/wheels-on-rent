'''
Module: shared_variables
'''
import datetime


def get_greeting():
    '''Say User Good Morning/Good Afternoon/Good Eveninig'''
    current_time = datetime.datetime.now()
    hour = current_time.hour

    if 5 <= hour < 12:
        return "Good Morning!"
    elif 12 <= hour < 17:
        return "Good Afternoon!"
    elif 17 <= hour < 21:
        return "Good Evening!"
    else:
        return "Welcome!"
