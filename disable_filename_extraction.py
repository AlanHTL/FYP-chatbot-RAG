#!/usr/bin/env python3
import os
import re
import sys

def disable_filename_extraction():
    """
    Completely disable the filename-based diagnosis extraction in chatbot_tester.py.
    This ensures tests only check against explicit disorder names in the test cases,
    not based on filenames.
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
        
        # Create the improved method with no filename dependency
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
        
        # For disorder cases, we MUST have an explicit disorder_name in the test case
        if "disorder_name" not in case["expected_diagnosis"]:
            print(f"WARNING: Test case is missing explicit disorder_name: {case.get('id', 'unknown')}")
            return False
            
        expected_disorder = case["expected_diagnosis"]["disorder_name"].lower()
        
        # Direct match with expected disorder name
        return expected_disorder in diagnosis_result"""
        
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
        
        print("Successfully updated _check_diagnosis method to require explicit disorder names")
        return True
        
    except Exception as e:
        print(f"Error updating _check_diagnosis method: {e}")
        return False

if __name__ == "__main__":
    if disable_filename_extraction():
        print("Successfully disabled filename-based diagnosis matching.")
        print("Test cases now require explicit disorder_name field in expected_diagnosis.")
        print("Run update_test_files.py to add disorder names to your test files.")
    else:
        print("Failed to update chatbot_tester.py. Please check the error messages above.")
        sys.exit(1) 