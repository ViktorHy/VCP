import os
import time
import config
import random
import sys

def demand_copy(signal,file,transfer_loc):
    rnd = str(random.randint(0, 100000))
    unique_id = str(int(time.time())) + "-" + rnd
    signal_file_path = os.path.join(signal, unique_id + ".request")
    with open(signal_file_path, 'w') as signal_fh:
        signal_fh.write(f"{file}\n{transfer_loc}")

    started = False
    waiting_time = 10 # this needs to be adapted to the biggest file and its expected transfer-time
    cnt = 0
    while(1):
        time.sleep(waiting_time)
        if not started and os.path.exists(os.path.join(signal, unique_id + '.queued')):
            print(" Transferring.", end="")
            started = True
        if os.path.exists(os.path.join(signal, unique_id + '.done')):
            print(" Done!")
            return 0
        if os.path.exists(os.path.join(signal, unique_id + '.identical')):
            print(" Done!")
            return 0
        if os.path.exists(os.path.join(signal, unique_id + '.failed')):
            print(" Transfer failed")
            return 2
        if os.path.exists(os.path.join(signal, unique_id + '.fnf')):
            print(" Could not find file to transfer")
            return 3
        if waiting_time * cnt > 3000 and not os.path.exists(os.path.join(signal, unique_id + '.queued')):
            print(" No response from daemon. Giving up!")
            return 4
        cnt = cnt+1



test = config.test

if test:
    signal_folder = config.signal_folder_test
    scriptroot = sys.path[0]
    signal_folder = scriptroot+"/"+signal_folder
    request = ["/mnt/c/Users/212814/dev/vcp/tests/copyme5","/mnt/c/Users/212814/dev/vcp/tests/transfer"]
else:
    signal_folder = config.signal_folder 
    request = []

exitcode = demand_copy(signal_folder,request[0],request[1])

exit(code=exitcode)
