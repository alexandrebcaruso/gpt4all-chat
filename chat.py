import os
import sys

from langchain_community.llms import GPT4All
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import Chroma

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = True

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=HuggingFaceEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("data/", glob='**/*.json', show_progress=True, loader_cls=TextLoader)
  if PERSIST:
    index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings(), vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator(embedding=HuggingFaceEmbeddings()).from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=GPT4All(model='orca-mini-3b-gguf2-q4_0.gguf', device='gpu'),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 10}),
)

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