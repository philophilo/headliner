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
    queue = os.path.join(project_name, 'workingQueue.txt')
    crawled = os.path.join(project_name, "workingCrawled.txt")
    if not os.path.isfile(queue):
        write_file(queue, base_url+'\n')
    else:
        append_to_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')


# Create a new file
def write_file(path, data):
    print("writing file...")
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
    with open(file_name, "w") as f:
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
