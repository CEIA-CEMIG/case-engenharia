import json
import os
import glob
from pathlib import Path
import re

def extract_test_number(filename):
    match = re.search(r'response_test_(\d+)', filename)
    if match:
        return int(match.group(1))
    return 0

def process_single_test_file(file_path, case_number):
    eval_cases = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "eval_cases" in data:
            for idx, eval_case in enumerate(data["eval_cases"], 1):
                clean_case = {
                    "eval_id": f"case{case_number:02d}",
                    "conversation": [],
                    "session_input": eval_case.get("session_input", {
                        "app_name": "cemig_agent",
                        "user_id": "test_user",
                        "state": {}
                    })
                }
                
                for conv in eval_case.get("conversation", []):
                    clean_conv = {
                        "invocation_id": conv.get("invocation_id", f"test-{case_number:03d}"),
                        "user_content": conv.get("user_content", {}),
                        "final_response": conv.get("final_response", {})
                    }
                    clean_case["conversation"].append(clean_conv)
                
                eval_cases.append(clean_case)
                case_number += 1
        
        elif "invocation_id" in data or "user_content" in data:
            clean_case = {
                "eval_id": f"case{case_number:02d}",
                "conversation": [
                    {
                        "invocation_id": data.get("invocation_id", f"test-{case_number:03d}"),
                        "user_content": data.get("user_content", {}),
                        "final_response": data.get("final_response", {})
                    }
                ],
                "session_input": data.get("session_input", {
                    "app_name": "cemig_agent",
                    "user_id": "test_user",
                    "state": {}
                })
            }
            eval_cases.append(clean_case)
            case_number += 1
        
        elif "conversation" in data:
            clean_case = {
                "eval_id": f"case{case_number:02d}",
                "conversation": [],
                "session_input": data.get("session_input", {
                    "app_name": "cemig_agent",
                    "user_id": "test_user",
                    "state": {}
                })
            }
            
            for conv in data.get("conversation", []):
                clean_conv = {
                    "invocation_id": conv.get("invocation_id", f"test-{case_number:03d}"),
                    "user_content": conv.get("user_content", {}),
                    "final_response": conv.get("final_response", {})
                }
                clean_case["conversation"].append(clean_conv)
            
            eval_cases.append(clean_case)
            case_number += 1
        
        else:
            print(f"Warning: Unrecognized format in file {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    
    return eval_cases, case_number

def concatenate_test_files(input_dir="tests/final_response", output_file="teste_benchmark.evalset.json"):
    
    if not os.path.exists(input_dir):
        print(f"Error: Directory '{input_dir}' does not exist.")
        os.makedirs(input_dir, exist_ok=True)
        print(f"Directory created.")
        return False

    pattern = os.path.join(input_dir, "response_test_*.test.json")
    test_files = glob.glob(pattern)

    if not test_files:
        pattern = os.path.join(input_dir, "response_test_*.json")
        test_files = glob.glob(pattern)
    
    if not test_files:
        print(f"No test files found in {input_dir}")
        return False
    
    test_files.sort(key=lambda x: extract_test_number(os.path.basename(x)))
    
    print(f"Found {len(test_files)} test files to process")
    
    benchmark = {
        "eval_set_id": "teste_benchmark",
        "name": "teste_benchmark",
        "description": None,
        "eval_cases": []
    }
    
    case_counter = 1
    
    for idx, file_path in enumerate(test_files, 1):
        filename = os.path.basename(file_path)
        print(f"Processing [{idx:2d}/{len(test_files)}]: {filename}")
        
        eval_cases, case_counter = process_single_test_file(file_path, case_counter)
        benchmark["eval_cases"].extend(eval_cases)
    
    import time
    current_timestamp = time.time()
    for case in benchmark["eval_cases"]:
        if "creation_timestamp" not in case:
            case["creation_timestamp"] = current_timestamp
    
    try:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created '{output_file}'")
        print(f"Total evaluation cases: {len(benchmark['eval_cases'])}")
        
        total_conversations = sum(len(case.get("conversation", [])) for case in benchmark["eval_cases"])
        print(f"Total conversations: {total_conversations}")
        
        print("Sample cases created:")
        for case in benchmark["eval_cases"][:5]:
            user_msg = ""
            if case.get("conversation") and case["conversation"][0].get("user_content"):
                parts = case["conversation"][0]["user_content"].get("parts", [])
                if parts and parts[0].get("text"):
                    user_msg = parts[0]["text"][:60] + "..." if len(parts[0]["text"]) > 60 else parts[0]["text"]
            print(f"  {case['eval_id']}: {user_msg}")
        
        if len(benchmark["eval_cases"]) > 5:
            print(f"  ... and {len(benchmark['eval_cases']) - 5} more cases")
        
        return True
        
    except Exception as e:
        print(f"Error writing output file: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_output(output_file="teste_benchmark.evalset.json"):
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Validating '{output_file}':")
        print(f"  eval_set_id: {data.get('eval_set_id', 'N/A')}")
        print(f"  name: {data.get('name', 'N/A')}")
        print(f"  evaluation cases: {len(data.get('eval_cases', []))}")
        
        valid_cases = 0
        missing_fields = []
        
        for case in data.get('eval_cases', []):
            has_all_fields = True
            required_fields = ['eval_id', 'conversation', 'session_input']
            
            for field in required_fields:
                if field not in case:
                    has_all_fields = False
                    missing_fields.append(f"Case {case.get('eval_id', 'unknown')}: missing {field}")
            
            if has_all_fields:
                if case['conversation'] and len(case['conversation']) > 0:
                    conv = case['conversation'][0]
                    if 'user_content' in conv and 'final_response' in conv:
                        valid_cases += 1
        
        print(f"  valid cases: {valid_cases}/{len(data.get('eval_cases', []))}")
        
        if missing_fields:
            for msg in missing_fields[:5]:
                print(f"    {msg}")
            if len(missing_fields) > 5:
                print(f"    ... and {len(missing_fields) - 5} more issues")
        
        return valid_cases == len(data.get('eval_cases', []))
        
    except FileNotFoundError:
        print(f"File '{output_file}' not found")
        return False
    except Exception as e:
        print(f"Validation error: {e}")
        return False

if __name__ == "__main__":
    INPUT_DIR = "tests/final_response"
    OUTPUT_FILE = "teste_benchmark_complete.evalset.json"
    
    success = concatenate_test_files(INPUT_DIR, OUTPUT_FILE)
    
    if success:
        print("Validating generated file")
        if validate_output(OUTPUT_FILE):
            print("Process completed successfully")
        else:
            print("File generated but validation found issues")
    else:
        print("Process failed")