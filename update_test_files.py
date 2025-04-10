#!/usr/bin/env python3
import os
import json
import glob
import re
import sys

def extract_disorder_name_from_file(file_path):
    """Extract the disorder name from a test file path."""
    file_name = os.path.basename(file_path)
    match = re.match(r"(.+)_test\.json", file_name)
    if match:
        return match.group(1).replace("_", " ")
    return None

def update_test_files(test_dir="."):
    """
    Update test files to include explicit disorder_name fields in the expected diagnosis.
    This ensures that tests are checking against actual disorder names, not just filename patterns.
    
    Args:
        test_dir: Directory containing test files
        
    Returns:
        int: Number of files updated
    """
    # Find all test files
    test_files = glob.glob(os.path.join(test_dir, "test_files", "*_test.json"))
    if not test_files:
        test_files = glob.glob(os.path.join(test_dir, "*_test.json"))
    
    if not test_files:
        print("No test files found.")
        return 0
    
    print(f"Found {len(test_files)} test files.")
    updated_count = 0
    
    for test_file in test_files:
        try:
            # Get disorder name from filename
            disorder_name = extract_disorder_name_from_file(test_file)
            if not disorder_name:
                print(f"Could not extract disorder name from {test_file}, skipping.")
                continue
            
            print(f"Processing: {test_file} (Disorder: {disorder_name})")
            
            # Read the test file
            with open(test_file, 'r') as f:
                test_data = json.load(f)
            
            # Check if test cases need updating
            modified = False
            disorder_cases = 0
            normal_cases = 0
            
            # Update the test cases
            for case in test_data.get("test_cases", []):
                expected_diagnosis = case.get("expected_diagnosis", {})
                
                # Add disorder_name to disorder cases if missing
                if expected_diagnosis.get("has_disorder", False):
                    disorder_cases += 1
                    if "disorder_name" not in expected_diagnosis:
                        expected_diagnosis["disorder_name"] = disorder_name
                        modified = True
                else:
                    normal_cases += 1
            
            print(f"  - Disorder cases: {disorder_cases}")
            print(f"  - Normal cases: {normal_cases}")
            
            # Save the updated test data if modified
            if modified:
                # Backup the original file
                backup_file = f"{test_file}.bak"
                with open(backup_file, 'w') as f:
                    json.dump(test_data, f, indent=2)
                print(f"  - Backed up original to {backup_file}")
                
                # Save the updated file
                with open(test_file, 'w') as f:
                    json.dump(test_data, f, indent=2)
                print(f"  - Updated with explicit disorder names")
                updated_count += 1
            else:
                print("  - No changes needed")
            
        except Exception as e:
            print(f"Error processing {test_file}: {e}")
    
    return updated_count

def main():
    """Process command line arguments and update test files."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update test files with explicit disorder names")
    parser.add_argument("--dir", type=str, default=".",
                       help="Directory containing test files (default: current directory)")
    args = parser.parse_args()
    
    print(f"Updating test files in {args.dir}")
    updated = update_test_files(args.dir)
    
    print(f"\nSummary: Updated {updated} test files with explicit disorder names")
    
    return 0 if updated > 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 