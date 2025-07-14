from langchain.agents import create_pandas_dataframe_agent
from langchain.llms import OpenAI
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.agents import initialize_agent
import pandas as pd

class LangChainProcessor:
    def __init__(self, api_key):
        self.llm = OpenAI(openai_api_key=api_key, temperature=0.1)
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        
    def create_dataframe_agent(self, dataframe):
        """Create a smart pandas agent that can analyze data"""
        return create_pandas_dataframe_agent(
            self.llm,
            dataframe,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            handle_parsing_errors=True
        )
    
    def process_query(self, query, dataframe):
        """Process user query with intelligent agent"""
        agent = self.create_dataframe_agent(dataframe)
        
        try:
            # Agent automatically decides how to handle the query
            result = agent.run(query)
            return {"type": "success", "content": result}
        except Exception as e:
            return {"type": "error", "content": str(e)}
