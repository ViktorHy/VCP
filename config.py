import os

remote = "10.231.229.20"
signal_folder = "/data/bnf/tmp/.signal/"
restore_folder = "/data/bnf/tmp/"
password = os.environ["PASS_LENNIE"]


### test ###
test = 1
remote_test = "localhost"
signal_folder_test = "tests/.signal/"
restore_folder_test = "tests/transfer/"
test_delay = 10


queue_vals = {
    'low': 40000,
    'normal': 30000,
    'high': 20000,
    'highest': 10000,
    'lowest': 50000
}



