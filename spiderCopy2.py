from urllib import urlopen
import robotparser
from link_finder import LinkFinder
import os
from domain import *
from general import *
from checks import *
from base64 import b16encode
from bs4 import BeautifulSoup
import time
import threading
import traceback

class Spider:
    AGENT_NAME = 'HEADLINER'
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    robots_file = ''
    currentBaseUrl = ''
    currentProjectName = ''
    startersIndex = None
    starters = {}
    queue = set()
    crawled = set()
    lock = threading.Lock()
    threadName = None

    def __init__(self, projectNames, baseUrls, domainNames, articleTitle, articleDate, articleBody):
        #Spider.project_name = project_name
        #Spider.base_url = base_url
        #Spider.domain_name = domain_name

        #modifications
        Spider.starters["projectNames"] = projectNames
        Spider.starters["baseUrls"] = baseUrls
        Spider.starters["domainNames"] = domainNames
        Spider.starters["articleTitle"] = articleTitle
        Spider.starters["articleDate"] = articleDate
        Spider.starters["articleBody"] = articleBody
        Spider.queue_file = 'workingQueue.txt'
        Spider.crawled_file = 'workingCrawled.txt'
        self.boot()
        #self.crawl_page('First spider', Spider.pickBaseLink())




    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        [create_storage_dir(prnames) for prnames in Spider.starters["projectNames"]]
        [create_data_files(project, Spider.starters["baseUrls"][k]) for k, project in enumerate(Spider.starters["projectNames"])]

    @staticmethod
    def bootProceed(project=""):
        q = file_to_set(project+""+Spider.queue_file)
        for i in q:
            Spider.queue.add(i)

        c = file_to_set(project+""+Spider.crawled_file)
        for x in c:
            Spider.crawled.add(x)





    # check robot permissions on site
    @staticmethod
    def check_robots(url):
        robots_parser = robotparser.RobotFileParser()
        robots_parser.set_url(Spider.currentBaseUrl+'/robots.txt')
        robots_parser.read()
        if not robots_parser.can_fetch(Spider.AGENT_NAME, url):
            return False
        return True





    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(threadName, page_url):
        Spider.threadName = threadName
        try:
            if page_url not in Spider.crawled:
                projectNameAndIndex = Spider.updateCurrentProjectName(page_url)
                Spider.startersIndex = projectNameAndIndex[0]
                Spider.currentProjectName = projectNameAndIndex[1]
                Spider.bootProceed(Spider.currentProjectName+"/")
                """
                print "##", Spider.threadName, "## index", Spider.startersIndex, "##proj", Spider.currentProjectName, "##"


                print(Spider.threadName + ' now crawling ' + page_url, "---"+Spider.currentProjectName+"-------")
                print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
                """
                Spider.add_links_to_queue(Spider.gather_links(threadName, page_url))
                if page_url in Spider.queue:
                    Spider.queue.remove(page_url)
                    Spider.crawled.add(page_url)
                Spider.update_files()
                print "threadName >>> ", Spider.threadName, "Queue length >>> ", len(Spider.queue)
                time.sleep(2)
                # TODO add a sleep by threadnames
        except Exception as e:
            print "<<< At crawl", Spider.threadName, "Error:", e
            traceback.print_exc()
            #pass




    @staticmethod
    def pickBaseLink():
        for k, c in enumerate(Spider.starters["baseUrls"]):
            if c not in Spider.crawled:
                Spider.currentBaseUrl = c
                Spider.currentProjectName = Spider.starters["projectNames"][k]
                print "base url =====> ", Spider.currentProjectName, Spider.currentBaseUrl
                return Spider.currentBaseUrl




    @staticmethod
    def setSiteParameters():
        return False




    # create a static method to pick projectName.
    @staticmethod
    def updateCurrentProjectName(url):
        for k, b in enumerate(Spider.starters["domainNames"]):
            if b == get_domain_name(url):
                print "project name >>> "+Spider.starters["projectNames"][k], "domain name >>> "+get_domain_name(url)
                return [k, Spider.starters["projectNames"][k]]



    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(thread, page_url):
        def createNone(x):
            if x is '':
                x = None
                return x
            return x

        html_string = ''
        verifiedDate = False
        days = False
        try:
            response = urlopen(page_url)
            print response
            if 'text/html' in response.headers.get('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
                # at this point we assess if we shall save
                # based publishing date date IF NOT THROW EXCEPTION
                # Spider.dates[Spider.startersIndex]
                """Spider.lock.acquire()"""
                tag = Spider.starters["articleDate"][Spider.startersIndex]['tag']
                classing = Spider.starters["articleDate"][Spider.startersIndex]['class']
                meta = Spider.starters["articleDate"][Spider.startersIndex]['meta']
                tag = createNone(tag)
                classing = createNone(classing)
                meta = createNone(meta)
                soup = BeautifulSoup(html_bytes)
                soup = BeautifulSoup(html_bytes)
                if (verifiedDate is not False) or (Spider.starters["baseUrls"][Spider.startersIndex] == page_url):
                    if verifiedDate is not False:
                        dateDifference = datetime.datetime.now().date() - verifiedDate.date()
                        days = dateDifference.days
                        if days <= 1:
                            print verifiedDate, dateDifference
                            Spider.save_the_html(html_string, page_url)
                    else:
                        Spider.save_the_html(html_string, page_url)
                else:
                    return set()
                """Spider.lock.release()"""
            finder = LinkFinder(Spider.currentBaseUrl, page_url)
            finder.feed(html_string)
            # TODO store the html_string
            # probably using another class
            # TODO include the respect for the
            # robot.txt file
            # TODO indexing the forward index and
            # the inverted index
            # TODO smartly crawl -- create a limit
            # TODO can there he a way to compress
            # the files... incase they are too big
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()
















    @staticmethod
    def save_the_html(html, link):
        file_path = os.path.join(
                Spider.currentProjectName, "htmlFiles")
        create_storage_dir(file_path)
        file_name = os.path.join(file_path, b16encode(link))
        stored_file = open(file_name, "w")
        stored_file.write(html.encode("utf-8"))
        stored_file.close()










    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if get_domain_name(url) not in Spider.starters["domainNames"]:#look up in a list
                continue
            Spider.queue.add(url)






    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.currentProjectName+"/"+Spider.queue_file)
        set_to_file(Spider.crawled, Spider.currentProjectName+"/"+Spider.crawled_file)
