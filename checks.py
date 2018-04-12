import re
import datefinder
import datetime
from bs4 import BeautifulSoup
from dateutil import parser


# get the author of the article for genralized articles
def checkAurthor(passedSoup):
    # searching for the aurthor by class
    aurthor = passedSoup.find_all(class_=re.compile("author"))
    aurthor = re.sub('(\t|\n|\[|\])', '', str(
        BeautifulSoup(str(aurthor)).get_text().encode('utf-8')))
    # assuming that level we have stripped enough to remain with a string
    if re.sub('[\s.*]', '', aurthor).isalpha():
        return aurthor


# verfiy publication based on the site parameters
def verifyPublicationDate(passedSoup, tag=None, classing=None, meta=None):
    d = None
    try:
        # testing the tag
        if (classing is None) and (meta is None):
            d = parser.parse(passedSoup.find("time").string, fuzzy=True)
            return d
        elif meta is None:
            try:
                # testing the class without inner tags
                d = parser.parse(passedSoup.find(
                    class_=classing).string, fuzzy=True)
                return d
            except Exception as e:
                try:
                    # testing the class with inner tags
                    if passedSoup.find(class_=classing):
                        d = parser.parse(passedSoup.find(
                            class_=classing).get_text(), fuzzy=True)
                        return d

                except Exception as e:
                    print(e)
                    pass
        else:
            try:
                # testing the mata tag
                d = parser.parse(passedSoup.find(
                    "meta", property=meta)["content"], fuzzy=True)
                return d
            except Exception as e:
                try:
                    d = parser.parse(passedSoup.find(
                        attrs={"itemprop": meta})["content"], fuzzy=True)
                    return d
                except Exception as e:
                    print(e)
                    pass
        return False
    except Exception as e:
        print(e)
        return False


# verify the language of the article
def verifyLanguage(passedSoup, tag=None, classing=None, meta=None):
    try:
        # testing the tag
        if (classing is None) and (meta is None) and (tag is None):
            return True
        elif (classing is None) and (meta is None):
            d = passedSoup.find('html').attrs['lang']
            return d.startswith("en")
        elif meta is None:
            try:
                # testing the class without inner tags
                d = passedSoup.find(class_=classing).string
                return d.startswith("en")
            except Exception as e:
                try:
                    # testing the class with inner tags
                    d = passedSoup.find(class_=classing).get_text()
                    return d.startswith("en")
                except Exception as e:
                    print(e)
                    pass
        else:
            try:
                # testing the mata tag
                d = passedSoup.find("meta", property=meta)["content"]
                return d.startswith("en")
            except Exception as e:
                print(e)
                pass
        return False
    except Exception as e:
        print(e)
        return False


# verify that the Article has Content
def verifyArticleContent(passedSoup, classing):
    if passedSoup.find(class_=classing):
        return True
    else:
        return False


# get articleText
def getArticleText(passedSoup, classing, locDict=None):
    if locDict is None:
        return removeOtherTags(removeFromArticleText(
            passedSoup.find(
                class_=classing).get_text()))+[checkTitle(passedSoup)]
    else:
        return removeOtherTags(
            removeFromArticleText(passedSoup.find(
                class_=classing), locDict))+[checkTitle(passedSoup)]


# remove known unncessary content
def removeFromArticleText(passedSoup, locDict):
    def removeClass(passedSoup, locDict):
        for key, value in locDict.iteritems():
            if key == "class":
                for classing in value:
                    for value in passedSoup.find_all(class_=classing):
                        value.decompose()
        return passedSoup

    def removeTag(passedSoup, locDict):
        for key, value in locDict.iteritems():
            if key == "tag":
                for tag in value:
                    for value in passedSoup.find_all(tag):
                        value.decompose()
        if passedSoup is not None:
            return passedSoup.get_text()
        else:
            return

    return removeTag(removeClass(passedSoup, locDict), locDict)


# remove other tags that may exist
def removeOtherTags(text):
    clean = re.compile('<.*?>')
    newText = re.sub(clean, '', text)
    return [newText, len(newText)]


# get the article date for genelaized articles
def getNewsDate(passedSoup):
    publicationDateString = publicationDate = re.sub(
        '(\t|\n|\[|\])', '', str(BeautifulSoup(str(
            checkDateValues(passedSoup))).get_text().encode('utf-8')))
    publicationDate = datefinder.find_dates(str(
        publicationDate.encode('utf-8')))
    for dates in publicationDate:
        if dates is not None:
            extractedDate = re.sub(
                '[\s|\t|\r|\n|\-|:|\/]', ',', str(dates)).split(",")
        extractedDate = [int(i) for i in extractedDate]
        try:
            datetime.datetime(*extractedDate)
            return publicationDateString
        except Exception as e:
            print(e)
            return False


# check date values from assumed methods
def checkDateValues(passedSoup):
    dateValue = checkDate(passedSoup)
    if dateValue is not None:
        return dateValue
    else:
        return checkTime(passedSoup)


# check for websites that have dates in fields labeled with "time"
def checkTime(passedSoup):
    publicationTime = passedSoup.find(class_=re.compile("time"))
    return publicationTime


# check for websites that have dates in fields labeled with "date"
def checkDate(passedSoup):
    publicationDate = passedSoup.find(class_=re.compile("date"))
    return publicationDate


# check for the title of the webpage
def checkTitle(passedSoup):
    try:
        title = passedSoup.find("title").get_text()
    except Exception as e:
        print("title not found!")
    return title

# TODO check for favicon
# TODO check for featured image
# TODO check for title [class or meta-data]
