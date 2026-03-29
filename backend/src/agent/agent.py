from langgraph.prebuilt import create_react_agent
from langchain_aws import ChatBedrock
import boto3
from langgraph.types import Command

from langgraph.checkpoint.postgres import PostgresSaver
import psycopg   

from settings import config
from tools.tools import CoffeeShopTools
from agent.prompt import get_system_prompt


def get_bedrock_client():
    return boto3.client(
        region_name=config.AWS_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        service_name="bedrock-runtime",
    )


def get_llm(max_tokens=500, temperature=0.7):
    return ChatBedrock(
        client=get_bedrock_client(),
        model_id=config.MODEL_ID,
        provider="amazon",
        model_kwargs={
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
    )


class CoffeeShopAgent:

    _checkpointer = None

    def __init__(self, service):
        self.service = service
        
        DB_HOST = config.db_host
        DB_PORT = config.db_port
        DB_NAME = config.db_name
        DB_USERNAME = config.db_username
        DB_PASSWORD = config.db_password
        
        self.db_url = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        try:
            if CoffeeShopAgent._checkpointer is None:
                print("\nInitializing PostgresSaver (DB Memory)...")
                
                conn = psycopg.connect(self.db_url)
                CoffeeShopAgent._checkpointer = PostgresSaver(conn)
                CoffeeShopAgent._checkpointer.setup()
                print("PostgresSaver initialized successfully")
                
            self.checkpointer = CoffeeShopAgent._checkpointer
            
        except Exception as e:
            print("Error initializing PostgresSaver :", str(e))
            raise

    def create_agent(self, customer_id: int):
        print("\nCreating agent ............")
        
        tools = CoffeeShopTools(self.service, customer_id).get_tools()
        SYSTEM_PROMPT = get_system_prompt()
        
        print("\nLLM configuring .....")
        llm = get_llm(max_tokens=500, temperature=0.3)
        
        print("\nCreating agent in AGENT function .....")
        agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=SYSTEM_PROMPT,
            checkpointer=self.checkpointer
        )
        
        return agent

    def ask_invoke(self, user_query: str, agent, thread_id: str):
        
        print(f"\n User Query: {user_query}")
        config = {
            "configurable": {
                "thread_id": str(thread_id)
            }
        }
        
        result = agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": user_query}
                ]
            },
            config=config
        )
        
        return result

    def resume_invoke(self, agent, thread_id: str, decision: str):
        
        print(f"\n Resume invoke called with decision: {decision}")
        config = {
            "configurable": {
                "thread_id": str(thread_id)
            }
        }
        result = agent.invoke(
            Command(resume=decision),
            config=config
        )
        return result

    # def ask_streaming(self, user_query: str, agent):
    #     print(f"\n User Query in streaming: {user_query}")
    #     full_response = ""
    #
    #     for chunk in agent.stream(
    #         {"messages": [{"role": "user", "content": user_query}]},
    #         stream_mode="messages"):
    #
    #         msg, metadata = chunk
    #
    #         if msg.type == "AIMessageChunk" and msg.content:
    #             content = msg.content
    #
    #             if isinstance(content, list):
    #                 for block in content:
    #                     if isinstance(block, dict) and "text" in block:
    #                         print(block["text"], end="", flush=True)
    #                         full_response += block["text"]
    #
    #             elif isinstance(content, str):
    #                 print(content, end="", flush=True)
    #                 full_response += content
    #
    #     return full_response