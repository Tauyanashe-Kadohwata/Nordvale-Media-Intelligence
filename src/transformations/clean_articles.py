import json
import pandas as pd
from pathlib import Path
from src.transformations.interface import ITransformer

class ArticleReader:
    def read_data(self):
        # Locate project root
        base_dir = Path(__file__).resolve().parents[2]
        input_file = base_dir / "data" / "bronze" / "news_data.json"

        # Validate input file
        if not input_file.exists():
            raise FileNotFoundError(
                f"Expected file is missing at: {input_file}"
            )

        if not input_file.is_file():
            raise ValueError(
                f"Path exists but is not a file: {input_file}"
            )

        # Read and parse JSON
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"Successfully loaded JSON file: {input_file.name}")
        return data


if __name__ == "__main__":
    reader = ArticleReader()

    try:
        # Step 1: Read Bronze JSON
        file_contents = reader.read_data()

        print("Data loaded successfully.")
        print(f"Data type: {type(file_contents)}")

        # Step 2: Validate JSON structure
        if not isinstance(file_contents, dict):
           raise ValueError("Expected JSON root to be a dictionary.")

        print(f"JSON keys: {list(file_contents.keys())}")

        # Step 3: Convert articles to DataFrame
        df = pd.DataFrame.from_dict(file_contents)

        print("\nDataFrame created successfully.")
        print(f"DataFrame shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")

        print("\nArticle data:")
        print(df.head(3))

    except Exception as e:
        print(f"Error processing Bronze data: {e}")
        raise

#---------------------------------------- Cleaning -----------------------------------------------------#
class ArticleCleaner(ITransformer):
    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        data = data.drop_duplicates(subset=["id"])
        data = data.dropna(subset=["title"])
        data["publish_date"] = pd.to_datetime(
            data["publish_date"], errors="coerce"
        )
        return data

if __name__ == "__main__":
    reader = ArticleReader()
    cleaner = ArticleCleaner()

    raw_data = reader.read_data()
    df = pd.DataFrame.from_dict(raw_data)
    cleaned_df = cleaner.transform_data(df)

    print(f"Before cleaning: {df.shape}")
    print(f"After cleaning: {cleaned_df.shape}")
    print(cleaned_df.head())
    