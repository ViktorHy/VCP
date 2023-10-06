import os
import config
import time
import sys
from paramiko import SSHClient
import base64
from scp import SCPClient, SCPException
import json


def find_ssh(client,signal_folder,queue):
    stdin, stdout, stderr = client.exec_command( 'find '+signal_folder+' -name "*.request" ')
    for line in stdout:
        noend = line.split('.')
        line = noend[0]
        request = []
        line = line.strip('\n')
        sin, sout, serr = client.exec_command( 'cat '+line+".request" )
        for row in sout:
            row = row.strip('\n')
            request.append(row)
        queue = add_to_queue(queue,request,line)
        rename_ssh(client,line,line+".queued")
    return queue

def add_to_queue(queue,request,line):
    if len(request) > 2:
        qval = config.queue_vals[request[2]]
    else:
        qval = 30000
    tmp = {}
    tmp['file'] = request[0]
    tmp['to'] = request[1]
    tmp['request'] = line
    ## This can probably be done more efficiently
    if qval in queue:
        for i in range(qval,qval+9999,1):
            if i not in queue:
                queue[i] = tmp
                break
    else:
        queue[qval] = tmp
    return queue


def fetch_data(data,restore_path,client):
    scp = SCPClient(client.get_transport())
    scp.put(data,remote_path=restore_path)
    scp.close()
    if compare_sizes(data,restore_path+"/"+os.path.basename(data),client):
        return 1
    else:
        return 0

def compare_sizes(file,file2,client):
    file_size = os.path.getsize(file)
    command = 'stat -c%s '+file2
    stdin, stdout, stderr = client.exec_command( command )
    file2_size = []
    for i in stdout:
        file2_size.append(i.strip('\n'))
    if int(file_size) == int(file2_size[0]):
        return 1
    else:
        return 0


def rename_ssh(client,file,new_file):
    client.exec_command( 'mv '+file+' '+new_file)
    return 1

def connect_to_ssh(server):
    client = SSHClient()
    host_keys = client.load_system_host_keys()
    client.connect(server, username='viktor', password=config.password)
    return client

    


test = config.test

# make queue loadable at start to resume if vcp dies for some reason. JSON output current queue
queue = {}

if test:
    os.popen('cp tests/1232.request tests/.signal/1232.request')
    os.popen('cp tests/1233.request tests/.signal/1233.request') 
    os.popen('cp tests/1234.request tests/.signal/1234.request') 
    os.popen('cp tests/1235.request tests/.signal/1235.request') 
    os.popen('cp tests/1236.request tests/.signal/1236.request')
    server = config.remote_test
    signal_folder = config.signal_folder_test
    scriptroot = sys.path[0]
    signal_folder = scriptroot+"/"+signal_folder
    restore_folder = scriptroot+"/"+config.restore_folder_test
else:
    server = config.remote
    signal_folder = config.signal_folder
    restore_folder = config.restore_folder

client = connect_to_ssh(server)

while(1):
    ## sleep has to be at start, os.read buffering issues
    time.sleep(2)
    # check connectivity to remote
    queue = find_ssh(client,signal_folder,queue)
    # print current queue on exit
    qkeys = list(queue.keys())
    qkeys.sort()
    queue = {i:queue[i] for i in qkeys}
    print("CURRENT QUEUE")
    if queue:
        do_me = next(iter(queue))
    else:
        continue
    if not os.path.exists(queue[do_me]['file']):
        rename_ssh(client,queue[do_me]['request']+".queued",queue[do_me]['request']+".fnf")
        del(queue[do_me])
    else:
        if fetch_data(queue[do_me]['file'],restore_folder,client):
            print("data transfered successfully")
            rename_ssh(client,queue[do_me]['request']+".queued",queue[do_me]['request']+".done")
            del(queue[do_me])
    for q in queue:
        print(q,end="\t")
        print(queue[q]['file'],end="\t")
        print(queue[q]['to'],end="\t")
        print(queue[q]['request'])
    print("\n\n")
    with open('queue.json', 'w') as fp:
        json.dump(queue, fp)

    

