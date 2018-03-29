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

    def load_from_disk(self, index_dir):
        self.invertedIndex = shelve.open(os.path.join(index_dir, "invertedIndex"))
        self.forwardIndex = shelve.open(os.path.join(index_dir, "forwardIndex"))
        self.urlToId = shelve.open(os.path.join(index_dir, "urlToId"))
        self.idToUrl = {v:k for k, v in self.urlToId.items()}
        #check where the value is used
        self._doc_count = 0
        print "LOADED!"

    def sync(self):
        self.invertedIndex.sync()
        self.forwardIndex.sync()
        self.urlToId.sync()

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
        if url not in self.urlToId:
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
                self.invertedIndex[stem].append(workaround.InvertedIndexHit(currentId, position, doc.score))
            return True
        return False

    def get_documents(self, query_term):
        return self.invertedIndex.get(query_term.stem.encode('utf-8'), [])

    def get_document_text(self, doc_id):
        return self.forwardIndex[str(doc_id)].parsed_text

    def get_url(self, doc_id):
        return self.idToUrl[doc_id]

    def get_title(self, doc_id):
        return self.forwardIndex[str(doc_id)].title

class SerpPagination(object):
    def __init__(self, page, page_size, total_doc_num):
        self.page = page
        self.page_size = page_size
        self.pages = (total_doc_num / page_size) if total_doc_num % page_size== 0 else (total_doc_num / page_size) + 1

    def iter_pages(self):
        if self.pages == 1:
            return [1]
        if self.page <= 6:
            left_part = range(1, self.page)
        else:
            left_part = [1, None] + range(self.page - 4, self.page)
        right_part = range(self.page, min(self.pages + 1, self.page + 5))
        result = left_part + right_part
        if result[-1] != self.page:
            result.append(None)

        return result

class SearchResults(object):
    def __init__(self, docs_with_relevance):
        self.docids, self.relevances = zip(*docs_with_relevance) if docs_with_relevance else ([], [])

    def get_page(self, page, page_size):
        start_num = (page-1)*page_size
        return self.docids[start_num:start_num+page_size]

    def get_pagination(self, page, page_size):
        return SerpPagination(page, page_size, len(self.docids))

    def total_doc_num(self):
        return len(self.docids)

class Searcher(object):
    def __init__(self, index_dir, IndexesImplementation):
        self.indexes = IndexesImplementation()
        self.indexes.load_from_disk(index_dir)

    def generate_snippet(self, query_terms, doc_id):
        query_terms_in_window = []
        best_window_len = 100500
        terms_in_best_window = 0
        best_window = []
        for pos, term in enumerate(self.indexes.get_document_text(doc_id)):
            if term in query_terms:
                query_terms_in_window.append((term, pos))
                if len(query_terms_in_window) > 1 and query_terms_in_window[0][0] == term:
                    query_terms_in_window.pop(0)
                current_window_len = pos - query_terms_in_window[0][1] + 1
                tiw = len(set(map(lambda x: x[0], query_terms_in_window)))
                if tiw > terms_in_best_window or (tiw == terms_in_best_window and current_window_len < best_window_len):
                    terms_in_best_window = tiw
                    best_window = query_terms_in_window[:]
                    best_window_len = current_window_len
        doc_len = len(self.indexes.get_document_text(doc_id))
        snippet_start = max(best_window[0][1] - 8, 0)
        snippet_end = min(doc_len, best_window[len(best_window) - 1][1] + 1 + 8)

        snippet = [(term.fullWord, term in query_terms) for term in self.indexes.get_document_text(doc_id)[snippet_start:snippet_end]]

        if len(snippet) > 50:
            excessive_len = len(snippet) - 50
            snippet = snippet[:len(snippet)/2 - excessive_len/2] + [("...", False)] + snippet[len(snippet)/2 + excessive_len/2:]
        return snippet


    def find_documents_and_rank_by_points(self, query_terms):
        docids_and_relevance = set()
        for query_term in query_terms:
            for hit in self.indexes.get_documents(query_term):
                docids_and_relevance.add((hit.docid, hit.score))

        return SearchResults(sorted(list(docids_and_relevance), key=lambda x: x[1], reverse=True))

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
        #print key
        return key
    def verifyDocument(self, threadName, index, openFile):
        def createNone(x):
            if x is '':
                x = None
                return x
            return x

        # document format tags
        tag = createNone(Preper.busket['articleDate'][index]['tag'])
        classing = createNone(Preper.busket["articleDate"][index]['class'])
        meta = createNone(Preper.busket["articleDate"][index]['meta'])
        # document language tags
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
            # number of days should be not more than a week
            if days:
                return getArticleText(soup, classingText, Preper.busket["articleAvoid"][index])+[verifiedDate]
        return [None, None, None, None]

def createIndexFromDir(indexesImplementation=ShelveIndexes):
    contents = readSourceFile()
    baseUrls, articleTitle, articleDate, articleBody, lang, avoid = zip(*[(v['link']['siteUrl'], v['title'], v['date'], v['articleBody'], v['language'], v['avoid']) for k, v in contents.iteritems()])
    projectNames = contents.keys()
    prep = Preper(projectNames, list(baseUrls), list(articleTitle), list(articleDate), list(articleBody), list(lang), list(avoid))
    save = False
    syncState = False
    startPrname = projectNames[0]
    for prname in projectNames:
        indexer = indexesImplementation()
        print ">>>", prname
        indexedDocNum = 1
        indexer.startIndexing(prname)
        for filename in os.listdir(prname+"/htmlFiles"):
            openedFile = open(os.path.join(prname+"/htmlFiles/"+filename))
            print "--", indexedDocNum, "--", filename
            plainText, tmpScore, title = prep.parseDocument("main", prname, openedFile)
            #print plainText, tmpScore, title
            if syncState:
                print indexedDocNum, "Syncing..."
                indexer.sync()
                print indexedDocNum, "synced!"
            if plainText is not None:
                indexedDocNum += 1
                plainText = toDocTerms(plainText)
                save = indexer.addDocument("main", prname, base64.b16decode(filename), workaround.Document(plainText, tmpScore, title))
        if save:
            print "+++", "saving..."
            indexer.saveOnDisk(prname)
            if indexedDocNum % 100 == 0:
                syncState = True
            save, syncState = False, False
        startPrname = prname


def main():
    #threading can be implemented here
    createIndexFromDir()

if __name__ == "__main__":
    main()
