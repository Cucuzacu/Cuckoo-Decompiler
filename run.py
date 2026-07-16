# run_cuckoo.py
# part of the Cuckoo-Decompiler project

import subprocess
import os
import sys
import tempfile
import shutil
import json
import requests

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def run_ghidra_headless(ghidra_path, binary_path, output_json):
    suffix = ".bat" if os.name == "nt" else ""
    analyze_headless_path = os.path.join(ghidra_path, "support", f"analyzeHeadless{suffix}")
    
    if not os.path.exists(analyze_headless_path):
        print(f"[!] Error: Could not find analyzeHeadless at {analyze_headless_path}")
        print("Please check your GHIDRA_PATH.")
        sys.exit(1)

    temp_project_dir = tempfile.mkdtemp()
    project_name = "temp_cuckoo_project"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_name = "DecompileHeadless.java"

    absolute_script_path = os.path.join(script_dir, script_name)

    cmd = [
        analyze_headless_path,
        temp_project_dir,
        project_name,
        "-import", binary_path,
        "-scriptPath", script_dir,
        "-postScript", absolute_script_path, output_json,
        "-deleteProject"
    ]

    print(f"\n[*] Booting Ghidra Headless Analyzer for '{binary_path}'...")
    
    output_json = os.path.abspath(output_json) 
    cmd[-2] = output_json 

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            print(line.strip())
            
        process.wait()
        if process.returncode != 0:
            print(f"[!] Headless analyzer exited with code {process.returncode}")
            
    finally:
        shutil.rmtree(temp_project_dir, ignore_errors=True)


def refine_with_ollama(json_path, model_name, custom_instructions, output_dir):
    print(f"\n[*] Starting up Ollama with model: {model_name}...")
    
    with open(json_path, "r") as f:
        functions = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    full_decompiled_input = []
    for func_name, data in functions.items():
        raw_c = data.get("raw_c", "")
        full_decompiled_input.append(f"// --- FUNCTION: {func_name} ---\n{raw_c}\n")
    
    combined_code = "\n".join(full_decompiled_input)

    prompt = f"""You are analyzing a decompiled binary. Here is the entire Ghidra pseudo-code output containing all decompiled functions.
Please rewrite this pseudo-code into highly readable, clean, and compilable C code.
Remove the useless boilerplate functions, making sure the program works eaxctly the same!

USER INSTRUCTIONS: {custom_instructions}

Here is the pseudo-code (ALL FUNCTIONS):
{combined_code}
"""

    system_prompt = (
        "You must output ONLY a valid JSON object. The object must contain a single key 'content' "
        "whose value is a string containing the complete, refined C source code (including helper functions, "
        "global variables, structures, and headers as needed). Do not include markdown blocks, and do not "
        "provide conversational text outside the JSON."
    )

    total_chars = len(prompt) + len(system_prompt)
    estimated_tokens = total_chars // 4
    required_tokens = estimated_tokens + 4096 
    num_ctx = 4096
    while num_ctx < required_tokens:
        num_ctx *= 2
    num_ctx = min(num_ctx, 131072) 
    print(f"[*] Dynamically scaled context window (num_ctx) to: {num_ctx}")

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "num_ctx": num_ctx,
            "temperature": 0.1
        },
        "system": system_prompt
    }

    print("[*] Sending codebase to LLM for global refinement. This may take a moment...")

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        result = response.json()
        llm_reply = json.loads(result["response"]) 
        
        content = llm_reply.get("content")

        if content:
            full_path = os.path.join(output_dir, "decompiled_source.c")
            
            with open(full_path, "w", encoding="utf-8") as out_f:
                out_f.write("// decompiled by Cuckoo Decompiler\n")
                out_f.write(content.strip() + "\n")
            
            print(f"[+] Successfully saved reconstructed code to {full_path}!")
        else:
            print("[-] Error: Response did not contain 'content'.")
            
    except Exception as e:
        print(f"[-] Ollama failed on global refinement: {e}")
        
    print(f"\n[*] Cuckoo has finished! All refined files have been saved in the '{output_dir}' directory.")


if __name__ == "__main__":
    print("========================================")
    print("        CUCKOO DECOMPILER               ")
    print("========================================\n")

    ghidra_input = input(f"Enter path to Ghidra directory: ").strip()
    ghidra_path = ghidra_input
    
    if not os.path.exists(ghidra_path):
        print(f"[!] Ghidra path '{ghidra_path}' does not exist. Exiting.")
        sys.exit(1)

    binary_path = input("Enter path to the binary to analyze: ").strip()
    if not os.path.exists(binary_path):
        print("[!] File not found. Exiting.")
        sys.exit(1)

    output_dir = input("Enter output directory for reconstructed project [default: cuckoo_workspace]: ").strip()
    if not output_dir:
        output_dir = "cuckoo_workspace"

    print("\nAvailable Local Models:")
    print(" 1. qwen2.5-coder:32b (NASA Supercomputer)")
    print(" 2. qwen2.5-coder:14b (Heavy)")
    print(" 3. qwen2.5-coder:7b  (Standard)")
    print(" 4. qwen2.5-coder:1.5b (Fast)")
    
    model_choice = input("Select model (1-4) [default: 3]: ").strip()
    models = {
        "1": "qwen2.5-coder:32b",
        "2": "qwen2.5-coder:14b",
        "3": "qwen2.5-coder:7b",
        "4": "qwen2.5-coder:1.5b"
    }
    selected_model = models.get(model_choice, "qwen2.5-coder:7b")

    print("\nAny specific decompilation instructions?")
    print("  (for example: 'Organize graphics functions into src/graphics.c' or 'Create a header file for constants')")
    custom_instructions = input("Instructions (Press Enter to skip): ").strip()
    if not custom_instructions:
        custom_instructions = "Rename variables to standard meaningful names and format the code beautifully."

    output_json = "raw_ghidra_output.json"

    run_ghidra_headless(ghidra_path, binary_path, output_json)
    
    if os.path.exists(output_json):
        refine_with_ollama(output_json, selected_model, custom_instructions, output_dir)
    else:
        print("[!] Ghidra failed to output JSON data. Halting.")
