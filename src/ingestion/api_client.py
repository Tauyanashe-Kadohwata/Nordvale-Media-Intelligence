import os
import asyncio
import logging
import requests
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from src.ingestion.interface import IExtractor

# Load environment variables
load_dotenv()
API_KEY = os.getenv("WORLD_NEWS_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

BASE_URL = "https://api.worldnewsapi.com/search-news"

PARAMS = {
    "text": "renewable energy",
    "language": "en",
    "number": 10,
    "offset": 0
}

HEADERS = {
    "x-api-key": API_KEY
}


class NewsAPIClient(IExtractor):
    def __init__(self):
        self.base_url = BASE_URL
        self.params = PARAMS.copy()
        self.headers = HEADERS

    async def extract_data(self, offset=0):
        try:
            current_params = self.params.copy()
            current_params["offset"] = offset

            response = requests.get(
                self.base_url,
                params=current_params,
                headers=self.headers,
                timeout=30
            )

            # Log the API's error response before raising
            if not response.ok:
                logging.error(
                    "API response body: %s",
                    response.text[:1000]
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logging.error("Error fetching news: %s", e)
            return None


async def main():
    client = NewsAPIClient()

    TOTAL_ARTICLES = 100
    BATCH_SIZE = 10

    all_articles = []
    ingestion_failed = False

    for current_offset in range(0, TOTAL_ARTICLES, BATCH_SIZE):
        logging.info(
            "Fetching articles %d to %d",
            current_offset,
            current_offset + BATCH_SIZE - 1
        )

        data = await client.extract_data(offset=current_offset)

        if data is None:
            logging.error(
                "Stopping ingestion: request failed at offset %d",
                current_offset
            )
            ingestion_failed = True
            break

        articles = data.get("news", [])

        if not articles:
            logging.info("No more articles returned. Stopping pagination.")
            break

        all_articles.extend(articles)

        logging.info(
            "Successfully retrieved %d articles",
            len(articles)
        )

        if len(articles) < BATCH_SIZE:
            logging.info("Last page reached.")
            break

        # Pause between requests
        if current_offset + BATCH_SIZE < TOTAL_ARTICLES:
            await asyncio.sleep(1)

    logging.info("Total articles collected: %d", len(all_articles))

    if ingestion_failed:
        logging.warning(
            "Incomplete ingestion: collected %d of %d requested articles",
            len(all_articles),
            TOTAL_ARTICLES
        )

    if not all_articles:
        logging.warning("No articles collected. No JSON created.")
        return

    # Create DataFrame from ALL collected batches
    df = pd.DataFrame(all_articles)

    columns = [
        "id",
        "title",
        "summary",
        "url",
        "publish_date",
        "author",
        "source_country",
        "sentiment"
    ]

    df = df.reindex(columns=columns)

    logging.info("Total DataFrame rows: %d", len(df))
    logging.info("Unique article IDs: %d", df["id"].nunique())
    logging.info(
        "Duplicate article IDs: %d",
        df["id"].duplicated().sum()
    )

    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    OUTPUT_DIR = PROJECT_ROOT / "data" / "bronze"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Avoid overwriting an earlier successful file with partial data
    filename = (
        "news_data_partial.json"
        if ingestion_failed
        else "news_data.json"
    )

    output_path = OUTPUT_DIR / filename

    df.to_json(output_path, index=False)

    logging.info("News data saved to %s", output_path)

    if ingestion_failed:
        logging.warning(
            "Saved partial data for inspection; ingestion was NOT successful."
        )
    else:
        logging.info("Ingestion completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
