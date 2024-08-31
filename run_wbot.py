import os
import sys
from datetime import time, date, datetime

print(sys.path)
print(datetime.now())
#sys.
#os.
#sys.
while True:
    try:
        exec(open('wbot.py').read())
    except Exception as err:
        print(datetime.now(), ' ',err)
        continue