# ShrewCrew
 ![New Shrew Logo](https://github.com/user-attachments/assets/388f4ea8-84b1-4097-a011-387a7e9315f8)

ShrewTechs
=======
- Team Leader: Anthony Vitro - avitro@csus.edu
- Team Member: Ronald Pierre Lingat
- Team Member: Ava Brady
- Team Member: Edmar Cimatu
- Team Member: Drew Izzo
- Team Member: Mia Brady
- Team Member: Spencer Headspeth
- Team Member: Rajesh Suresh

Synopsis
=======
![CSC 191 Flowchart](https://github.com/user-attachments/assets/133ecc88-1d52-418b-97fb-18da42199855)
Our project is to create an AI-powered texting channel for the 311 hotline that the Sacramento City uses. This texting channel can to take in a user's input and respond dynamically to that response. If the user asks a question, then the AI will respond to that question with relevant links acquired from Sacramento City's online resources. The user can also report various cases to the text channel and the text channel is able to gather information from the user, use that information to create a case, and then file that case to Sacramento City's Salesforce Database to be hosted. Cases the text channel can currently handle include Abandoned Vehicles, Dead Animals, as well as more generalized reports such as miscellaneous road hazards.

ERD:
![CSC 191 ERD (1)](https://github.com/user-attachments/assets/09cd77e6-c200-442d-8311-2f85988b67b6)
In order to accomplish this, Sacramento City has asked us to use Google Cloud's Dialogflow CX service, which has allowed us to use their Conversational Agents feature in order to accomplish our tasks. This involves us using "agents," which are effectively AI bots, in order to direct the flow of conversation to properly service the user. These agents use playbooks as instruction sets for what to do, when they receive that message, whether such as answering the question directly or referring them to another agent with their own playbook in order to answer the user's query.

We have also developed various tools so that the agent using the playbook can then use the tool associated with that playbook in order to accomplish at task. This can be a tool to report a specific kind of case to Salesforce or a tool to gather information from Sacramento City's online resources. Almost every playbook has a tool associated with it in our product.

Testing
=======
To test the endpoints, first: download requirements.txt (pip install -r requirements.txt), second: go to the base folder of the Github and run 'pytest'

Deployment
=======
Prerequisites <br />
Before deploying, make sure you have:<br />
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed <br />
- Docker installed <br />
- Run the following to authenticate and set your project:<br />

```bash
gcloud auth login
gcloud config set project [PROJECT_ID]
```

Replace `[PROJECT_ID]` with your actual Google Cloud project ID.<br />

---

Build and Push Docker Image <br />

**1. Build the Docker image (M1/M2 compatible):**<br />
```bash
DOCKER_DEFAULT_PLATFORM=linux/amd64/v8 docker build -t gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] .
```

**2. Push the image to Google Container Registry:**<br />
```bash
docker push gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG]
```

- `[PROJECT_ID]`: Your GCP project ID <br />
- `[IMAGE_NAME]`: Your image name (e.g., `flask-webhook`) <br />
- `[TAG]`: Optional version tag (e.g., `v1`, `latest`) <br />

---

Deploy `project_structure` (SMS Messaging Webhook) <br />
This webhook handles SMS via Twilio and **does not require a static IP**.<br />

```bash
gcloud run deploy [SERVICE_NAME] \
  --image gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] \
  --region [REGION] \
  --platform managed \
  --allow-unauthenticated
```

Cloud Run will return a public URL for the webhook after deployment.<br />

---

Deploy `tool_webhook` (Dialogflow + Salesforce Tools) <br />
This webhook requires a **static IP** due to external services (e.g., ArcGIS, Salesforce).<br />

One-Time Setup for Static IP <br />
```bash
gcloud compute networks create [VPC_NETWORK_NAME] --subnet-mode=custom

gcloud compute networks subnets create [SUBNET_NAME] \
  --network=[VPC_NETWORK_NAME] \
  --region=[REGION] \
  --range=10.8.0.0/28

gcloud compute networks vpc-access connectors create [VPC_CONNECTOR_NAME] \
  --region=[REGION] \
  --network=[VPC_NETWORK_NAME] \
  --range=10.8.0.0/28

gcloud compute addresses create [STATIC_IP_NAME] --region=[REGION]

gcloud compute routers create [ROUTER_NAME] \
  --network=[VPC_NETWORK_NAME] \
  --region=[REGION]

gcloud compute routers nats create [NAT_NAME] \
  --router=[ROUTER_NAME] \
  --region=[REGION] \
  --nat-custom-subnet-ip-ranges=[SUBNET_NAME] \
  --nat-external-ip-pool=[STATIC_IP_NAME] \
  --enable-logging
```

Deploy with VPC and Static IP Egress <br />
```bash
gcloud run deploy [SERVICE_NAME] \
  --image gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] \
  --region [REGION] \
  --network [VPC_NETWORK_NAME] \
  --subnet [SUBNET_NAME] \
  --vpc-egress all-traffic \
  --allow-unauthenticated
```

Ensure your environment variables and service credentials are properly configured via the Cloud Run UI or Secret Manager.<br />


Developer Instructions
=======
Local Setup <br />

**1. Clone the repository:**<br />
```bash
git clone https://github.com/[your-org-or-username]/ShrewCrew.git
cd ShrewCrew
```

**2. Set up a virtual environment:**<br />
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies:**<br />
```bash
pip install -r requirements.txt
```

**4. Set up environment variables:**<br />
Create a `.env` file in the root directory and define the following:<br />

```
SALESFORCE_AUTH_URL=
SALESFORCE_CLIENT_ID=
SALESFORCE_SECRET_KEY=
SALESFORCE_USERNAME=
SALESFORCE_PASSWORD=
SALESFORCE_URL=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
EXTERNAL_GIS_URL=
```

Ensure all necessary values are filled in based on project requirements.<br />

---

Run Locally <br />

To run the Flask app locally:<br />
```bash
flask run
```

Or to run using Gunicorn for production-style testing:<br />
```bash
gunicorn app:app
```

Replace `app:app` with the correct module and app name if needed.<br />

---

Run Tests <br />

To run the test suite from the project root:<br />
```bash
pytest
```

Product Example Images
=======
![IMG_1607](https://github.com/user-attachments/assets/b33f1ba4-997b-46b6-94bf-28be5fee43d5)
*This first image shows starting a new session with the product with the keywords "New Session," then saying you want to file an abandoned vehicle case. The product will then begin to gather information.*

![IMG_1608](https://github.com/user-attachments/assets/4c25e81a-557d-4805-a331-2b3630fec463)
*This second image shows the AI Text Channel continuing to gather information from the user, and then sending one last larger message in order to confirm with the user that the info the AI has gathered is correct. This confirmation message should happen with any case a user files with the text channel.*

![IMG_1609](https://github.com/user-attachments/assets/a5c412f6-c10f-4a00-86a4-8a85cf2a3ace)
*This third image shows the Text Channel filing the case to Salesforce, and then telling the user their specific case number so that they may reference it again later. This should also happen whenever a user files a case with the text channel.*


