from abc import ABC, abstractmethod
import pandas as pd

class IExtractor(ABC):
    """
    Interface for data extraction classes.
    Defines the contract for extracting data from API endpoints or other sources.
    Methods:
        extract_data(): Abstract method to be implemented by subclasses for data extraction.
    """

    @abstractmethod
    def extract_data(self):
        """
        Reads data from API endpoins and returns it as pandas DataFrame.
        Returns:
            pd.DataFrame: DataFrame containing the extracted data.
        """
        pass