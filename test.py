# import os
# import json
# from auth import google_auth


# # Setting API call creds
# service_account_credentials = google_auth(
#     name="projects/422741767417/secrets/live-firebase-admin-sdk-credentials-key/versions/1",
#     mode="json",
# )

# print(service_account_credentials)





# import firebase_admin
# from firebase_admin import credentials, firestore
# from fastapi import FastAPI
# import requests
# import re
# from datetime import datetime
# from pytz import timezone
# from firebase_admin.firestore import SERVER_TIMESTAMP
# import json
# from auth import google_auth


# service_account_credentials = google_auth(
#     name="projects/422741767417/secrets/live-firebase-admin-sdk-credentials-key/versions/1",
#     mode="json",
# )
# with open("fsSdk.json", "w") as f:
#     json.dump(service_account_credentials, f, indent=4)

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate("fsSdk.json")
# firebase_admin.initialize_app( cred )
# db = firestore.client()
