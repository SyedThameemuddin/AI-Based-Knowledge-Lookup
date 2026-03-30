import os
import pandas as pd
from typing import Dict, Any

from langchain_groq import ChatGroq
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

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
            agent = create_pandas_dataframe_agent(
                self.llm,
                df,
                verbose=True,
                allow_dangerous_code=True,
                prefix="You are working with a pandas dataframe `df`. Safely perform the requested update, addition, or deletion on `df` in-memory. Do not write to disk yourself. Keep your final output simple and friendly."
            )
            
            result = agent.invoke(query)
            
            # Save the modified df back to disk to persist!
            if ext in [".xlsx", ".xls"]:
                df.to_excel(rag_engine.dataset_path, index=False)
            else:
                df.to_csv(rag_engine.dataset_path, index=False)

            # Re-index so the RAG search knows about the new data
            from utils.data_loader import DataLoader
            DataLoader().load_and_index(rag_engine.dataset_path)

            return {
                "status": "success",
                "answer": result.get("output", "Successfully updated the dataset."),
                "file_updated": True
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to successfully perform the data modification operation via Agent: {str(e)}"
            }

data_agent = DataAgent()
