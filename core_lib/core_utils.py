import pandas as pd
import numpy as np
from pathlib import Path
#import dill
import pickle
import multiprocessing as mproc
import os
import sys
import random
from multiprocessing.dummy import Pool as ThreadPool
import asyncio
from asyncio.events import AbstractEventLoop
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial

import _thread
import traceback
import zmq
import gc
  
    
def create_request_queue(host='*',port=5555):
    context = zmq.Context()
    sender = context.socket(zmq.REP)
    context = zmq.Context()
    try:
        sender.bind("tcp://"+host+":"+str(port))
        return sender
    except Exception as e:
        print(f'error {e} in binding to Request queue')
        print(traceback.format_exc())
        return None
def delete_msg_queue(socket):
    socket.close()
    
def create_push_queue(host='127.0.0.1',port=5556):
    context = zmq.Context()
    sender = context.socket(zmq.PUSH)
    addr = "tcp://"+host+":"+str(port)
    print(addr)
    try:
        sender.bind(addr)
        return sender
    except Exception as e:
        print(f'error {e} in binding to Message queue')
        print(traceback.format_exc())
        return None
        
def push_message(data,queue):
    try:
        ret = queue.send_pyobj(data)
        return 0,ret
    except Exception as e:
        print(f'error {e} in pushing message to queue')
        print(traceback.format_exc())
        return -1,e
    

def connect_pull_queue(host='127.0.0.1',port=5556):
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    try:
        receiver.connect("tcp://"+host+":"+str(port))
        return receiver
    except Exception as e:
        print(f'error {e} in connecting to Message queue')
        print(traceback.format_exc())
        return None

def pull_message(queue):
    try:
        msg = queue.recv_pyobj()
        return msg
    except Exception as e:
        print(f'error {e} in pulling message from queue')
        print(traceback.format_exc())
        return None
    
    
def recv_message(queue):
    try:
        msg = queue.recv_pyobj()
        ack = {'message':'acknowledged'}
        queue.send_pyobj(ack)
        return msg
    except Exception as e:
        print(f'error {e} in receiving or acknowleding request')
        print(traceback.format_exc())
        return None
#import logging
#from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

'''
def create_new_logger(logger_name,fname,level_prefix):
    logger_params = get_logger_params(level_prefix)
    logging.basicConfig(level=logger_params['console_log_level'],
                        format='%(asctime)s-%(levelname)s-%(filename)s-%(lineno)d-%(funcName)s-%(message)s')
    logger = logging.getLogger(logger_name)

    handler_size = RotatingFileHandler(fname,
                                  mode='a',
                                  maxBytes=logger_params['maxBytes'],
                                  backupCount=logger_params['backupCount'])
    handler_format = logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(lineno)d-%(funcName)s-%(message)s')
    handler_size.setFormatter(handler_format)
    handler_size.setLevel(logger_params['file_log_level'])

    logger.addHandler(handler_size)
    return logger
    
def start_redis_task(data,tasks,task_type,logger):
    taskid,task = tasks.createTask(data,task_type=task_type)
    tasks.startTask(task)
'''


'''        
def parallelize(func, data):
    pool = ThreadPool(mproc.cpu_count())
    results =  pool.map(func, data)
    pool.close()
    pool.join()
    gc.collect()
    return results
'''

'''
def parallel_map(l, m):
    return parallelize(m,l)
'''
def make_partials(f,lst,**kwargs):
    x = [partial(f,e,**kwargs) for e in lst]
    return x
    
'''
async def parallelize_(calls):
    with ProcessPoolExecutor(max_workers=3) as process_pool:
        loop = asyncio.get_event_loop()
        call_coroutines = []
        for call in calls:
            call_coroutines.append(loop.run_in_executor(process_pool, call))
            
        results = await asyncio.gather(*call_coroutines)
    return results
'''

async def parallelize_(calls):
    with ThreadPoolExecutor(max_workers=3) as process_pool:
        loop = asyncio.get_event_loop()
        call_coroutines = []
        for call in calls:
            call_coroutines.append(loop.run_in_executor(process_pool, call))
            
        results = await asyncio.gather(*call_coroutines)
    return results

def parallelize(pars):
    return asyncio.run(parallelize_(pars))

def parallel_map(lst, m,**kwargs):
    pars = make_partials(m,lst,**kwargs)
    #gc.collect()
    return asyncio.run(parallelize_(pars))

# def parallelize(func, data):
#     pool = ThreadPool(mproc.cpu_count())
#     results =  pool.map(func, data)
#     pool.close()
#     pool.join()
#     return results

# def parallel_map(l, m):
#     return parallelize(m,l)

def startThread(func,params):
    try:
        _thread.start_new_thread(func,params)
    except Exception as e:
        raise Exception(f'exception {e} while creating thread')
       
   
def list_map(l, m, args=None):
    return list(pd.Series(l).apply(m, args=args))


