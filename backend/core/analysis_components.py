import os
import re
import jinja2
import json
import asyncio
import copy
import time
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List

# from core.approximate_costs import approximate_costs
from core.prompts import analysis_system
from core.prompts import get_related_components_prompt_web_page, get_related_components_prompt_web_page_simpler, get_related_components_prompt_web_page_complex
from core.prompts import get_related_components_prompt_library
from core.prompts import components_analysis_content
from core.analysis_utils import get_response

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Define the schema using
class ComponentSchema(BaseModel):
    components: List[str]

class AnalysisComponent(BaseModel):
    bad_design_code_filename: str
    bad_design_code: str
    detailed_reference_from_guidelines: str
    suggestion_fix_code: str

class AnalysisComponentSchema(BaseModel):
    bad_component_design: List[AnalysisComponent]


def extract_components_list(comp_guidelines):
    components_list = []
    for comp in comp_guidelines:
        components_list.append(comp['component_type'])
    return components_list        


test_content = '''{
  "bad_component_design": [
    {
      "bad_design_code": "<Avatar className=\"shrink-0\">",
      "detailed_reference_from_guidelines": "Component: badges\nAnatomy#Container#Badges have fixed positions. Don't change the position of the badge arbitrarily or place the badge over the icon.",
      "suggestion_fix_code": "<Avatar className=\"shrink-0\" style={{ position: 'static' }}>"
    },
    {
      "bad_design_code": "<span className=\"text-sm text-gray-500 dark:text-gray-400\">{email.tags.join(', ')}</span>",
      "detailed_reference_from_guidelines": "Component: badges\nAnatomy#Label text#Don't let the badge get cut off 
or collide with another element",
      "suggestion_fix_code": "<span className=\"text-sm text-gray-500 dark:text-gray-400 truncate\">{email.tags.join(', ')}</span>"
    },
    {
      "bad_design_code": "<Checkbox />",
      "detailed_reference_from_guidelines": "Component: checkbox\nUsage#None#Checkboxes let users select one or more options from a list. A parent checkbox allows for easy selection or deselection of all items.",
      "suggestion_fix_code": "<Checkbox aria-label=\"Select email\" />"
    },
    {
      "bad_design_code": "<button className=\"p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300\">\n  <MoreVertical className=\"h-5 w-5\" />\n</button>",
      "detailed_reference_from_guidelines": "Component: icon buttons\nBehavior#Selection#Don't use toggle icon buttons for actions that don't have a selected state, such as an icon button for an overflow menu",
      "suggestion_fix_code": "<button aria-label=\"More actions\" className=\"p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300\">\n  <MoreVertical className=\"h-5 w-5\" />\n</button>"
    }
  ]
}'''

# TODO - Test segment code into chunks, and for each chunk find the relevant components in the library
def assemble_get_web_components_prompt(file_content, sys_prompt):
    print ("------GET WEB COMPONENTS-------")
    prompt = [
        {
            "role": "system",
            "content": analysis_system,
        },
        {
            "role": "user",
            "content": sys_prompt.replace("{file_content}", file_content)
        }
    ]
    functions=[
        {
          "name": "get_web_page_components",
          "description": "Get all the components name in the web page",
          "parameters": ComponentSchema.schema()
        },
    ]
    return prompt, functions


def assemble_get_library_components_prompt(page_response, components_list):
    print ("------GET LIBRARY COMPONENTS-------")
    prompt =[
        {
            "role": "system",
            "content": analysis_system,
        },
        { 
            "role": "user",
            "content": get_related_components_prompt_library.replace("{components_list}", str(components_list))
        },
        {
            "role": "user",
            "content": "You have the following list of components in the web page:\n" 
                        + page_response + "\n" +
                        "Get all the corresponding components name in library.\n"
        }]

    functions=[
        {
          "name": "get_library_components",
          "description": "Get all the corresponding components name in library",
          "parameters": ComponentSchema.schema()
        },
    ]
    return prompt, functions


