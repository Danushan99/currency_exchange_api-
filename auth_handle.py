import os
import json
from auth import google_auth


# Setting API call creds
service_account_credentials = google_auth(
    name="projects/422741767417/secrets/live-gcp-cloud-functions-invoke/versions/latest",
    mode="json",
)

with open("temp_creds.json", "w") as f:
    json.dump(service_account_credentials, f, indent=4)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_creds.json"
