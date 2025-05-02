# script verifies that code is connecting to the 
# correct project within GCP as well as 
# verifies that login credentials are valid
from google.auth import default

creds, project = default()
print("Authenticated project:", project)
print("Credentials valid:", creds.valid)