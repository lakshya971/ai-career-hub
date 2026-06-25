from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_chunk(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, # semantic chunk strategy
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

