import logging
import urllib.parse
import requests
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun


@function_tool
async def get_weather(context: RunContext, city: str) -> str:
    """
    Get the current weather for a given city
    """
    try:
        encoded_city = urllib.parse.quote(city)
        url = f"https://wttr.in/{encoded_city}?format=3"
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}."

@function_tool
async def search_web(context: RunContext, query: str) -> str:
    """
    Search the web for a given query using DuckDuckGo and return the top result.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        if results:
            logging.info(f"Search results for '{query}': {results}")
            return results
        else:
            logging.warning(f"No results found for '{query}'.")
            return f"No results found for '{query}'."
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."