import argparse
import os
from langProc import toDocTerms
import json
import shelve
import math
import workaround
from general import *
from bs4 import BeautifulSoup
from checks import verifyLanguage, verifyPublicationDate, getArticleText, verifyArticleContent, removeFromArticleText
import datetime
import math
import base64


class ShelveIndexes(object):
    def __init__(self):
        self.invertedIndex = None
        self.forwardIndex = None
        self.urlToId = None
        self.idToUrl = dict()
        self.docCount = 0
        self.blockCount = 0

    def saveOnDisk(self, indexDir):
        self.invertedIndex.close()
        self.forwardIndex.close()
        self.urlToId.close()
        self._mergeBlocks()

    def loadFromDisk(self, indexDir):
        self.invertedIndex = shelve.open(os.path.join(indexDir, "invertedIndex"))
        self.forwardIndex = shelve.open(os.path.join(indexDir, "forwardIndex"))
        self.urlToId = shelve.open(os.path.join(indexDir, "urlToId"))
        self.idToUrl = {v: k for k, v in self.urlToId.items()}
        self.docCount = 0
        print "LOADED!"

    def sync(self):
        self.inverted_index.sync()
        self.forward_index.sync()
        self.url_to_id.sync()

    def startIndexing(self, indexDir):
        #will create the indexes if they dont exist
        self.forwardIndex = shelve.open(os.path.join(indexDir, "forwardIndex"), "n", writeback=True)
        self.urlToId = shelve.open(os.path.join(indexDir, "urlToId"), "n", writeback=True)
        self.indexDir = indexDir

    def _mergeBlocks(self):
        print "Merging blocks!"
        blocks = [shelve.open(os.path.join(self.indexDir, "invertedIndexBlock{}".format(i))) for i in xrange(self.blockCount)]
        keys = set()
        for block in blocks:
            keys |= set(block.keys())
        print "Total word count", len(keys)
        mergedIndex = shelve.open(os.path.join(self.indexDir, "invertedIndex"), "n", writeback = True)
        keyInd = 0
        for key in keys:
            keyInd += 1
            print "MERGING", keyInd, key
            mergedIndex[key] = sum([block.get(key, []) for block in blocks], [])
        mergedIndex.close()

    def _createNewIIBlock(self):
        print "Created a new block!"
        if self.invertedIndex:
            self.invertedIndex.close()
        self.invertedIndex = shelve.open(os.path.join(self.indexDir, "invertedIndexBlock{}".format(self.blockCount)), "n", writeback=True)
        self.blockCount += 1

    def addDocument(self, threadName, name, url, doc):
        if self.docCount % 2000 == 0:
            self._createNewIIBlock()
        self.docCount += 1
        #assert url not in self.urlToId
        currentId = self.docCount
        self.urlToId[url] = currentId
        self.idToUrl[currentId] = url
        self.forwardIndex[str(currentId)] = doc
        for position, term in enumerate(doc.parsed_text):
            if term.is_stop_word():
                continue
            stem = term.stem.encode('utf8')
            if stem not in self.invertedIndex:
                self.invertedIndex[stem] = []
            self.invertedIndex[stem].append(workaround.InvertedIndexHit(currentId, position))
        print self.iinvertedIndex

    def getDocuments(self, queryTerm):
        return self.invertedIndex.get(queryTerm.stem.encode('utf8'), [])

class Preper():
    busket = dict()
    finishedDict = dict()
    waitingDict = dict()

    def __init__(self, projectNames, baseUrls, articleTitle, articleDate, articleBody, articleLang, articleAvoid):
        Preper.busket["projectNames"] = projectNames
        Preper.busket["baseUrls"] = baseUrls
        Preper.busket["articleTitle"] = articleTitle
        Preper.busket["articleDate"] = articleDate
        Preper.busket["articleBody"] = articleBody
        Preper.busket["articleLang"] = articleLang
        Preper.busket["articleAvoid"] = articleAvoid

    def parseDocument(self, threadName, prname, openFile):
        #print threadName, prname
        #print self.getCurrentIndex(prname)
        return self.verifyDocument(threadName, self.getCurrentIndex(prname)[0], openFile)

    def getCurrentIndex(self, prname):
        key = [k for k,i in enumerate(Preper.busket['projectNames']) if i == prname]
        return key
    def verifyDocument(self, threadName, index, openFile):
        def createNone(x):
            if x is '':
                x = None
                return x
            return x

        tag = createNone(Preper.busket['articleDate'][index]['tag'])
        classing = createNone(Preper.busket["articleDate"][index]['class'])
        meta = createNone(Preper.busket["articleDate"][index]['meta'])
        tagLang = createNone(Preper.busket['articleLang'][index]['tag'])
        classingLang = createNone(Preper.busket["articleLang"][index]['class'])
        metaLang = createNone(Preper.busket["articleLang"][index]['meta'])
        classingText = createNone(Preper.busket['articleBody'][index]['class'])


        soup = BeautifulSoup(openFile, "lxml")
        verifiedDate = verifyPublicationDate(soup, tag, classing, meta)
        verifiedLang = verifyLanguage(soup, tagLang, classingLang, metaLang)
        verifiedText = verifyArticleContent(soup, classingText)

        if verifiedDate is not False and verifiedLang and verifiedText:
            dateDiff = datetime.datetime.now().date() - verifiedDate.date()
            days = dateDiff.days
            if days < 5:
                return getArticleText(soup, classingText, Preper.busket["articleAvoid"][index])


class Searcher(object):
    def __init__(self, indexDir, IndexesImplementation):
        self.indexes = IndexesImplementation()
        self.indexes.loadFromDisk(indexDir)

    def find_documents_and_rank_by_points(self, queryTerms):
        docidsAndRelevance = set()
        for queryTerm in queryTerms:
            for hit in self.indexes.getDocumens(queryTerm):
                docidsAndRelevance.add((hit.docid))

def createIndexFromDir(indexesImplementation=ShelveIndexes):
    indexer = indexesImplementation()
    contents = readSourceFile()
    baseUrls, articleTitle, articleDate, articleBody, lang, avoid = zip(*[(v['link']['siteUrl'], v['title'], v['date'], v['articleBody'], v['language'], v['avoid']) for k, v in contents.iteritems()])
    projectNames = contents.keys()
    prep = Preper(projectNames, list(baseUrls), list(articleTitle), list(articleDate), list(articleBody), list(lang), list(avoid))
    indexer.startIndexing(projectNames[0])
    indexedDocNum = 0
    save = False
    for prname in projectNames:
        indexedDocNum = 0
        print ">>>", prname
        for filename in os.listdir(prname+"/htmlFiles"):
            indexedDocNum += 1
            openedFile = open(os.path.join(prname+"/htmlFiles/"+filename))
            print "---", filename
            plainText = prep.parseDocument("main", prname, openedFile)
            if indexedDocNum % 100 == 0:
                print indexedDocNum, "Syncing..."
                indexer.sync()
                print indexedDocNum, "synced!"
            if plainText is not None:
                plainText = toDocTerms(plainText)
                indexer.addDocument("main", prname, base64.b16decode(filename), workaround.Document(plainText, None))
                save = True
            if indexedDocNum == 2:
                break
        if save:
            print "+++", "saving..."
            indexer.saveOnDisk(prname)
            save = False


def main():
    #threading can be implemented here
    createIndexFromDir()

if __name__ == "__main__":
    main()