def print_(x):
    print(x)
    sys.stdout.flush()
    #pass

def flatten_list(l):
    try:
        return sum(l, [])
    except:
        return sum(l, ())


def p_list(path):
    return list(Path(path).iterdir())

def is_str(x):
    return isinstance(x, str)

def is_array(x):
    return isinstance(x, np.ndarray)

def is_list(x):
    return isinstance(x, list)

def is_tuple(x):
    return isinstance(x, tuple)

def is_path(x):
    return isinstance(x, Path)

def path_or_str(x):
    return is_str(x) or is_path(x)

def list_or_tuple(x):
    return (is_list(x) or is_tuple(x))

def last_modified(x):
    return x.stat().st_ctime

def sorted_paths(path, key=None, suffix=None, make_str=False, map_fn=None,
                 reverse=False, only_dirs=False, full_path=True):

    if suffix is None:
        l = p_list(path)
    else:
        if isinstance(suffix, str):
            suffix = (suffix)
        l = [p for p in p_list(path) if p.suffix in suffix]
    if only_dirs:
        l = [x for x in l if x.is_dir()]
    if key is None:
        l = sorted(l, key=last_modified, reverse=True)
    else:
        l = sorted(l, key=key, reverse=reverse)
    if map_fn is not None:
        l = list_map(l, map_fn)
    if not full_path:
        l = list_map(l, lambda x:x.name)
    if make_str:
        l = list_map(l, str)
    return l
    
'''
class Worker(mproc.Process):
    def __init__(self,name):
        mproc.Process.__init__(self)
        self.task_queue = mproc.Queue()
        self.name = name

    def run(self):
        proc_name = self.name
        while True:
            print(f'Worker {self.name} Waiting for New Task')
            next_task = self.task_queue.get()
            print(f'Worker-{proc_name} got new task ')
            #try:
            result = next_task()
            print(f'Worker-{proc_name} Finished Task with result: {result}')
            #except Exception as e:
                #print(f'task failed for Worker-{proc_name} with error {e}')
            
        print(f'******Worker--{proc_name} out of loop******')
    
class WorkerQueues():
    def __init__(self,num_workers=7):
        self.workers = [Worker(str(i+1)) for i in range(num_workers)]
        for w in self.workers:
            w.start()
    def distribute_tasks(self,tasks_list):
        num_tasks = len(tasks_list)
        for i in range(num_tasks):
            worker_index = random.randint(0,len(self.workers))
            print(f'SELECTED WORKER {worker_index} ')
            self.workers[worker_index].task_queue.put(tasks_list[i])
'''
class Worker(mproc.Process):
    def __init__(self, task_queue, result_queue):
            mproc.Process.__init__(self)
            self.task_queue = task_queue
            self.result_queue = result_queue
    def run(self):
        print(f'WORKER {os.getpid()} STARTING')
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task == 'None':
                # Poison pill means shutdown
                print(f'{proc_name}: Exiting')
                self.task_queue.task_done()
                print(f'{proc_name} got exit signal ')
                break
            print(f'{proc_name} got new task ')
            result = next_task()
            self.task_queue.task_done()
            self.result_queue.put(result)
        
def task_manager(tasks_list,num_workers):
    print('TASK MANAGER STARTING')
    tasks_q = mproc.JoinableQueue()
    results_q = mproc.Queue()
    results = []
    #while True:
    print(f'Task Manager putting {num_workers} tasks in queue')
    num_tasks = len(tasks_list)
    for i in range(num_tasks):
        tasks_q.put(tasks_list[i])
        
    print(f'Creating {num_workers} workers')
    workers = [Worker(tasks_q, results_q) for i in range(num_workers)]
    for w in workers:
        #w.daemon = True
        w.start()
    
    # Add a poison pill for each consumer
    for i in range(num_tasks):
        tasks_q.put('None')

    # Wait for all of the tasks to finish
    try:
        tasks_q.join()
        print('TASK MANAGER OUT OF JOIN WITH ALL TASKS FINISHED')
    except Exception as e:
        print(f'MANAGER OUT OF JOIN WITH EXCEPTION {e}')
        for w in workers:
            if w.is_alive():
                w.terminate()
                w.join(timeout=1.0)
                
    count = 0
    while num_tasks:
        result = results_q.get()
        count +=1
        print(f'TASK {count} FINISHED')
        print(f'Result:{result}')
        results.append(result)
        num_tasks -= 1
    
    return results
        
    

def parallelize_tasks(tasks_list,num_workers=1):
    manager = mproc.Process(target=task_manager, args=(tasks_list,num_workers) )
    #manager.daemon = True
    return manager
    
def taskRunner(task):
    print('TASK RUNNER CALLING TASK')
    ret = task()
    print(f'TASK RUNNER OUT OF TASK--ret = {ret}')
    return ret
    
    

    
    
        