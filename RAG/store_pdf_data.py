import fitz
import operator
import utils
import tiktoken  # !pip install tiktoken
from tqdm.auto import tqdm
from uuid import uuid4
from elasticsearch import Elasticsearch, helpers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings



tokenizer = tiktoken.get_encoding('p50k_base')

class StorePDFData():
    def __init__(self, path):
        self.path = path
        self.es = Elasticsearch('http://localhost:9200')


    
    def fonts(self, doc, granularity=False):
        """Extracts fonts and their usage in PDF documents.
        :param doc: PDF document to iterate through
        :type doc: <class 'fitz.fitz.Document'>
        :param granularity: also use 'font', 'flags' and 'color' to discriminate text
        :type granularity: bool
        :rtype: [(font_size, count), (font_size, count}], dict
        :return: most used fonts sorted by count, font style information
        """
        styles = {}
        font_counts = {}

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b['type'] == 0:  # block contains text
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if granularity:
                                identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                                styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                    'color': s['color']}
                            else:
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {'size': s['size'], 'font': s['font']}

                            font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

        font_counts = sorted(font_counts.items(), key=operator.itemgetter(1), reverse=True)

        if len(font_counts) < 1:
            raise ValueError("Zero discriminating fonts found!")

        return font_counts, styles

    def font_tags(self, font_counts, styles):
        """Returns dictionary with font sizes as keys and tags as value.
        :param font_counts: (font_size, count) for all fonts occuring in document
        :type font_counts: list
        :param styles: all styles found in the document
        :type styles: dict
        :rtype: dict
        :return: all element tags based on font-sizes
        """
        p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
        p_size = p_style['size']  # get the paragraph's size

        # sorting the font sizes high to low, so that we can append the right integer to each tag 
        font_sizes = []
        for (font_size, count) in font_counts:
            font_sizes.append(float(font_size))
        font_sizes.sort(reverse=True)
        # aggregating the tags for each font size
        idx = 0
        size_tag = {}
        for size in font_sizes:
            idx += 1
            if size <= p_size:
                idx = 0
                size_tag[size] = "para"
            if size > p_size:
                if idx > 2:
                    size_tag[size] = "para"
                else:
                    size_tag[size] = "heading"
            '''elif size < p_size:
                size_tag[size] = '<s{0}>'.format(idx)'''

        return size_tag
    
    def headers_para(self, doc, size_tag):
        """Scrapes headers & paragraphs from PDF and return texts with element tags.
        :param doc: PDF document to iterate through
        :type doc: <class 'fitz.fitz.Document'>
        :param size_tag: textual element tags for each size
        :type size_tag: dict
        :rtype: list
        :return: texts with pre-prended element tags
        """
        header_para = [] # list with headers and paragraphs
        first = True  # boolean operator for first header
        previous_s = {}  # previous span

        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if "type" not in b:
                    continue
                if b['type'] == 0:  # this block contains text

                    # REMEMBER: multiple fonts and sizes are possible IN one block
                    block_string = ""  # text found in block
                    if len(b["lines"]) == 1 and len(b["lines"]["spans"]) == 1:
                        print(b["lines"]["spans"]["text"])
                    '''for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if s['text'].strip():  # removing whitespaces:
                                if first:
                                    previous_s = s
                                    first = False
                                    block_string = s['text']
                                else:
                                    if s['size'] == previous_s['size']:

                                        #if block_string and all((c.strip() == "") for c in block_string):
                                            # block_string only contains pipes
                                        #    block_string = size_tag[s['size']] + s['text']
                                        if block_string.strip() == "":
                                            # new block has started, so append size tag
                                            block_string = s['text']
                                        else:  # in the same block, so concatenate strings
                                            block_string += " " + s['text']

                                    else:
                                        if block_string.strip():
                                            header_para_dict = {}
                                            header_para_dict["page"] = page_num + 1
                                            header_para_dict["para"] = size_tag[s['size']]
                                            header_para_dict["text"] = block_string
                                            header_para.append(header_para_dict)
                                        block_string = s['text']

                                    previous_s = s
                    if block_string.strip():
                        header_para_dict = {}
                        header_para_dict["page"] = page_num + 1
                        header_para_dict['para'] = size_tag[s['size']]
                        header_para_dict['text'] = block_string
                        header_para.append(header_para_dict)
        return header_para'''
    
    def get_blocks(self, doc):
        """Scrapes paragraphs from PDF and return texts by each block.
        :param doc: PDF document to iterate through
        :type doc: <class 'fitz.fitz.Document'>
        :rtype: list
        :return: texts by block
        """
        paras = [] # list with paragraphs
        first = True  # boolean operator for first header
        
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block_num, b in enumerate(blocks):  # iterate through the text blocks
                if "type" not in b:
                    continue
                if b['type'] == 0:  # this block contains text

                    # REMEMBER: multiple fonts and sizes are possible IN one block
                    block_string = ""  # text found in block
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if s['text'].strip():  # removing whitespaces:
                                block_string += s['text']
                    para_dict = {}
                    para_dict["page"] = page_num + 1
                    para_dict["para"] = block_num + 1
                    para_dict["text"] = block_string
                    paras.append(para_dict)
        return paras
    
    def tiktoken_len(self, text):
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)


    def read_pdf(self):
        doc = fitz.open(self.path)
        font_counts, styles = self.fonts(doc)
        size_tag = self.font_tags(font_counts, styles)
        self.headers_para(doc, size_tag)
        #paras = self.headers_para(doc, size_tag)
        #paras = self.get_blocks(doc)
        #return paras
        
    def create_hf_embeddings(self, header_para):
        batch_limit = 100
        embeddings = HuggingFaceEmbeddings()
        #metas = [{"page":f['page'], "type":f["type"]} for f in header_para]
        #texts = [f['text'] for f in header_para]
        texts = []
        metadatas = []
        ids = []
        for i, record in enumerate(tqdm(header_para)):
            metadata = {
                "page": record["page"],
                "para": record["para"],
                "text": record["text"]
            }
            texts.append(record["text"])
            metadatas.append(metadata)
            #print(str(uuid4()))
            ids.append(str(uuid4()))
            if len(metadatas) >= batch_limit:
                body = []
                embeds = embeddings.embed_documents(texts)
                for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
                    entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":"amazoncom-inc-prospectus-hf", "_op_type":"index"}
                    body.append(entry)
                helpers.bulk(self.es, body)
                texts = []
                metadatas = []
                ids = []
        body = []
        embeds = embeddings.embed_documents(texts)
        for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
            entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":"amazoncom-inc-prospectus-hf", "_op_type":"index"}
            body.append(entry)
        helpers.bulk(self.es, body)
        texts = []
        metadatas = []
        ids = []

    def create_openai_embeddings(self, header_para):
        '''metas = [{"page":f['page'], "type":f["type"]} for f in header_para]
        texts = [f['text'] for f in header_para]
        embeddings = HuggingFaceEmbeddings()
        db = ElasticVectorSearch.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metas,
            elasticsearch_url="http://localhost:9200",
            index_name="amazoncom-inc-prospectus-ada".lower(),
        )
        print(db.client.info())'''
        model_name = 'text-embedding-ada-002'

        embed = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=utils.KEY
        )
        batch_limit = 100
        #metas = [{"page":f['page'], "type":f["type"]} for f in header_para]
        #texts = [f['text'] for f in header_para]
        texts = []
        metadatas = []
        ids = []
        for i, record in enumerate(tqdm(header_para)):
            metadata = {
                "page": record["page"],
                "para": record["para"],
                "text": record["text"]
            }
            texts.append(record["text"])
            metadatas.append(metadata)
            #print(str(uuid4()))
            ids.append(str(uuid4()))
            if len(metadatas) >= batch_limit:
                body = []
                embeds = embed.embed_documents(texts)
                for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
                    entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":"amazoncom-inc-prospectus-ada", "_op_type":"index"}
                    body.append(entry)
                helpers.bulk(self.es, body)
                texts = []
                metadatas = []
                ids = []
        body = []
        embeds = embed.embed_documents(texts)
        for id, embedding, metadata, text in zip(ids, embeds, metadatas, texts):
            entry = {"vector": embedding, "metadata": metadata, "text":text, "_id": id, "_index":"amazoncom-inc-prospectus-ada", "_op_type":"index"}
            body.append(entry)
        helpers.bulk(self.es, body)
        texts = []
        metadatas = []
        ids = []



if __name__=='__main__':
    s = StorePDFData('Data/AMZN 20210510A.pdf')
    s.read_pdf()
    #blocks = s.read_pdf()
    #print(len(blocks))
    #s.create_hf_embeddings(blocks)