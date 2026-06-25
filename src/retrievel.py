def retrieve_documents(query, vector_store, k=5):

   retriever =  vector_store.as_retriever(search_type = "similarity", search_kwargs = {"k": 5})

   docs = retriever.invoke(query)
   return docs