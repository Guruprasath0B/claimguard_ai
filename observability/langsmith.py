# observability/langsmith.py

from langsmith import Client

from config.settings import settings


def get_langsmith_client() -> Client:
    return Client(
        api_url=settings.LANGCHAIN_ENDPOINT,
        api_key=settings.LANGCHAIN_API_KEY,
    )


langsmith_client = get_langsmith_client()