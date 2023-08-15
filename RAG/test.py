'''from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import ElasticVectorSearch

import tiktoken  # !pip install tiktoken

tokenizer = tiktoken.get_encoding('p50k_base')


# create the length function


print(tiktoken_len("hello I am a chunk of text and using the tiktoken_len function "
             "we can find the length of this chunk of text in tokens"))'''

import fitz
from unidecode import unidecode
doc=fitz.open("Data/AMZN 20210510A.pdf")
print(doc)
for pnum, page in enumerate(doc):
    if pnum > 0:
        break
    append_block = ""
    for block in page.get_text("dict")["blocks"]:
        if block["type"] == 0:
            if append_block != "":
                block_string = append_block
                append_block = ""
            else:
                block_string = ""
            for l in block["lines"]:
                for s in l["spans"]:
                    if len(block["lines"]) == 1 and len(l["spans"]) == 1 and not s["text"].isascii():
                        append_block += unidecode(s["text"])
                    else:
                        block_string += s["text"]
        if block_string.strip():
            print(block_string)  
        print("******************")
