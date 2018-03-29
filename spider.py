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
    queueDict = dict()
    crawledDict = dict()
    lock = threading.Lock()
    threadName = None

    def __init__(self, projectNames, baseUrls, domainNames, articleTitle, articleDate, articleBody):
        Spider.starters["projectNames"] = projectNames
        Spider.starters["baseUrls"] = baseUrls
        Spider.starters["domainNames"] = domainNames
        Spider.starters["articleTitle"] = articleTitle
        Spider.starters["articleDate"] = articleDate
        Spider.starters["articleBody"] = articleBody
        Spider.queue_file = 'workingQueue.txt'
        Spider.crawled_file = 'workingCrawled.txt'
        self.boot()
        for prname in projectNames:
            Spider.getLinkSets(prname+"/")
        #self.crawl_page('First spider', Spider.pickBaseLink())

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        [create_storage_dir(prnames) for prnames in Spider.starters["projectNames"]]
        [create_data_files(project, Spider.starters["baseUrls"][k]) for k, project in enumerate(Spider.starters["projectNames"])]

    @staticmethod
    def getLinkSets(project=""):
        q = file_to_set(project+""+Spider.queue_file)
        Spider.queueDict[project.split("/")[0]] = q

        c = file_to_set(project+""+Spider.crawled_file)
        Spider.crawledDict[project.split("/")[0]] = c
        print "************************************"
        print project.split("/")[0], Spider.crawledDict[project.split("/")[0]]
        print "************************************"

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
        currentProjectName = Spider.updateCurrentProjectName(page_url)[1]
        print Spider.crawledDict[currentProjectName]
        try:
            if page_url not in Spider.crawledDict[currentProjectName]:
                Spider.add_links_to_queue(Spider.gather_links(Spider.updateCurrentProjectName(page_url), page_url), page_url)
                time.sleep(2)
                # TODO add a sleep by threadnames
        except Exception as e:
            print "<<< At crawl", Spider.threadName, "Error:", e
            traceback.print_exc()
            #pass

    # create a static method to pick projectName.
    @staticmethod
    def updateCurrentProjectName(url):
        for k, b in enumerate(Spider.starters["domainNames"]):
            if b == get_domain_name(url):
                print "project name >>> "+Spider.starters["projectNames"][k], "domain name >>> "+get_domain_name(url)
                return [k, Spider.starters["projectNames"][k]]

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(projectDetails, page_url):
        startersIndex = projectDetails[0]
        currentProjectName = projectDetails[1]

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
                tag = Spider.starters["articleDate"][startersIndex]['tag']
                classing = Spider.starters["articleDate"][startersIndex]['class']
                meta = Spider.starters["articleDate"][startersIndex]['meta']
                tag = createNone(tag)
                classing = createNone(classing)
                meta = createNone(meta)
                soup = BeautifulSoup(html_bytes)
                soup = BeautifulSoup(html_bytes)
                if (verifiedDate is not False) or (Spider.starters["baseUrls"][startersIndex] == page_url):
                    if verifiedDate is not False:
                        dateDifference = datetime.datetime.now().date() - verifiedDate.date()
                        days = dateDifference.days
                        if days <= 1:
                            print verifiedDate, dateDifference
                            Spider.save_the_html(html_string, currentProjectName, page_url)
                    else:
                        Spider.save_the_html(html_string, currentProjectName, page_url)
                else:
                    return set()
            finder = LinkFinder(Spider.currentBaseUrl, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    @staticmethod
    def save_the_html(html, projectName, link):
        Spider.lock.acquire()
        try:
            file_path = os.path.join(
                    projectName, "htmlFiles")
            create_storage_dir(file_path)
            file_name = os.path.join(file_path, b16encode(link))
            stored_file = open(file_name, "w")
            stored_file.write(html.encode("utf-8"))
            stored_file.close()
        finally:
            Spider.lock.release()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links, page_url):
        Spider.lock.acquire()
        try:
            currentProjectName = Spider.updateCurrentProjectName(page_url)[1]
            for url in links:
                if (url in Spider.queueDict[currentProjectName]) or (url in Spider.crawledDict[currentProjectName]):
                    continue
                if get_domain_name(url) not in Spider.starters["domainNames"]:#look up in a list
                    continue
                Spider.queueDict[currentProjectName].add(url)
                Spider.crossCheck(page_url, currentProjectName)
        finally:
            Spider.lock.release()


    @staticmethod
    def crossCheck(page_url, currentProjectName):
        if page_url in Spider.queueDict[currentProjectName]:
            Spider.queueDict[currentProjectName].remove(page_url)
            opider.crawled.add(page_url)
        Spider.update_files(currentProjectName)

    @staticmethod
    def update_files(page_url):
        set_to_file(Spider.queueDict[currentProjectName], currentProjectName+"/"+Spider.queue_file)
        set_to_file(Spider.crawledDict[currentProjectName], currentProjectName+"/"+Spider.crawled_file)
