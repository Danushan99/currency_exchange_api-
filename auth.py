from google.cloud import secretmanager
from google.oauth2 import service_account
import json
import google.oauth2.id_token
import google.auth.transport.requests


def google_auth(name, mode="service_account"):

    client = secretmanager.SecretManagerServiceClient()

    # name = f"projects/YOUR_PROJECT_ID/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(name=name)

    if mode == "service_account":
        # Return the secret payload.
        service_account_json = json.loads(response.payload.data.decode("UTF-8"))
        credentials = service_account.Credentials.from_service_account_info(
            service_account_json
        )
    elif mode == "json":
        print("json key type triggerred")
        service_account_json = json.loads(response.payload.data.decode("UTF-8"))
        credentials = service_account_json
    else:  # plain text api keys
        print("plain text mode triggerred")
        credentials = response.payload.data.decode("UTF-8")

    return credentials


def verify_token(token, current_url):
    try:
        request_adapter = google.auth.transport.requests.Request()
        id_info = google.oauth2.id_token.verify_oauth2_token(token, request_adapter)
        # print('id_info --', id_info)
        # print('token received --', token)
        # print('current_url --', current_url)
        
        if id_info["aud"].split('//')[-1] == current_url.split('//')[-1]:
            return True
        else:
            return None

    except ValueError as e:
        return None


