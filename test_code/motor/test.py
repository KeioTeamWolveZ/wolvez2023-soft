from datetime import datetime
import time

print(datetime.now())
i=0
while i < 60*120/5:
    i+=1
    print("current time: "+str(datetime.now()))
    time.sleep(5)