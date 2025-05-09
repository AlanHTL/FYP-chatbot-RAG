# Screening chatbot testing
We used Python to implement the screening chatbot testing:
using api.py to host a server,
using request.py to communicate with the chatbot manually,
using run_all_test.py to run the test using multi-tester, connecting to api.py
The run_all_test.py used the "Test json" file to run tests based on the cases in the file.
---
## 1. install requirements
Install the requirement using pip install:
```bash
pip install -r requirements.txt
```
---
## 2. Hosting the chatbot server through api.py
The current prompt is using the CoT + Few-shot method, if you want to change the prompt to the prompt 2 with ToT method, please modify the prompt with the "prompt 2.txt"

For first time use, make sure that the RAG data: "mental_disorders.json" is available for embedding it into vector database. It will generate a "faiss_index" file to save the vector storage.

Confirm the hosting port through .env file
API_PORT=8080
API_HOST=127.0.0.1
CHATBOT_API_URL=http://127.0.0.1:8080/chat

start server:
Open a terminal
```bash
python api.py
```
## 3. connect to the chatbot server through request.py
Open a terminal
```bash
python request.py
```
you can commnicate with the chatbot here

## 4. test the chatbot through run_all_tests.py
run_all_tests.py create multiple chatbot_test on different port (default number of testing server = 3, you can modify in .env) to test the api.py chatbot using the test data of "Test json" file
make sure that the file of "Test json" exsit
make sure the visualize_result.py, multi_disorder_tester.py, and chatbot_tester.py exsit
make sure the port and number of servers in .env correct

Open a terminal
```bash
python run_all_tests.py
```
the result will be in the results file
