from haystack.document_stores import FAISSDocumentStore
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
from haystack.nodes import PreProcessor
from pathlib import Path
from bs4 import BeautifulSoup
import unicodedata
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import FARMReader

from haystack.pipelines import Pipeline

reader = FARMReader(model_name_or_path="deepset/deberta-v3-large-squad2", use_gpu=True)


# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

def contains_nouns_and_verbs(text):
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    for sentence in sentences:
        # Tokenize the sentence into words
        words = word_tokenize(sentence)

        # Get part-of-speech tags for the words
        pos_tags = pos_tag(words)

        has_noun = False
        has_verb = False

        # Check for nouns and verbs in the POS tags
        for word, tag in pos_tags:
            if tag.startswith('NN'):  # Nouns (NN, NNS, NNP, NNPS)
                has_noun = True
            if tag.startswith('VB'):  # Verbs (VB, VBD, VBG, VBN, VBP, VBZ)
                has_verb = True

        # If the sentence contains both a noun and a verb, return True
        if has_noun and has_verb:
            return True

    # If no sentence contains both a noun and a verb, return False
    return False

def filter_docs_with_nouns_and_verbs(all_docs):
    # Filter the documents using the contains_nouns_and_verbs function
    return [doc for doc in all_docs if contains_nouns_and_verbs(doc['content'])]

document_store = FAISSDocumentStore()

doc_dir = "content/"

# create a list of dictionaries from the HTML files in the input directory
all_docs = []
file_paths = [p for p in Path(doc_dir).glob("**/*")]
for path in file_paths:
      with open(path, 'r', encoding='utf-8') as f:
          html_content = f.read()
          soup = BeautifulSoup(html_content, 'html.parser')
          page_text = soup.get_text()
          text_content = unicodedata.normalize('NFKD', page_text)
          all_docs.append({
            'content': text_content,
            'meta': {'name': path.name}
          })


preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=False,
    split_by="word",
    split_length=100,
    split_overlap=0,
    split_respect_sentence_boundary=True,
)

docs = filter_docs_with_nouns_and_verbs(all_docs)
docs = preprocessor.process(docs)

print(f"n_files_input: {len(all_docs)}\nn_docs_output: {len(docs)}")

document_store.delete_documents()
document_store.write_documents(docs)

retriever = EmbeddingRetriever(
    document_store=document_store,
    embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1",
)

pipe = Pipeline()
pipe.add_node(component=retriever, name="Retriever", inputs=["Query"])
pipe.add_node(component=reader, name="Reader", inputs=["Retriever"])



def reply(query):
    prediction = pipe.run(
        query=query,
        params={
            "Retriever": {"top_k": 5},
            "Reader": {"top_k": 1}
        }
    )

    return prediction.answers
