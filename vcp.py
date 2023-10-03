import os
import config
import time
import sys
import paramiko
import base64


def find_locally(signal_folder,queue):
    os_list = list(os.listdir(signal_folder)) # filter for files only - FIXME
    results = [signal_folder+i for i in os_list if i.endswith('.request')]
    for file in results:
        fd = os.open(file, os.O_RDONLY)
        request = os.read(fd,1000)
        request = request.decode().split('\n')
        os.close(fd)
        queue = add_to_queue(queue,request)
        rename_locally(file,".queued")
    return queue

def find_ssh(client,signal_folder,queue):
    stdin, stdout, stderr = client.exec_command( 'find '+signal_folder+' -name "*.request" ')
    for line in stdout:
        request = []
        line = line.strip('\n')
        sin, sout, serr = client.exec_command( 'cat '+line )
        for row in sout:
            row = row.strip('\n')
            request.append(row)
        queue = add_to_queue(queue,request)
        rename_ssh(line,".queued")
    return queue

def add_to_queue(queue,request):
    qval = config.queue_vals[request[2]]
    ## THis can probably be done more efficiently
    if qval in queue:
        for i in range(qval,qval+9999,1):
            if i not in queue:
                tmp = {}
                tmp['file'] = request[0]
                tmp['to'] = request[1]
                queue[i] = tmp
                break
    else:
        tmp = {}
        tmp['file'] = request[0]
        tmp['to'] = request[1]
        queue[config.queue_vals[request[2]]] = tmp
    #depending on prio add to place in queue
    return queue


def fetch_data(data,to_server):
    command = "scp "+data+" "+to_server
    code = 1
    #run scp, return 1 if success
    return code

def rename_locally(file,end):
    new_name = file+end
    os.rename(file,new_name)
    return 1

def rename_ssh(file,end):
    new_file = file+end
    stdin, stdout, stderr = client.exec_command( 'mv '+file+' '+new_file)
    return 1

def connect_to_ssh(server):
    client = paramiko.SSHClient()
    host_keys = client.load_system_host_keys()
    client.connect(server, username='viktor', password=config.password)
    return client


test = 1
ssh = 1
queue = {}

if test:
    os.popen('cp tests/1234.request tests/.signal/1233.request') 
    os.popen('cp tests/1234.request tests/.signal/1234.request') 
    os.popen('cp tests/1235.request tests/.signal/1235.request') 
    os.popen('cp tests/1236.request tests/.signal/1236.request')
    server = config.remote_test
    signal_folder = config.signal_folder_test
    scriptroot = sys.path[0]
    signal_folder = scriptroot+"/"+signal_folder
else:
    server = config.remote
    signal_folder = config.signal_folder    
if ssh:
    client = connect_to_ssh(server)

while(1):
    ## sleep has to be at start, os.read buffering issues
    time.sleep(2)
    if ssh:
        queue = find_ssh(client,signal_folder,queue)
    else:
        queue = find_locally(signal_folder,queue)
    # check connectivity to remote
    # print current queue on exit
    qkeys = list(queue.keys())
    qkeys.sort()
    queue_sorted = {i:queue[i] for i in qkeys}
    print("CURRENT QUEUE")
    for q in queue_sorted:
        print(q,end="\t")
        print(queue[q]['file'],end="\t")
        print(queue[q]['to'])
    print("\n\n")
    # perform first task, highest prio
    #fetch_data(queue[1],to_server)
    

