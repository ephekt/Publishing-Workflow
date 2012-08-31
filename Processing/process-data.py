import redis
from redis._compat import b, next
from redis.exceptions import ConnectionError
import json
from paramiko import SSHClient, SFTPClient
import error_mail
from functools import partial

#Hostname (ip) of the redis server to communicate with
REDIS_HOST = '10.12.27.245'
#Location of machine info
MACHINE_INFO = '/etc/delphi/data/machineinfo.json'
#Name of the channel to listen to for jobs
PROCESS_CHANNEL = 'Process City Data'
#Key for the work queue where jobs are stored
WORK_QUEUE = 'processCD'
#Message sent on the work queue to indicate new work is available
WORK_MESSAGE = 'process'
#Local path to put temporary data for processing
TEMP_PATH = '.'

'''
Initializes the connection to the redis and server
'''
def init():
    r = redis.StrictRedis(host=REDIS_HOST)
    info = {}
    try:
        identfile = open(MACHINE_INFO)
        info = json.loads(identfile.readline())
        info = info['identity']
    except: 
        #just leave the info as an empty object
        pass

    return r, info

def work_loop():
    def pop():
        return r.lpop(WORK_QUEUE)
    while True:
        job = error_mail.redis_func(partial(pop), machineinfo)       
        if job == None:
            break
        job = json.loads(job)

        datapath = job['path']
        host = job['host']
        channel = job['hash']

        client = SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(host)
        sftp_client = ssh_client.open_sftp()

        #TODO: Datapath is list
        sftp_client.get(datapath, TEMP_PATH)
        #Call Matt's stuff
        
    
def listen_loop():
    pubsub = r.pubsub()
    def subscribe():
        pubsub.subscribe(PROCESS_CHANNEL)

    error_mail.redis_func(partial(subscribe), machineinfo)

    def listen():
        return next(pubsub.listen())
    while True:
        msg = error_mail.redis_func(partial(listen), machineinfo)

        if msg and msg == WORK_MESSAGE:
            work_loop()

r, machineinfo = init()
work_loop()
listen_loop()
