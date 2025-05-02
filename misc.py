'''

Miscellaneous functions that do not fit into other categories.

Used throughout the bot

'''



import time



def wait_16_minutes(start_time):
    elapsed = time.time() - start_time
    time.sleep(max(0, 960 - elapsed))