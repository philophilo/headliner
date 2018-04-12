import threading
from Queue import Queue
from spiderStarter import Spider
from domain import get_domain_name
from general import readSourceFile, file_to_set

projectNames = []
popNames = []
QUEUE_FILE = 'workingQueue.txt'
CRAWLED_FILE = 'workingCrawled.txt'
NUMBER_OF_THREADS = 8
queue = Queue()
queued_links = set()


def starter():
    contents = readSourceFile()
    domains, baseUrls, articleTitle, articleDate, articleBody, lang = zip(
        *[(get_domain_name(v['link']['siteUrl']), v['link']['siteUrl'],
           v['title'], v['date'], v['articleBody'], v['language'])
          for k, v in contents.iteritems()])
    global projectNames
    projectNames = contents.keys()
    Spider(projectNames, list(baseUrls), list(domains), list(articleTitle),
           list(articleDate), list(articleBody), list(lang))


# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs(links):
    for link in links:
        queue.put(link)
    queue.join()
    crawl()


# Check if there are items in the queue, if so crawl them
def crawl():
    queued_links = list()
    for prname in projectNames:
        prname_links = file_to_set(prname+'/'+QUEUE_FILE)
        if prname_links is not None:
            for link in prname_links:
                queued_links.append(link)
    create_jobs(queued_links)


starter()
create_workers()
crawl()
