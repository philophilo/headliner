import threading
from Queue import Queue

threadNumber = 2
incomingNumbers = set()
finishedNumbers = set()
wString = "python"
queue = Queue()
"""
def createWorkers():
    for _ in range(threadNumber):
        t = threading.Thread(target=working)
        t.deamon = True
        t.start

def working():
    print "hi"
    while True:
        n = queue.get()
        print n, threading.current_thread().name
        workLoad(threading.current_thread().name, n)
        queue.task_done()

def createJobs():
    print "creating"

    if queue.empty:
        print "hello"#queue.get()
    for i in range(10):
        print i
        queue.put(i)
    queue.join()





def workLoad(name, i):
    print name, i
    if i not in finishedNumbers:
        for s in wString:
            print name, i, s
        finishedNumbers.add(i)
print "theWorkers"
createWorkers()
print "jobsNext"
creiateJobs()
"""


def do_stuff(q):
    while True:
        n = q.get()
        print n
        #hello(threading.current_thread().name, n)
        q.task_done()

q = Queue()
numthreads = 10
"""
def hello(name, k):
    print name, k
"""

def createWorkers():
    for i in range(numthreads):
        worker = threading.Thread(target=do_stuff, args=(q,))
        worker.setDaemon(True)
        worker.start()

def createJobs():
    for x in range(100):
        q.put(x)
    q.join()

createWorkers()
createJobs()
