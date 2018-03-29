from urllib import urlopen
import robotparser
from link_finder import LinkFinder
import os
from domain import *
from general import *
from checks import *
from base64 import b16encode
from bs4 import BeautifulSoup
from Queue import Queue
import time
import threading
import traceback

class Spider:
    AGENTNAME = 'HEADLINER'
    starters = dict()
    queueDict = dict()
    crawledDict = dict()
    generalQueue = set()
    queueFile = 'workingQueue.txt'
    crawledFile = 'workingCrawled.txt'

    def __init__(self, projectNames, baseUrls, domainNames, articleTitle, articleDate, articleBody, articleLang):
        Spider.starters["projectNames"] = projectNames
        Spider.starters["baseUrls"] = baseUrls
        Spider.starters["domainNames"] = domainNames
        Spider.starters["articleTitle"] = articleTitle
        Spider.starters["articleDate"] = articleDate
        Spider.starters["articleBody"] = articleBody
        Spider.starters["articleLang"] = articleLang
        Spider.boot()
        for prname in projectNames:
            Spider.getLinkSets(prname+"/")


    @staticmethod
    def boot():
        [create_storage_dir(prnames) for prnames in Spider.starters["projectNames"]]
        [create_data_files(project, Spider.starters["baseUrls"][k]) for k, project in enumerate(Spider.starters["projectNames"])]

    @staticmethod
    def getLinkSets(project=""):
        initialQueue = file_to_set(project+""+Spider.queueFile)
        Spider.queueDict[project.split("/")[0]] = initialQueue

        initialCrawled = file_to_set(project+""+Spider.crawledFile)
        Spider.crawledDict[project.split("/")[0]] = initialCrawled

    @staticmethod
    def check_robots(url):
        robots_parser = robotparser.RobotFileParser()
        robots_parser.set_url(Spider.currentBaseUrl+'/robots.txt')
        robots_parser.read()
        if not robots_parser.can_fetch(Spider.AGENTNAME, url):
            return False
        return True

    @staticmethod
    def crawl_page(threadName, pageUrl):
        print ".......Start", threadName, pageUrl
        projectDetails = Spider.updateCurrentProjectName(pageUrl)
        try:
            if Spider.crawledDict[projectDetails[1]] is None or pageUrl not in Spider.crawledDict[projectDetails[1]] or pageUrl in Spider.starters["baseUrls"]:
                #print threadName, pageUrl, projectDetails[1]
                Spider.addLinksToQueue(Spider.gatherLinks(projectDetails, pageUrl, threadName), projectDetails[1], pageUrl, threadName)
        except Exception as e:
            print ">>> At crawl:", threadName, "Error:", e

    @staticmethod
    def updateCurrentProjectName(url):
        for key, name in enumerate(Spider.starters["domainNames"]):
            if name == get_domain_name(url):
                return [key, Spider.starters["projectNames"][key]]

    @staticmethod
    def gatherLinks(projectDetails, pageUrl, threadName):
        currentIndex = projectDetails[0]
        currentName = projectDetails[1]

        def createNone(x):
            if x is '':
                x = None
                return x
            return x

        htmlString = ''
        verifiedDate = False
        days = False

        try:
            response = urlopen(pageUrl)
            if 'text/html' in response.headers.get('content-Type'):
                htmlBytes = response.read()
                htmlString = htmlBytes.decode("utf-8")
                tag = createNone(Spider.starters['articleDate'][currentIndex]['tag'])
                classing = createNone(Spider.starters["articleDate"][currentIndex]['class'])
                meta = createNone(Spider.starters["articleDate"][currentIndex]['meta'])
                tagLang = createNone(Spider.starters['articleLang'][currentIndex]['tag'])
                classingLang = createNone(Spider.starters["articleLang"][currentIndex]['class'])
                metaLang = createNone(Spider.starters["articleLang"][currentIndex]['meta'])
                classingText = createNone(Spider.starters['articleBody'][currentIndex]['class'])
                soup = BeautifulSoup(htmlBytes)
                verifiedDate = verifyPublicationDate(soup, tag, classing, meta)
                verifiedLang = verifyLanguage(soup, tagLang, classingLang, metaLang)
                if (verifiedDate is not False) or (Spider.pickBaseLink(currentIndex) == pageUrl):
                    print "++++detected++++", verifiedDate
                    if verifiedDate is not False:
                        dateDifference = datetime.datetime.now().date() - verifiedDate.date()
                        days = dateDifference.days
                        print "~~~~", days, "day(s)"
                        if days <= 1 and verifyArticleContent(soup, classingText) and verifiedLang and len(Spider.queueDict[currentName]) < 100:
                            print ":::>>day", threadName, currentName, pageUrl
                            Spider.saveTheHtml(htmlString, currentName, pageUrl, threadName)
                        elif Spider.pickBaseLink(currentIndex) == pageUrl:
                            Spider.saveTheHtml(htmlString, currentName, pageUrl,threadName)
                        else:
                            return set()
                    else:
                        print ":::>>day", threadName, currentName, pageUrl
                        Spider.saveTheHtml(htmlString, currentName, pageUrl, threadName)
                else:
                    return set()
            finder = LinkFinder(Spider.pickBaseLink(currentIndex), pageUrl)
            finder.feed(htmlString)
        except Exception as e:
            print ">>> At gatherLinks", threadName, "Error:", e
            return set()

        return finder.page_links()

    @staticmethod
    def pickBaseLink(index):
        return Spider.starters["baseUrls"][index]

    @staticmethod
    def saveTheHtml(html, projectName, link, threadName):
        #Spider.lock.acquire()
        print "====>> saving:", threadName, link
        try:
            file_path = os.path.join(
                        projectName, "htmlFiles")
            create_storage_dir(file_path)
            file_name = os.path.join(file_path, b16encode(link))
            stored_file = open(file_name, "w")
            stored_file.write(html.encode("utf-8"))
            stored_file.close()
        except Exception as e:
            print ">>> At save", threadName, "Error:", e
        #Spider.lock.release()

    @staticmethod
    def addLinksToQueue(links, name, pageUrl, threadName):
        try:
            #print Spider.queueDict, Spider.queueDict[name]
            for url in links:
                if (url in Spider.queueDict[name]) or (url in Spider.crawledDict[name]):
                    continue
                if get_domain_name(url) not in Spider.starters["domainNames"]:
                    continue
                Spider.queueDict[name].add(url)
        except Exception as e:
            print ">>> At addLinks", threadName, "Error:", e
        try:
            if pageUrl not in Spider.starters["baseUrls"]:
                Spider.queueDict[name].remove(pageUrl)
        except Exception as e:
            print "-<->-<-> At rmLink", threadName, "Error:", e
        try:
            if pageUrl not in Spider.starters["baseUrls"]:
                Spider.crawledDict[name].add(pageUrl)
        except Exception as e:
            print "-<->-<-> At addLink", threadName, "Error:", e
        try:
            Spider.updateFiles(name)
        except Exception as e:
            print "-<->-<-> At update", threadName, "Error:", e

    @staticmethod
    def updateFiles(name):
        set_to_file(Spider.queueDict[name], name+"/"+Spider.queueFile)
        set_to_file(Spider.crawledDict[name], name+"/"+Spider.crawledFile)
