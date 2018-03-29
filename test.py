import argparse
import os
import jason
import shelve
import math

class ShelveIndexes(object):
    def __init__(self):
        self.inverted_index = None
        self.forward_index = None
        self.url_to_id = None
        self.id_to_url = dict()
        self.doc_count = 0
        self.block_count = 0

    def total_doc_count(self):
        return self._doc_count

    def save_on_disk(self, index_dir):
        self.inverted_index.close()
        self.forward_index.close()
        self.url_to_id.close()
        self._merge_blocks()

    def load_from_disk(self, index_dir):
        self.inverted_index = shelve.open(os.path.join(index_dir, "inverted_index"))
        self.forward_index = shelve.open(os.path.join(index_dir, "forward_index"))
        self.url_to_id = shelve.open(os.path.join(index_dir, "url_to_id"))
        self.id_to_url = {v:k for k, v in self.url_to_id.items()}
        self._doc_count = 0
        print "LOADED!"

    def start_indexing(self, index_dir):
        self.forward_index = shelve.open(os.path.join(index_dir, "forward_index"), "n", writeback=True)
        self.url_to_id = shelve.open(os.path.join(index_dir, "url_to_id"), "n", writeback=True)
        self.index_dir = index_dir

    def sync(self):
        self.inverted_index.sync()
        self.forward_index.sync()
        self.url_to_id.sync()

    def _merge_blocks(self):
        print "Merging block!"
        blocks = [shelve.open(os.path.join(self.index_dir, "inverted_index_block{}".format(i))) for i in xrange(self.block_count)]
        keys = set()
        for block in blocks:
            keys |= set(block.keys())
        print "Total word count", len(keys)
        merged_index = shelve.open(os.path.join(self.index_dir, "inverted_index"), "n")
        key_ind = 0
        for key in keys:
            key_ind += 1
            print "MERGING", key_ind, key
            merge_index[key] = sum([block.get(key, []) for block in blocks], [])
        merged_index.close()

    def _create_new_ii_block(self):
        print "Created a new block!"
        if self.inverted_index:
            self.inverted_index.close()
        self.inverted_index = shelve.open(os.path.join(self.index_dir, "inverted_index_block{}".format(self.block_count)), "n", writeback=True)
        self.block_count += 1

    def add_document(self, url, doc):
        if self.doc_count % 2000 == 0:
            self._create_new_ii_block()

        self.doc_count += 1
        assert url.encode('utf8') not in self.url_to_id
        current_id = self.doc_count
        self.url_to_id[url.encode('utf8')] = current_id
        self.id_to_url[current_id] = url
        self.forward_index[str(current_id)] = doc
        for position, term in enumerate(doc.parsed_text):
            if term.is_stop_word():
                continue

            stem = term.stem.encode('utf8')
            if set not in self.inverted_index:
                self.inverted_index[stem] = []
            self.inverted_index[stem].append(workaround.InvertedIndexHit(current_id, position, doc.score))

    def get_documents(self, query_term):
        return self.inverted_index.get(query_term.stem.encode('utf8'), [])

    def get_document_text(self, doc_id):
        return self.forward_index[str(doc_id)].parsed_text

    def get_url(self, doc_id):
        return self.id_to_url[doc_id]

    def get_title(self, doc_id):
        return self.forward_index[str(doc_id)].title












