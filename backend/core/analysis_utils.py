import os
import time
from core.prompts import analysis_system
from core.prompts import regenerate_file_content, merge_suggestions, regenerate_file_content_multi
from core.llm import stream_openai_response
from pydantic import BaseModel
from typing import List
import json
from collections import defaultdict

class RepairedCode(BaseModel):
    filename_with_path: str
    repaired_code_file: str


class RepairedCodeSchema(BaseModel):
    repaired_code_files: List[RepairedCode]


class AnalysisComponent(BaseModel):
    bad_design_code_filename: str
    bad_design_code: str
    detailed_reference_from_guidelines: str
    suggestion_fix_code: str


class AnalysisComponentSchema(BaseModel):
    design_suggestion: List[AnalysisComponent]


def generate_analysis_report():
    pass

async def get_response(prompt_messages, functions_schema=None, temperature=0.0, model=None):
    async def process_chunk(content: str):
        pass

    if not os.environ.get("OPENAI_API_KEY"):
        raise Exception("OpenAI API key not found")
    
    completion = await stream_openai_response(
        messages=prompt_messages,
        temperature=temperature,
        functions=functions_schema,
        api_key=os.environ.get("OPENAI_API_KEY"),
        callback=lambda x: process_chunk(x),
        base_url=None,
        model=model,
    )
    return completion


def assemble_regenerate_prompt(og_prompt, file_content, suggestions):

    regenerate_file_content_prompt = og_prompt.replace("{file_content}", file_content)
    regenerate_file_content_prompt = regenerate_file_content_prompt.replace("{suggestions}", suggestions)
    print ("------REGENERATE FILE-------")
    prompt = [
        {
            "role": "system",
            "content": analysis_system,
        },
        {
            "role": "user",
            "content": regenerate_file_content_prompt
        }
    ]
    return prompt


def assemble_prompt_with_function(og_prompt, file_content, suggestions, function_schema=RepairedCodeSchema.schema()):

    regenerate_file_content_prompt = og_prompt.replace("{file_content}", file_content)
    regenerate_file_content_prompt = regenerate_file_content_prompt.replace("{suggestions}", suggestions)
    print ("------REGENERATE FILE-------")
    prompt = [
        {
            "role": "system",
            "content": analysis_system,
        },
        {
            "role": "user",
            "content": regenerate_file_content_prompt
        }
    ]
    
    functions=[
        {
          "name": "repair_to_full_code",
          "description": "Repair content of files to full code",
          "parameters": function_schema
        },
    ]
    return prompt, functions


def save_code_to_file(code, filename):
    try:
        with open(filename, 'w') as file:
            file.write(code)
        print(f"Code saved to {filename} successfully.")
    except Exception as e:
        print(f"Error occurred while saving the code to {filename}: {e}")



async def repair_to_full_code(ctx, comp_suggestions, property_suggestions, save_path, sub_name=None):

    ### regenerate code(refer aider)
    suggestions = str(comp_suggestions) + str(property_suggestions)

    regenerate_prompt = assemble_regenerate_prompt(regenerate_file_content, ctx.file_content, suggestions)
    print(regenerate_prompt)
    completion = await get_response(regenerate_prompt)
    # print(completion)

    # save code to file
    # save_dir = ctx.file_dir.replace("orginal", "generated")
    # if not os.path.exists(save_dir):
    #     os.makedirs(save_dir)

    # timestamp = int(time.time() * 1000)
    # file_name = str(timestamp) + '.' + ctx.file_name.split(".")[1]
    # save_name = os.path.join(save_dir, file_name)
    if sub_name:
        save_name = sub_name + ctx.file_name
    else:
        save_name = (ctx.file_name)

    save_path = os.path.join(save_path, save_name)
    save_code_to_file(completion, save_path)
    print("-----Write to file: " + save_name + " -----")



async def repair_to_full_code_multi_once(ctx, comp_suggestions, property_suggestions, save_path, sub_name=None):

    ### regenerate code(refer aider)
    suggestions = str(comp_suggestions) + str(property_suggestions)

    regenerate_prompt, regenerate_schema = assemble_prompt_with_function(regenerate_file_content_multi, ctx.file_content, suggestions)
    print(regenerate_prompt)
    completion = await get_response(regenerate_prompt, regenerate_schema)

    if "repaired_code_files" in completion:
        completion_json = json.loads(completion)
        repaired_code_files = completion_json['repaired_code_files'] # remove duplicates
    else:
        raise Exception("No components found in results")
    for code in repaired_code_files:
        print(code['filename_with_path'])

    for code in repaired_code_files:
        save_name = code['filename_with_path']
        save_content = code['repaired_code_file']
        save_path = os.path.join(save_path, save_name)
        save_dir= os.path.dirname(save_path)
        #save path, remove filename
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            save_code_to_file(save_content, save_path)
            print("-----Write to file: " + save_name + " -----")



async def repair_to_full_code_multi(ctx, comp_suggestions, property_suggestions, save_path, sub_name=None):

    ### regenerate code(refer aider)
    suggestions = str(comp_suggestions) + str(property_suggestions)

    merge_prompt, merge_schema = assemble_prompt_with_function(merge_suggestions, ctx.file_content, suggestions, AnalysisComponentSchema.schema())
    completion = await get_response(merge_prompt, merge_schema)

    if "design_suggestion" in completion:
        completion_json = json.loads(completion)
        merged_suggestion = completion_json['design_suggestion']
    else:
        raise Exception("No suggestions found in results")

    # log
    log_file = os.path.join(save_path, "repair_all_log.json")
    # with open(log_file, "a") as file:
        # file.write("merged suggestions:" + formatted_json + "\n\n")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(completion_json, f, indent=4, ensure_ascii=False)

    # refer filename merge suggestions
    suggestions_by_file = defaultdict(list)
    for suggestion in merged_suggestion:
        filename = suggestion['bad_design_code_filename']
        suggestions_by_file[filename].append(suggestion)

    # split repair files
    for filename, suggestions in suggestions_by_file.items():
        print(f"Suggestions for {filename}:")
        regenerate_prompt, regenerate_schema = assemble_prompt_with_function(regenerate_file_content_multi, ctx.file_content, str(suggestions), RepairedCode.schema())
        completion = await get_response(regenerate_prompt, regenerate_schema)
        completion_json = json.loads(completion)

        save_name = completion_json['filename_with_path']
        save_content = completion_json['repaired_code_file']
        save_file = os.path.join(save_path, save_name)
        save_dir= os.path.dirname(save_file)
        #save path
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        save_code_to_file(save_content, save_file)
        print("-----Write to file: " + save_name + " -----")