def assemble_components_analysis_prompt(file_content, related_guidelines):
    print ("-----ANALYZE COMPONENTS-------")
    def get_soft_constraints(related_guidelines):
        soft_constraints = ""
        for item in related_guidelines:
            # Extract the name of the component
            component_name = item.get('component_type', 'Unnamed Component')
            guidelines = item.get('guidelines', {}).get('soft', {})

            # Append component name
            soft_constraints += f"Component: {component_name}\n"

            for section, content in guidelines.items():
                soft_constraints += f"{section}:\n"
                for sub_section, sub_content in content.items():
                    soft_constraints += f"- {sub_section}: {sub_content}\n"

            soft_constraints += "\n\n"  # Add a newline for separation between items

        return soft_constraints.strip()

    def get_hard_constraints(related_guidelines):
        hard_constraints = ""
        for item in related_guidelines:
            # Extract the name of the component
            component_name = item.get('component_type', 'Unnamed Component')

            constraints = item['guidelines'].get('hard', {})
            do_constraints = constraints.get('do', [])
            dont_constraints = constraints.get('dont', [])

            # Append component name
            hard_constraints += f"Component: {component_name}\n"

            # Append 'Do' and 'Don't' constraints
            if do_constraints:
                hard_constraints += "Do:\n" + "\n".join(do_constraints)
            if dont_constraints:
                hard_constraints += "\nDon't:\n" + "\n".join(dont_constraints)

            hard_constraints += "\n\n"  # Add extra newline for separation between components

        return hard_constraints.strip()
    
    components_analysis_content_prompt = components_analysis_content
    components_analysis_content_prompt = components_analysis_content_prompt.replace("{file_content}", file_content)
    # components_analysis_content_prompt = components_analysis_content_prompt.replace("{soft_constraints}", get_soft_constraints(related_guidelines))
    components_analysis_content_prompt = components_analysis_content_prompt.replace("{hard_constraints}", get_hard_constraints(related_guidelines))

    prompt =[
        {
            "role": "system",
            "content": analysis_system,
        },
        { 
            "role": "user",
            "content": components_analysis_content_prompt
        },
        {
            "role": "system",
            "content": "Please respond ONLY with valid json that conforms to this pydantic json_schema: {model_class.schema_json()}.\n"
        }]

    functions=[
        {
          "name": "analyze_components",
          "description": "analyze ",
          "parameters": AnalysisComponentSchema.schema()
        },
    ]
    return prompt, functions



def get_related_comp_guidelines(need_list, comp_guidelines, components_list):
    related_guidelines = []

    for needed_comp in need_list:
        if needed_comp.lower() in components_list:
            print("Found component in library: " + needed_comp)
            for single_guideline in comp_guidelines:
                if single_guideline['component_type'] == needed_comp:
                    related_guidelines.append(single_guideline)
                    break
    return related_guidelines
     

   
async def analysis_components(ctx, comp_guidelines):
    components_list = extract_components_list(comp_guidelines)
    # print(str(components_list))
    
    # define log file
    folder_name = ctx.file_name.split(".")[0]
    log_file = os.path.join(folder_name, "components.log")

    # get web simpler components
    get_web_components_prompt, web_components_schema = assemble_get_web_components_prompt(ctx.file_content, get_related_components_prompt_web_page_simpler)
    completion_simpler = await get_response(get_web_components_prompt, web_components_schema, model="gpt-4-turbo-2024-04-09")
    print(completion_simpler)
    completion_simpler_list = list(json.loads(completion_simpler)['components'])
    if len(completion_simpler_list) >= 10:
        get_web_components_prompt.append(
        {
            "role": "user",
            "content": "Don't include all the components! Only the most relevant ones in the webpage."
        }
        )
        completion_simpler = await get_response(get_web_components_prompt, web_components_schema, model="gpt-4-turbo-2024-04-09")
        print("second try",completion_simpler)
        completion_simpler_list = list(json.loads(completion_simpler)['components'])
    with open(log_file, "a") as file:
        file.write("simpler components" + completion_simpler + "\n")


    get_web_components_prompt, web_components_schema = assemble_get_web_components_prompt(ctx.file_content, get_related_components_prompt_web_page_complex)
    completion_complex = await get_response(get_web_components_prompt, web_components_schema, model="gpt-4-turbo-2024-04-09")
    print(completion_complex)
    completion_complex_list = list(json.loads(completion_complex)['components'])
    if len(completion_complex_list) >= 5:
        get_web_components_prompt.append(
        {
            "role": "user",
            "content": "Don't include all the components! Only the most relevant ones."
        }
        )
        completion_complex = await get_response(get_web_components_prompt, web_components_schema, model="gpt-4-turbo-2024-04-09")
        print("second try",completion_complex)
        completion_complex_list = list(json.loads(completion_complex)['components'])
        if len(completion_complex_list) >= 15:
            completion_complex_list = []
        with open(log_file, "a") as file:
            file.write("complex components" + completion_complex + "\n")
            
    components_lists = completion_simpler_list  + completion_complex_list

    # get library components
    get_library_components_prompt, lib_components_schema = assemble_get_library_components_prompt(str(components_lists), components_list)
    completion = await get_response(get_library_components_prompt, lib_components_schema, model="gpt-4-turbo-2024-04-09")
    print(completion)
    with open(log_file, "a") as file:
        file.write("library components" + completion + "\n")

    # extract components
    my_list = []
    if "components" in completion:
        completion_json = json.loads(completion)
        my_list = list(set(completion_json['components'])) # remove duplicates
    else:
        raise Exception("No components found in results")
    print(my_list)
    with open(log_file, "a") as file:
        file.write("simpler components" + completion + "\n")

    # get related components guidelines
    related_guidelines = get_related_comp_guidelines(my_list, comp_guidelines, components_list)

    # get components analysis prompt
    components_analysis_prompt, components_analysis_schema = assemble_components_analysis_prompt(ctx.file_content, related_guidelines)
    # print(components_analysis_prompt)
    # completion = await get_response(components_analysis_prompt, components_analysis_schema, 0.2)
    completion = await get_response(components_analysis_prompt, components_analysis_schema)
    # print(completion)
    with open(log_file, "a") as file:
        file.write(completion + "\n")

    return completion