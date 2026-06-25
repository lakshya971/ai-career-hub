from langchain_community.vectorstores import FAISS

def create_vector_store(chunks, embedding_model):
    vector_store = FAISS.from_documents(chunks, embedding_model)
    vector_store.save_local("vector_store")
    return vector_store
