import os

remote = "10.231.229.20"
signal_folder = "/data/bnf/tmp/.signal/"
password = os.environ["PASS_LENNIE"]


### test ###
remote_test = "localhost"
signal_folder_test = "tests/.signal/"
test_delay = 10


queue_vals = {
    'low': 40000,
    'normal': 30000,
    'high': 20000,
    'highest': 10000,
    'lowest': 50000
}



