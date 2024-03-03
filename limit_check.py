import requests
import json
from datetime import datetime

def check_openai_usage(api_key):
    """
    Adjust the request to use the correct date format (YYYY-MM-DD) for the OpenAI API usage check.
    Using the first day of the current month as the date parameter.
    """
    # Use the first day of the current month in YYYY-MM-DD format
    first_day_of_month = datetime.now().strftime("%Y-%m-01")
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    params = {
        "date": first_day_of_month  # Correct the 'date' query parameter format
    }
    response = requests.get("https://api.openai.com/v1/usage", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json(), "status_code": response.status_code}

# Load your OpenAI API key from a local file
with open("api.key", "r") as file:
    api_key = file.read().strip()

# Check usage
usage_info = check_openai_usage(api_key)
print(json.dumps(usage_info, indent=4))

