import redis
from redis._compat import b, next
from redis.exceptions import ConnectionError
import json
from paramiko import SSHClient, SFTPClient

sys.path.insert(0, os.path.abspath('../Common'))
import error_mail

#Hostname (ip) of the redis server to communicate with
REDIS_HOST = '10.12.27.245'
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
    r = redis.StrictRedis(host=Const.REDIS_HOST)
    return r

def work_loop():
    def pop():
        return r.lpop(Const.LOG_KEY)
    while True:
        job = error_mail.redis_func(partial(pop), machineinfo)       
        if job == None:
            break
        job = json.loads(job)

        datapath = job['path']
        host = job['host']
        channel = job['hash']

        client = SSHClient()
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

r = init()
work_loop()
listen_loop()
