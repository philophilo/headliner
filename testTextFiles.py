from testIndexer import Preper
from general import readSourceFile, create_storage_dir
import os
import json

class SaveText(object):
    def __init__(self):
        self.json_file_store = dict()

    def text_fetcher(self):
        contents = readSourceFile()
        base_urls, article_title, article_date, article_body, lang, avoid = zip(*[(v['link']['siteUrl'], v['title'], v['date'], v['articleBody'], v['language'], v['avoid']) for k, v in contents.iteritems()])
        project_names = contents.keys()
        prep = Preper(project_names, list(base_urls), list(article_title), list(article_date), list(article_body), list(lang), list(avoid))
        json_dir = project_names[0]

        for k, pr_name in enumerate(project_names):
            for f_name in os.listdir(pr_name+"/htmlFiles"):
                json_file_store = dict()
                open_file = open(os.path.join(pr_name+'/htmlFiles/'+f_name))
                plain_text, length, title, art_date = prep.parseDocument("main", pr_name, open_file)
                json_file_store['title'] = title
                json_file_store['date'] = str(art_date)
                json_file_store['length'] = length
                json_file_store['text'] = plain_text
                self.dump_json_to_file(pr_name+'/json_files/', f_name, json_file_store)
                # TODO -store
                # url to feature image location
                # url to icon
                # clean title from metadata/class
                # examine more avoids, rt-comments
            if k == 0:
                break

    def dump_json_to_file(self, json_dir, json_name, json_file):
        create_storage_dir(json_dir)
        file_path = os.path.join(json_dir, json_name)
        #TODO check the file already exists
        json.dump(json_file, open(file_path, "w"), indent=4)

    def load_json_from_file(self, index_dir, file_name):
        file_path = os.path.join(index_dir, file_name)
        out = json.load(open(file_path))
        return out

    def get_json_from_dir(self, index_dir):
        json_files = []
        for f_name in os.listdir(index_dir):
            json_files.append(self.load_json_from_file(index_dir, f_name))
        return json_files



