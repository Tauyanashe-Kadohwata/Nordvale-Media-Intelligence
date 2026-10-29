from abc import ABC, abstractmethod
import pandas as pd

class ITransformer(ABC):
    """
    Interface for data transformation classes.
    Defines the contract for transforming data into a desired format or structure.
    Methods:
        transform_data(data: pd.DataFrame): Abstract method to be implemented by subclasses for data transformation.
    """

    @abstractmethod
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the input data into a desired format or structure.
        Args:
            data (pd.DataFrame): Input DataFrame to be transformed.
        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        pass