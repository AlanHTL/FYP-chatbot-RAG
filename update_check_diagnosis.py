#!/usr/bin/env python3
import os
import re
import sys

def extract_disorder_name_from_file(file_path):
    """Extract the disorder name from a test file path."""
    file_name = os.path.basename(file_path)
    match = re.match(r"(.+)_test\.json", file_name)
    if match:
        return match.group(1).replace("_", " ")
    return None

def update_check_diagnosis_method():
    """
    Update the _check_diagnosis method in chatbot_tester.py to properly evaluate
    responses instead of just matching against filenames.
    """
    try:
        # Read the current content of chatbot_tester.py
        with open("chatbot_tester.py", "r") as f:
            content = f.read()
        
        # Find the _check_diagnosis method
        check_diagnosis_pattern = r"def _check_diagnosis\(self, case:.*?expected_has_disorder = case.*?# For disorder cases.*?return \"(.*?)\" in diagnosis\.get\(\"result\", \[None\]\)\[0\]\.lower\(\)"
        
        # Check if we can find the method with regex
        match = re.search(check_diagnosis_pattern, content, re.DOTALL)
        if not match:
            print("Could not locate the _check_diagnosis method in chatbot_tester.py")
            return False
        
        # Create the improved method with properly formatted triple quotes
        updated_method = """    def _check_diagnosis(self, case: Dict[str, Any], diagnosis: Dict) -> bool:
        \"\"\"Check if the diagnosis matches the expected diagnosis.\"\"\"
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
        
        # For disorder cases, check for expected disorder names or symptoms
        expected_disorder = None
        if "disorder_name" in case["expected_diagnosis"]:
            # Use provided disorder name if available in the case data
            expected_disorder = case["expected_diagnosis"]["disorder_name"].lower()
        
        # Compare against chatbot diagnosis
        # Note: diagnosis_result has already been converted to lowercase
        if expected_disorder:
            # Direct match with expected disorder name
            return expected_disorder in diagnosis_result
        else:
            # If no expected disorder was provided, just check it's not "normal"
            return diagnosis_result != "normal\""""
        
        # Replace the old method with the updated one
        updated_content = re.sub(check_diagnosis_pattern, updated_method, content, flags=re.DOTALL)
        
        # Backup the original file
        backup_file = "chatbot_tester.py.bak"
        with open(backup_file, "w") as f:
            f.write(content)
        print(f"Original file backed up to {backup_file}")
        
        # Write the updated content
        with open("chatbot_tester.py", "w") as f:
            f.write(updated_content)
        
        print("Successfully updated _check_diagnosis method in chatbot_tester.py")
        
        # Also update test data preprocessing
        add_disorder_names_to_tests()
        
        return True
        
    except Exception as e:
        print(f"Error updating _check_diagnosis method: {e}")
        return False

def add_disorder_names_to_tests():
    """Add explicit disorder_name field to test cases if missing."""
    try:
        import json
        import glob
        import os
        
        # Find all test files
        test_files = glob.glob("test_files/*_test.json")
        if not test_files:
            test_files = glob.glob("*_test.json")
        
        if not test_files:
            print("No test files found.")
            return
            
        for test_file in test_files:
            # Get disorder name from filename
            disorder_name = extract_disorder_name_from_file(test_file)
            if not disorder_name:
                continue
                
            # Read the test file
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            
            # Check if test cases need updating
            modified = False
            for case in test_data.get("test_cases", []):
                expected_diagnosis = case.get("expected_diagnosis", {})
                
                # Add disorder_name to disorder cases if missing
                if expected_diagnosis.get("has_disorder") and "disorder_name" not in expected_diagnosis:
                    expected_diagnosis["disorder_name"] = disorder_name
                    modified = True
                    
            # Save the updated test data if modified
            if modified:
                with open(test_file, 'w') as f:
                    json.dump(test_data, f, indent=2)
                print(f"Updated test cases in {test_file}")
                
    except Exception as e:
        print(f"Error updating test files: {e}")

if __name__ == "__main__":
    if update_check_diagnosis_method():
        print("chatbot_tester.py has been successfully updated to properly evaluate diagnoses")
    else:
        print("Failed to update chatbot_tester.py. Please check the error messages above.")
        sys.exit(1) 