import json
import pickle
from typing import Dict, Any, List
import os
from datetime import datetime

class DataManager:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        
    def export_data(self, data: Dict[str, Any], data_type: str) -> str:
        """Export data to a file with timestamp"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{data_type}_{timestamp}"
        
        if data_type == "vector_database":
            # Export vector database
            filepath = os.path.join(self.export_dir, f"{filename}.pkl")
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
        else:
            # Export other data as JSON
            filepath = os.path.join(self.export_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
                
        return filepath
    
    def import_data(self, filepath: str) -> Dict[str, Any]:
        """Import data from a file"""
        if filepath.endswith('.pkl'):
            with open(filepath, "rb") as f:
                return pickle.load(f)
        else:
            with open(filepath, "r") as f:
                return json.load(f)