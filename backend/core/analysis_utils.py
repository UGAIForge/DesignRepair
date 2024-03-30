import os
import time
from core.prompts import analysis_system
from core.prompts import regenerate_file_content
from core.llm import stream_openai_response

def generate_analysis_report():
    pass


async def get_response(prompt_messages, functions_schema=None, temperature=0.0):
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
    )
    return completion



def assemble_regenerate_prompt(file_content, suggestions):

    regenerate_file_content_prompt = regenerate_file_content.replace("{file_content}", file_content)
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

    regenerate_prompt = assemble_regenerate_prompt(ctx.file_content, suggestions)
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
