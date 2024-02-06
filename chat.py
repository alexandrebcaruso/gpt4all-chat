import os
import sys

from langchain_community.llms import GPT4All
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import MarkdownHeaderTextSplitter

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=HuggingFaceEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = UnstructuredMarkdownLoader("context.md")
  headers_to_split_on = [
    ("#", "# Informações gerais"),
    ("#", "# Lista de imóveis à venda"),
    ("##", "## Propriedade"),
  ]
  # loader = TextLoader("context.json")
  # loader = DirectoryLoader("context/", glob='**/*.json', show_progress=True, loader_cls=TextLoader)

  docs = loader.load()
  txt = ' '.join([d.page_content for d in docs])

  markdown_splitter = MarkdownHeaderTextSplitter(
      headers_to_split_on=headers_to_split_on
  )
  md_header_splits = markdown_splitter.split_text(txt)

  if PERSIST:
    index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings(), vectorstore_kwargs={"persist_directory":"persist"}).from_documents([docs])
  else:
    index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings()).from_documents([docs])

chain = ConversationalRetrievalChain.from_llm(
  llm=GPT4All(model='mistral-7b-openorca.Q4_0.gguf', device='gpu'),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}))

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None
