import os
import json
from pydantic import BaseModel
from typing import Optional
import asyncio
import csv
from core.analysis_components import analysis_components
from core.analysis_groups import analysis_groups
from core.analysis_utils import repair_to_full_code



class FileContext(BaseModel):
    file_name: str
    file_dir: str
    file_content: str
    root_directory: str = None
    example_content: Optional[str] = None



def process_file(file_dir, file_name, root_directory=None, example=None):
    """
    processes files
    """
    file_path = os.path.join(file_dir, file_name)
    with open(file_path, "r") as file:
        file_content = file.read()

    example_content = None
    if example:
        example_path = os.path.join(root_directory, "./" + example)
        try:
            with open(example_path, "r") as example_file:
                example_content = example_file.read()
        except FileNotFoundError:
            print(f"Could not find example file at {example_path}")
            return

    ctx = FileContext(
        file_name=file_name,
        file_dir=file_dir,
        file_content=file_content,
        root_directory=root_directory,
        example_content=example_content,
    )
    return ctx



def load_component_guidelines(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
    


def load_system_level_guidelines(file_path):
    data_by_property_and_constraint = {}  # based on property constraint

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # print(row[0:5])
            if row[0] == 'material_design_section':
                continue
            if len(row) != 6:
                print(f"Invalid row number: {row}")
                continue

            # check system_design_aspect
            if row[1] not in ["Structure","Flow","Layout","Implement","Label","Text","Color","Typography","Shape","Icon","Elevation"]:
                print(f"Invalid row High_Level_Subclasses: {row}")
                continue

            # check property
            if row[2] not in ["Group", "Clickable", "Spacing", "Platform","Label","Text","Color"]:
                print(f"Invalid row property: {row}")
                continue

            # check constraint
            if row[3] not in ["soft","hard"]:
                print(f"Invalid row constraint: {row}")
                continue

            # init
            if row[2] not in data_by_property_and_constraint:
                data_by_property_and_constraint[row[2]] = {"soft": [], "hard": []}

            # save by property constraint
            data_by_property_and_constraint[row[2]][row[3]].append(row)

    return data_by_property_and_constraint


if __name__ == "__main__":
    file_dir = r"..\examples"
    file_name = "example1.tsx"

    comp_guidelines_path = r"..\library\components_knowledge_base.json"
    system_level_guidelines_path = r"..\library\system_design_knowledge_base.csv"

    # page to be tested
    pageurl = "http://localhost:3000"
    
    ctx = process_file(file_dir, file_name)
    
    # make log folder
    folder_name = ctx.file_name.split(".")[0]
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    
    # a.components detect and repair
    comp_guidelines = load_component_guidelines(comp_guidelines_path)
    comp_suggestions = asyncio.run(analysis_components(ctx, comp_guidelines))
    asyncio.run(repair_to_full_code(ctx, comp_suggestions, "", folder_name, 'comp_'))

    # b.groups detect and repair
    system_level_guidelines = load_system_level_guidelines(system_level_guidelines_path)
    property_suggestions = asyncio.run(analysis_groups(ctx, system_level_guidelines, pageurl))
    asyncio.run(repair_to_full_code(ctx, "", property_suggestions, folder_name, 'property_'))

    # c.repair
    asyncio.run(repair_to_full_code(ctx, comp_suggestions, property_suggestions, folder_name, ''))

    