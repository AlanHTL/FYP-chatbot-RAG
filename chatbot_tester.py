import json
import os
import uuid
import time
import requests
import threading
import concurrent.futures
import re
from typing import Dict, List, Any, Tuple
import argparse

# OpenAI API settings
os.environ["OPENAI_API_KEY"] = "sk-UnNXXoNG6qqa1RUl24zKrakQaHBeyxqkxEtaVwGbSrGlRQxl"
os.environ["OPENAI_API_BASE"] = "https://xiaoai.plus/v1"

# Update the constant with environment variable support
CHATBOT_API_URL = os.environ.get("CHATBOT_API_URL", "http://127.0.0.1:8081/chat")

# Import necessary libraries for GPT model
from langchain_openai import ChatOpenAI

class ChatbotTester:
    """Class to test the screening chatbot accuracy using simulated patients."""

    def __init__(self, test_file_path: str, parallel_workers: int = 3):
        """Initialize the tester with the test case file."""
        self.test_file_path = test_file_path
        self.test_cases = self._load_test_cases()
        self.results = []
        self.conversation_history = {}
        self.parallel_workers = parallel_workers
        
        # Initialize GPT-3.5 model for patient simulation
        self.patient_simulator = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"]
        )

    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from the JSON file."""
        try:
            with open(self.test_file_path, 'r') as f:
                data = json.load(f)
                return data.get("test_cases", [])
        except Exception as e:
            print(f"Error loading test cases: {e}")
            return []

    def _create_patient_prompt(self, case: Dict[str, Any]) -> str:
        """Create a prompt for the GPT model to simulate a patient."""
        patient = case["patient_profile"]
        context = case.get("conversation_context", {})
        background = case.get("patient_background", {})
        symptoms = case["symptoms_and_experiences"]
        emotions = case["emotional_state"]
        behaviors = case["behavioral_patterns"]
        
        prompt = f"""
        You are roleplaying as a patient with the following characteristics:
        
        Name: {patient["name"]}
        Age: {patient["age"]}
        Gender: {patient.get("gender", "Not specified")}
        Occupation: {patient["occupation"]}
        
        Context:
        Setting: {context.get("setting", "Not specified")}
        Reason for visit: {context.get("reason_for_visit", "Health concerns")}
        
        Background:
        Living situation: {background.get("living_situation", "Not specified")}
        Family history: {background.get("family_history", "Not specified")}
        Medical history: {background.get("medical_history", "Not specified")}
        
        Main complaints:
        {', '.join(symptoms["main_complaints"])}
        
        Duration of symptoms: {symptoms["duration"]}
        Severity: {symptoms["severity"]}
        Impact on life: {symptoms["impact_on_life"]}
        
        Examples of issues:
        {', '.join(symptoms["specific_examples"])}
        
        Current mood: {emotions["current_mood"]}
        Thoughts: {', '.join(emotions["thoughts"])}
        Feelings: {', '.join(emotions["feelings"])}
        
        Behavioral patterns:
        Daily activities: {', '.join(behaviors["daily_activities"])}
        Changes in routine: {', '.join(behaviors["changes_in_routine"])}
        Coping mechanisms: {', '.join(behaviors["coping_mechanisms"])}
        
        Your task is to answer a mental health screening chatbot's questions naturally as if you were this patient. Be consistent with the above description but respond in a natural conversational way. Don't dump all of this information at once - only share details when directly asked about them. Initially just tell the chatbot your name and basic concern.
        
        When asked about your symptoms, gradually reveal the information based on the main complaints. Answer any follow-up questions with specific details from the examples provided. Use language that a real patient might use, not clinical terminology.
        
        If asked about your history, include relevant details from your family and medical history. If asked about your living situation, describe it according to the information provided.
        
        Remember to stay in character throughout the conversation - show the emotional state and thinking patterns described above in your responses.
        """
        return prompt

    def _get_patient_response(self, case: Dict[str, Any], chatbot_message: str, conversation_id: str) -> str:
        """Get a response from the simulated patient using GPT."""
        # First time this case is processed - create a new prompt
        if conversation_id not in self.conversation_history:
            # Initialize conversation history
            self.conversation_history[conversation_id] = {
                "prompt": self._create_patient_prompt(case),
                "messages": []
            }
        
        # Add the chatbot's message to history
        self.conversation_history[conversation_id]["messages"].append({"role": "assistant", "content": chatbot_message})
        
        # Create the full prompt with history
        messages = [
            {"role": "system", "content": self.conversation_history[conversation_id]["prompt"]},
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history[conversation_id]["messages"])
        
        # Get response from GPT
        try:
            response = self.patient_simulator.invoke(messages)
            patient_response = response.content
            
            # Save the response to history
            self.conversation_history[conversation_id]["messages"].append({"role": "user", "content": patient_response})
            
            return patient_response
        except Exception as e:
            print(f"Error getting patient response: {e}")
            return "I'm not feeling well."

    def _send_message_to_chatbot(self, message: str, conversation_id: str) -> str:
        """Send a message to the screening chatbot API."""
        headers = {'Content-Type': 'application/json'}
        payload = {
            'message': message,
            'conversation_id': conversation_id 
        }
        
        try:
            response = requests.post(CHATBOT_API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response_data = response.json()
            
            if "reply" in response_data:
                return response_data['reply']
            else:
                print(f"Error: 'reply' key not found in response: {response_data}")
                return "Error: Could not get reply from chatbot."
        except Exception as e:
            print(f"Error sending message to chatbot: {e}")
            return "Error: Could not communicate with chatbot."

    def _extract_diagnosis(self, message: str) -> Dict:
        """Extract the diagnosis JSON from the chatbot response."""
        try:
            # Look for JSON pattern in the text
            match = re.search(r'(\{\"result\":\[.*?\],\s*\"probabilities\":\[.*?\]\})', message)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            return None
        except Exception as e:
            print(f"Error extracting diagnosis: {e}")
            return None

    def _check_diagnosis(self, case: Dict[str, Any], diagnosis: Dict) -> bool:
        """Check if the diagnosis matches the expected diagnosis."""
        if not diagnosis or "result" not in diagnosis or not diagnosis["result"]:
            return False
        
        expected_has_disorder = case["expected_diagnosis"]["has_disorder"]
        diagnosis_result = diagnosis.get("result", [None])[0]
        
        if not diagnosis_result:
            return False
        
        diagnosis_result = diagnosis_result.lower()
        
        # For normal cases, check if result is "normal"
        if not expected_has_disorder:
            return diagnosis_result == "normal"
        
        # For disorder cases, check for expected disorder name
        expected_disorder = case["expected_diagnosis"].get("disorder_name", "").lower()
        if not expected_disorder:
            print(f"WARNING: Test case is missing disorder_name in expected_diagnosis: {case.get('case_id', 'unknown')}")
            return False
            
        # Direct match with expected disorder name
        return expected_disorder in diagnosis_result

    def _simulate_conversation(self, case: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, Dict]:
        """Simulate a conversation between the patient and the chatbot."""
        conversation_id = str(uuid.uuid4())
        print(f"Starting conversation for case {case['case_id']} (ID: {conversation_id})...")
        
        # Start the conversation with a greeting
        bot_message = "Hi, I am Dr. Mind, a mental health screening specialist. May I have your name, please?"
        
        # Simulate conversation until diagnosis or max turns
        max_turns = 15
        for i in range(max_turns):
            # Get patient response
            patient_response = self._get_patient_response(case, bot_message, conversation_id)
            print(f"Patient: {patient_response}")
            
            # Send to chatbot
            bot_message = self._send_message_to_chatbot(patient_response, conversation_id)
            print(f"Chatbot: {bot_message}")
            
            # Check if this is a diagnosis
            diagnosis = self._extract_diagnosis(bot_message)
            if diagnosis:
                print(f"Diagnosis received: {diagnosis}")
                correct = self._check_diagnosis(case, diagnosis)
                return case, correct, diagnosis
            
            # Add short delay to avoid rate limiting
            time.sleep(1)
        
        print(f"Max turns reached without diagnosis for case {case['case_id']}")
        return case, False, None

    def test_case(self, case_id: int) -> Tuple[Dict[str, Any], bool, Dict]:
        """Test a specific case by ID."""
        case = next((c for c in self.test_cases if c["case_id"] == case_id), None)
        if not case:
            print(f"Case {case_id} not found.")
            return None, False, None
        
        return self._simulate_conversation(case)

    def test_all_cases(self) -> List[Dict[str, Any]]:
        """Test all cases and return results."""
        results = []
        
        # Use ThreadPoolExecutor for parallel testing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit test cases with a delay between each to avoid overloading the API
            future_to_case = {}
            for case in self.test_cases:
                future = executor.submit(self._simulate_conversation, case)
                future_to_case[future] = case
                # Add a short delay between starting each conversation
                time.sleep(2)
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_case):
                case = future_to_case[future]
                try:
                    case_info, correct, diagnosis = future.result()
                    results.append({
                        "case_id": case["case_id"],
                        "patient_name": case["patient_profile"]["name"],
                        "expected_diagnosis": case["expected_diagnosis"]["disorder_name"] if case["expected_diagnosis"]["has_disorder"] else "Normal",
                        "actual_diagnosis": diagnosis.get("result", ["Unknown"])[0] if diagnosis else "No diagnosis",
                        "correct": correct,
                        "confidence": diagnosis.get("probabilities", [0])[0] if diagnosis else 0
                    })
                    print(f"Completed case {case['case_id']}: {'✓' if correct else '✗'}")
                except Exception as e:
                    print(f"Error processing case {case['case_id']}: {e}")
        
        self.results = results
        return results

    def calculate_accuracy(self) -> Dict[str, float]:
        """Calculate the accuracy metrics based on test results."""
        if not self.results:
            return {
                "overall_accuracy": 0,
                "true_positive_rate": 0,
                "true_negative_rate": 0
            }
        
        total = len(self.results)
        correct = sum(1 for r in self.results if r["correct"])
        
        # For true positive rate (correctly identifying disorder cases)
        disorder_cases = [r for r in self.results if r["expected_diagnosis"] != "Normal"]
        tp = sum(1 for r in disorder_cases if r["correct"])
        tpr = tp / len(disorder_cases) if disorder_cases else 0
        
        # For true negative rate (correctly identifying normal cases)
        normal_cases = [r for r in self.results if r["expected_diagnosis"] == "Normal"]
        tn = sum(1 for r in normal_cases if r["correct"])
        tnr = tn / len(normal_cases) if normal_cases else 0
        
        return {
            "overall_accuracy": correct / total,
            "true_positive_rate": tpr,
            "true_negative_rate": tnr
        }

    def print_results(self):
        """Print the test results and accuracy."""
        if not self.results:
            print("No test results available.")
            return
        
        print("\n===== TEST RESULTS =====")
        for result in self.results:
            status = "PASS" if result["correct"] else "FAIL"
            print(f"Case {result['case_id']} ({result['patient_name']}): {status}")
            print(f"  Expected: {result['expected_diagnosis']}")
            print(f"  Actual: {result['actual_diagnosis']} (confidence: {result['confidence']})")
            print("-" * 40)
        
        # Calculate and print accuracy metrics
        accuracy = self.calculate_accuracy()
        print("\n===== ACCURACY METRICS =====")
        print(f"Overall Accuracy: {accuracy['overall_accuracy']:.2%}")
        print(f"True Positive Rate: {accuracy['true_positive_rate']:.2%}")
        print(f"True Negative Rate: {accuracy['true_negative_rate']:.2%}")

    def test_selected_cases(self, case_ids: List[int]) -> List[Dict[str, Any]]:
        """Test only the specified case IDs."""
        results = []
        selected_cases = [case for case in self.test_cases if case["case_id"] in case_ids]
        
        if not selected_cases:
            print(f"No cases found with the specified IDs: {case_ids}")
            return results
            
        print(f"Testing {len(selected_cases)} selected cases: {case_ids}")
        
        # Use ThreadPoolExecutor for parallel testing
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            # Submit test cases with a delay between each to avoid overloading the API
            future_to_case = {}
            for case in selected_cases:
                future = executor.submit(self._simulate_conversation, case)
                future_to_case[future] = case
                # Add a short delay between starting each conversation
                time.sleep(2)
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_case):
                case = future_to_case[future]
                try:
                    case_info, correct, diagnosis = future.result()
                    results.append({
                        "case_id": case["case_id"],
                        "patient_name": case["patient_profile"]["name"],
                        "expected_diagnosis": case["expected_diagnosis"]["disorder_name"] if case["expected_diagnosis"]["has_disorder"] else "Normal",
                        "actual_diagnosis": diagnosis.get("result", ["Unknown"])[0] if diagnosis else "No diagnosis",
                        "correct": correct,
                        "confidence": diagnosis.get("probabilities", [0])[0] if diagnosis else 0
                    })
                    print(f"Completed case {case['case_id']}: {'✓' if correct else '✗'}")
                except Exception as e:
                    print(f"Error processing case {case['case_id']}: {e}")
        
        self.results = results
        return results
        
    def save_results_to_file(self, filename: str = "chatbot_test_results.json"):
        """Save the test results to a JSON file."""
        if not self.results:
            print("No results to save.")
            return
            
        result_data = {
            "test_file": self.test_file_path,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "accuracy_metrics": self.calculate_accuracy()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(result_data, f, indent=2)
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results to {filename}: {e}")


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Test the mental health screening chatbot accuracy.")
    parser.add_argument("--file", type=str, required=True,
                        help="Path to the test case JSON file")
    parser.add_argument("--save", type=str, required=True,
                        help="Save results to the specified JSON file")
    parser.add_argument("--save-responses", action="store_true",
                        help="Save detailed chatbot responses")
    parser.add_argument("--parallel", type=int, default=3,
                        help="Number of parallel tests to run (default: 3)")
    
    args = parser.parse_args()
    
    # Initialize the tester with the specified test file
    tester = ChatbotTester(args.file, args.parallel)
    print(f"Loaded {len(tester.test_cases)} test cases from {args.file}")
    
    # Run all tests
    print("Testing all cases...")
    tester.test_all_cases()
    
    # Print the results
    tester.print_results()
    
    # Save results
    tester.save_results_to_file(args.save) 