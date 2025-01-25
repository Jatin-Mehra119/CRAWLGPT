import json
import pickle
from typing import Dict, Any, List
import os
from datetime import datetime

class DataManager:
    """
    Handles data import/export operations for the application.
    
    This class manages serialization and deserialization of data to/from files,
    supporting both JSON and pickle formats for different data types.
    
    Attributes:
        export_dir (str): Directory where exported files are stored
        
    Examples:
        >>> data_manager = DataManager(export_dir="exports")
        >>> data = {"metrics": {"requests": 100}}
        >>> filepath = data_manager.export_data(data, "metrics")
        >>> imported_data = data_manager.import_data(filepath)
    """
    def __init__(self, export_dir: str = "exports"):
        """
        Initialize DataManager with export directory.
        
        Args:
            export_dir (str): Path to directory for storing exports. 
                            Created if it doesn't exist.
        """
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        
    def export_data(self, data: Dict[str, Any], data_type: str) -> str:
        """
        Export data to a timestamped file.
        
        Args:
            data (Dict[str, Any]): Data to export
            data_type (str): Type of data ('vector_database' or other)
        
        Returns:
            str: Path to the exported file
            
        Examples:
            >>> data = {"metrics": {"requests": 100}}
            >>> filepath = data_manager.export_data(data, "metrics")
            >>> print(filepath)
            'exports/metrics_20240123_123456.json'
        """
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
        """
        Import data from a file.
        
        Args:
            filepath (str): Path to the file to import
        
        Returns:
            Dict[str, Any]: Imported data

        Examples:
            >>> imported_data = data_manager.import_data("exports/metrics_20240123_123456.json")
            >>> print(imported_data)
            {'metrics': {'requests': 100}}
        """
        if filepath.endswith('.pkl'):
            with open(filepath, "rb") as f:
                return pickle.load(f)
        else:
            with open(filepath, "r") as f:
                return json.load(f)