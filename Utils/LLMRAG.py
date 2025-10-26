from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_ollama.chat_models import ChatOllama
from ragUtils import SupabaseAPI as sb

#Might have to edit to utilize static method instead of instance method, i.e, Convert to "Conversatin" class, where you quety llm with just a user object. Would also need to create user object.

class LLMRAG:
    db: sb.SupabaseAPI
    llm: ChatOllama
    chunks: list[str]

    def __init__(self, user_id: int | None, user_embedding: list[float], match_count: int):
        self.db = sb.SupabaseAPI()
        self.__load_model()
        self.__load_user_context(user_id, user_embedding, match_count)

# =========== QUERY LLM WITH RAG ============= 
    def query_LLM(self, question: str) -> str:

        if not self.chunks:
            return "No relevant context found to answer the question."
        
        context = "\n".join([chunk['details'] for chunk in self.chunks])
        prompt = self.__create_prompt(context, question)

        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt)
        ]

        response = self.llm(messages)

        return response.content

    def query_LLM(self, question: str) -> str:
        
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=question)
        ]

        response = self.llm(messages)

        return response.content
    
# =========== Helper METHODS =============
    def __load_user_context(self, user_id: int | None, user_embedding: list[float], match_count: int) -> None:

       #Change this to handle user_id being None
        if user_id is not None:
            try:
                self.chunks = self.db.rag_Search(embedding=user_embedding, match_count=match_count)
            except Exception as e:
                print(f"Error during RAG search: {e}")

        else:
            try:
                self.chunks = self.db.rag_Search(embedding=user_embedding, match_count=match_count)
            except Exception as e:
                print(f"Error during RAG search: {e}")
    
    def __load_model(self) -> None:
        try:
            self.llm = ChatOllama(model="llama2", temperature=0.7)
        except Exception as e:
            print(f"Error loading LLM: {e}")
            exit(1)

    def __create_prompt(self, context: str, question: str) -> str:

        prompt_template = PromptTemplate(

            input_variables=["context", "question"],
            template="You are an expert assistant matching the user to professors they can do research with. Use the following context to answer the question\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"

        )

        return prompt_template.format(context=context, question=question)