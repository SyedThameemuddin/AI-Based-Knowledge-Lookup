import os
import pandas as pd
from typing import Dict, Any

import time
from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.callbacks import BaseCallbackHandler

class AgentLogHandler(BaseCallbackHandler):
    def __init__(self):
        self.logs = []
        
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get('name', 'python_ast_repl')
        self.logs.append(f"⚙️ **Executing {tool_name}:**\\n```python\\n{input_str}\\n```")
        
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        out = output[:200] + "..." if len(output) > 200 else output
        self.logs.append(f"⏱️ **Result:**\\n```text\\n{out}\\n```")

from settings import config
from utils.rag_engine import rag_engine

class DataAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=config.MODEL_NAME,
            temperature=0,
            api_key=config.GROQ_API_KEY
        )

    def is_modification_query(self, query: str) -> bool:
        prompt = f"""You are an intent classifier.
Analyze the user's query and output strictly "MODIFY" or "RETRIEVE".
If the user wants to add, delete, update, remove, insert, or change data, output "MODIFY". 
If the user wants to retrieve info, summarize, list, ask a question, greet you, or download something, output "RETRIEVE".

Query: {query}
"""
        response = self.llm.invoke(prompt)
        return "MODIFY" in response.content.upper()

    def handle_modification(self, query: str) -> Dict[str, Any]:
        if not rag_engine.dataset_path or not os.path.exists(rag_engine.dataset_path):
            return {"status": "error", "message": "No structured dataset is loaded to modify. Please upload a CSV or Excel file first."}

        ext = os.path.splitext(rag_engine.dataset_path)[1].lower()
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(rag_engine.dataset_path)
        elif ext == ".csv":
            df = pd.read_csv(rag_engine.dataset_path)
        else:
            return {"status": "error", "message": f"Modification agent specifically supports Excel and CSV files. Uploaded type: {ext}"}

        try:
            # We bypass the bloated LangChain pandas_agent to save 5000+ tokens and avoid 429s.
            import ast
            
            # Simple custom prompt to generate the exact Pandas update string
            prompt = f"""You are an expert Data Scientist.
You are given a pandas dataframe `df` with the following columns: {list(df.columns)}.
The user's dataset has {len(df)} rows.
The user wants to execute the following modification: "{query}"

Return ONLY the valid Python code to update `df` in-memory. DO NOT return markdown formatting (`python ...`), triple backticks, explanations, or print statements. ONLY return pure code. Example: df.loc[df['Name'] == 'Chris Anderson', 'Review'] = 3
"""
            
            # Use Groq to generate the raw pandas command
            code_response = self.llm.invoke(prompt).content.strip().replace('```python', '').replace('```', '').strip()
            
            # Provide an isolated environment for safety (basic)
            local_env = {'df': df, 'pd': pd}
            
            try:
                # Execute the safe in-memory pandas mutation
                exec(code_response, {}, local_env)
                updated_df = local_env['df']
            except Exception as e:
                # If the LLM generated bad syntax, gracefully catch and return it
                return {
                    "status": "error",
                    "message": f"Agent generated invalid update code: `{code_response}`. Error: {str(e)}"
                }
            
            # Save the modified df back to disk to persist!
            if ext in [".xlsx", ".xls"]:
                updated_df.to_excel(rag_engine.dataset_path, index=False)
            else:
                updated_df.to_csv(rag_engine.dataset_path, index=False)

            # Re-index so the RAG search knows about the new data
            from utils.data_loader import DataLoader
            DataLoader().load_and_index(rag_engine.dataset_path)

            full_response = f"### 🤖 Data Agent Executed:\\n`{code_response}`\\n\\n---\\n**✅ Update Complete!**\\nThe dataset has been successfully modified in memory and saved to disk."

            return {
                "status": "success",
                "answer": full_response,
                "file_updated": True
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to successfully perform the data modification operation via Agent: {str(e)}"
            }

data_agent = DataAgent()
