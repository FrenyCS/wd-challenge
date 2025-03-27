## Building a Microservice for Property Alert Notifications

### Background:
Your company, which operates in the real estate sector, wants to engage users by
sending personalized notifications about property listings and offers based on their
preferences.

### Task:
Create a simple Python-based microservice that sends property alert notifications.
Focus on email and SMS notifications.

### Requirements:
1. Architecture Outline:
   - Sketch a basic architecture for the microservice.
   - Explain how it will integrate with existing property management systems and user databases accessible via RESTful APIs.
   - Choose and justify the use of specific technologies, suggesting Flask or FastAPI for simplicity.
   - Candidates are encouraged to ask questions to better define any ambiguities in the system’s requirements or existing integrations.
2. Code Prototype:
   - Objective: Build a prototype capable of sending notifications based on
   user preferences.
   - Key Functionalities:
     - Notification System: Implement email and SMS notifications (Can
       be mocked). 
     - API Development
         - An endpoint to schedule notifications (POST /notifications). 
         - Endpoints to manage user preferences (GET, POST
           /preferences/{user_id}). 
         - Payload example for POST: { "email_enabled": true,
           "sms_enabled": false } 
   - Queuing Mechanism: Use a simple queue system for task management. 
   - Implementation Details: Use Flask or FastAPI for the API and a
     relational DB. 
   - Testing: Candidates should provide example unit tests for their code and
     mock-up integration tests.
3. Documentation:
   - Provide a README file with setup and basic usage instructions. Include
   explanations for running tests and a section on known limitations or areas
   for improvement.
   
### Deliverables:
   - Architecture Diagram: A simple diagram showing the microservice architecture.
   - GitHub Repository: Containing all source code and the README.