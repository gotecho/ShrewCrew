# ShrewCrew
 ![New Shrew Logo](https://github.com/user-attachments/assets/388f4ea8-84b1-4097-a011-387a7e9315f8)

ShrewTechs
=======
- Team Leader: Anthony Vitro
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
For CSC 191...

Developer Instructions
=======
For CSC 191...
