from bods_data_extractor import BODSDataExtractor
import pandas as pd
import requests

# Replace with your actual API key
api_key = '44f6986733e5ffee883319e58ffd16a4d164a4d8'

# --- Initialize the extractor and get metadata for SIRI-VM feeds ---
my_bus_data_object = BODSDataExtractor(
    api_key=api_key,
    data_format='SIRI-VM',
    status='published'
)

# --- Find the specific feed for First West of England (FBWE) ---
first_bus_feeds = my_bus_data_object.metadata[
    my_bus_data_object.metadata['noc'].str.contains('FBWE', case=False, na=False)
]

if not first_bus_feeds.empty:
    # --- Get the resource URL for the feed ---
    feed_url = first_bus_feeds.iloc[0]['resource_uri']
    print(f"First Bus (FBWE) SIRI-VM feed URL found: {feed_url}")

    # --- Fetch the real-time data from the dynamically found URL ---
    try:
        response = requests.get(feed_url, headers={'Authorization': api_key, 'Accept': 'application/xml'})
        response.raise_for_status()
        
        # Now you can proceed with parsing the XML content from response.content
        print("Successfully downloaded real-time data.")
        # print(response.content)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

else:
    print("No First Bus (FBWE) SIRI-VM feed found in the published datasets.")

