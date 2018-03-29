import os
import yaml

# Each website is a separate project (folder)
# creating site dir and sub dirs for indexes and downloaded html
def create_storage_dir(directory):
    if not os.path.exists(directory):
        print('Creating directory ' + directory)
        os.makedirs(directory)


# Create queue and crawled files (if not created)
# TODO rename to create_site_link_files
def create_data_files(project_name, base_url):
    queue = os.path.join(project_name , 'workingQueue.txt')
    crawled = os.path.join(project_name,"workingCrawled.txt")
    if not os.path.isfile(queue):
        write_file(queue, base_url+'\n')
    else:
        append_to_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')

# Create a new file
def write_file(path, data):
    print "writing file..."
    with open(path, 'w') as f:
        f.write(data)


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    open(path, 'w').close()


# Read a file and convert each line to set items
def file_to_set(file_name):
    results = set()
    try:
        with open(file_name, 'rt') as f:
            for line in f:
                results.add(line.replace('\n', ''))
        return results
    except Exception as e:
        pass


# Iterate through a set, each item will be a line in a file
def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in sorted(links):
            f.write(l+"\n")

# create html directory
def save_html_file(directory):
    if not os.path.exists(directory):
        print('Creating html directory ' + directory)
        os.makedirs(directory)


# get dictionary from the source file
def readSourceFile():
    dst = yaml.safe_load(open("source"))
    return dst
"""
#import shutil
#from tempfile import NamedTemporaryFile
#import csv
#import ast

# create source file
def writeToSourceFile(name, link, title, date, author, articleSummary, articleBody, avoid, pageType, featuredImage):
    with open('source.csv', 'w') as source:
        fieldNames = ["name", "link", "title", "date", "author", "articleSummary", "articleBody", "avoid", "pageType", "featuredImage"]
        writer = csv.DictWriter(source, fieldnames=fieldNames)
        writer.writeheader()
        writer.writerow({"name":name, "link":link, "title":title, "date":date, "author":author, "articleSummary":articleSummary, "articleBody":articleBody, "avoid":avoid, "pageType":pageType, "featuredImage":featuredImage})


# append to the source file
def appendToSourceFile(name, link, title, date, author, articleSummary, articleBody, avoid, pageType, featuredImage):
    fieldNames = ["name", "link", "title", "date", "author", "articleSummary", "articleBody", "avoid", "pageType", "featuredImage"]
    with open(r'source.csv', 'a') as source:
        writer = csv.DictWriter(source, fieldnames=fieldNames)
        writer.writerow({"name":name, "link":link, "title":title, "date":date, "author":author, "articleSummary":articleSummary, "articleBody":articleBody, "avoid":avoid, "pageType":pageType, "featuredImage":featuredImage})

# append to ordered dictionary to source file
def appendOrderedDictSourceFile(dataDict):
    with open("source.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerows(zip(*dataDict.values()))

# read the full source file
def readFullSourceFile():
    results = {}
    with open("source.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for column, value in row.iteritems():
                results.setdefault(column, []).append(ast.literal_eval(value))
    return results

#read the full source file as a dictionary
def readFullSourceFileDictionary():
    results = {}
    with open("source.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for column, value in row.iteritems():
                results.setdefault(column, []).append(ast.literal_eval(value))
    return results

# lookup in the source file
def readSourceRowByMatch(column, key, fieldValue):
    fieldNames = ["name", "link", "title", "date", "author", "articleSummary", "articleBody", "avoid", "pageType", "featuredImage"]
    with open('source.csv', 'rb') as f:
        reader = csv.DictReader(f, fieldnames=fieldNames)
        x = 0
        for row in reader:
            if x > 0:
                if ast.literal_eval(row[column])[key] == fieldValue:
                    return row
            x+=1


# update by column in source file -- requires tesing first
def updateColumnSourceFile(fieldName, fieldValue, fieldNewValue):
    fileName = 'source.csv'
    tempFile = NamedTemporaryFile(delete = False)
    with open(fileName, 'rb') as f, tempFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')
        writer = csv.writer(tempFile, delimiter=',', quotechar='"')
        for row in reader:
            if fieldValue == row[fieldName]:
                row[fieldName] = fieldNewValue
                writer.writerow(row)
    shutil.move(tempFile.name, fileName)

# delete row from the csv file
def deleteRowFromSourceFile(fieldName, fieldValue):
    fieldNames = ["name", "link", "date", "author"]
    with open("source.csv", "rt") as infile, open("output.csv", "wt") as outfile:
        reader = csv.DictReader(infile, fieldnames = fieldNames)
        writer = csv.DictWriter(outfile, fieldnames = fieldNames)
        for row in reader:
            if fieldValue != row[fieldName]:
                writer.writerow({"name":row["name"], "link":row["link"], "date":row["date"], "author":row["author"]})
    shutil.move('output.csv', 'source.csv')

"""
