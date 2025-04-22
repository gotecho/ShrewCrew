# ShrewCrew
 ![Shrew logo (1)](https://github.com/user-attachments/assets/a7e46d64-bf4a-4d0c-a2de-d96bc6980590)

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
![Shrew Crew - Sprint 1 ERD (5)](https://github.com/user-attachments/assets/c6764f20-2b85-45c5-bd72-24c2b7e75553)
Our project is to create a texting channel for the 311 hotline that the Sacramento City uses. This texting channel will be able to take in a user's input and respond dynamically to that response. If the user asks a question, then the AI will respond to that question. If the user asks a question about a specific ticket, then the AI will access the ticket in question and respond with the appropriate information. If the user asks to file a ticket, then the AI will be able to gather information from the user and use that information to create a ticket.

ERD:
![Shrew Crew - Sprint 1 ERD (10)](https://github.com/user-attachments/assets/7bd8e6d1-c690-4b28-9e2f-e4a7513d1e66)

In order to accomplish this, Sacramento City has asked us to use Google Cloud's Dialogflow CX service, which has allowed us to use their Conversational Agents feature in order to accomplish our tasks. This involves us using Agents, which are effectively AI bots, in order to direct the flow of conversation to properly service the user. These agents use Playbooks as instruction sets for what to do, when they receive that message, whether such as answering the question directly or referring them to another Agent with their own playobok in order to answer the User's query.

![IMG_0131](https://github.com/user-attachments/assets/3d0a29fa-c478-4c41-96f6-968c40b600ee)

We, however, still must develop the tools necessary for Dialogflow CX to both post the completed ticket into Salesforce and validate that the person who is texting is actually in Sacramento. If they are not, then we must direct them to the proper hotline in the location they are in. Moreover, we must still develop the admin dashboard that will be used by the team at Sacramento City in order to keep tract of this texting channel.

Testing
=======
To test the endpoints, go to tool_webhook and then webhook_tools. When there, go in the terminal in VSCode and type "pytest filename.py" without the quotation marks. Replace "filename.py" with the actual name of the file. 

Deployment
=======
For CSC 191...

Developer Instructions
=======
For CSC 191...

Timeline
=======
- Sprint 1: Basic functionality, get familiar with the class and acquire a project.
- Sprint 2: Get formal documents in order, get basic functionality of twilio scripts and other components.
- Sprint 3: Create the visual dashboard for the twilio texting channel, make connections between components.
- Sprint 4: Add logging to all the components and connect the Gemini AI to the Twilio text channel.
- Sprint 5: Get Salesforce scripts working, advance the Twilio app, and link ArcGIS and Salesfore together.
- Sprint 6: Ensure the AI is able to work based on our designated flows (asking both types of questions and filing tickets)
- Sprint 7: Finalize testing, fix any bugs that may arise.
- Sprint 8: Finishing touches.

