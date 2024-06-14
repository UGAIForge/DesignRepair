import re
import os
import json
import copy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

component_info = {
    "component_type": "", 
    "description": "", 
    "guidelines": {
        "docs_path": None,
        "hard": {
            "do": [],
            "dont": []
        },
        "soft": {}
    }, #-<> -![]
    # "accessbility": {
    #     "docs_path": None,
    #     "constraints": {
    #         "do": [],
    #         "dont": []
    #     },
    #     "general": {}
    # },
    # "specs": {
    #     "Measurements": "",
    #     "docs_path": ""
    # },
}


def find_matches(pattern, content, flags=0):
    return [(m.group(0), m.start(0)) for m in re.finditer(pattern, content, flags)]


def extract_content(content):

    # Extracting title
    header_matches = find_matches(r'^(#### .*|### .*|## .*|# .*)$', content, re.MULTILINE)
    # Extracting bulleted lists
    bullet_list_matches = find_matches(r'^\*(?!\*).+', content, re.MULTILINE)
    # Extracting ![] content
    image_alt_matches = find_matches(r'!\[(?!img\])([^]]+)\]', content)
    # Extracting lines that start with specific patterns like a., b., 1., etc.
    numbered_lists_matches = find_matches(r'^\d+\.\s.*$', content,  re.MULTILINE)
    # Extracting table rows
    table_matches_matches = find_matches(r'^\|.*\|$', content, re.MULTILINE)
    # Extracting 'checkDo' and the next relevant lines based on the given condition
    # checkdo_matches = find_matches(r'checkDo\s*\n(.*?)(?:\n|$)(?(1)(.*?\n|)|(?:\n(.*?\n.*?)\n|))', content)
    checkdo_matches = find_matches(r'checkDo\s*(.*?)(?:\n|$)(?(1)(.*?\n|)|(?:\n(.*?\n.*?)\n|))', content)
    # Extracting 'closeDon’t' and the next relevant lines based on the given condition
    closedont_matches = find_matches(r'closeDon’t\s*(.*?)(?:\n|$)(?(1)(.*?\n|)|(?:\n(.*?\n.*?)\n|))', content)

    # Merge all matched results and sort them based on their position in the original document
    all_matches = sorted(header_matches + bullet_list_matches + image_alt_matches + numbered_lists_matches + table_matches_matches + checkdo_matches + closedont_matches, key=lambda x: x[1])

    # Extract the results after sorting
    sorted_results = [match[0] for match in all_matches]

    # Count the number of matches for each type
    list_count = len(bullet_list_matches) + len(numbered_lists_matches)
    image_alt_count = len(image_alt_matches)
    table_count = len(table_matches_matches)
    checkdo_count = len(checkdo_matches)
    closedont_count = len(closedont_matches)

    return sorted_results, list_count, image_alt_count, table_count, checkdo_count, closedont_count


def process_comp_guidelines(file_path, component_info, docount, dontcount, guidelinecount):

    with open(file_path, 'r') as file:
        content = file.read()

        # Extracting all level headlines and their content
        pattern = r'(#+)\s*(.*?)\n(.*?)\n(?=\n#+ |\Z)'
        matches = re.findall(pattern, content, flags=re.DOTALL)

        parsed_content = {}

        current_h2_key = None
        current_h3_key = None

        for match in matches:
            level, heading, section_content  = match
            heading_key = heading.strip()
            
            # remove <video> tag content
            section_content  = re.sub(r'<video.*?>.*?</video>', '', section_content , flags=re.DOTALL)
            # remove link
            section_content  = re.sub(r'\(https?://\S+\)', '', section_content )

            # Extracting and removing "checkDo" and "closeDon’t"
            do_pattern = r'checkDo\s*(.*?)(?:\n|$)(?(1)(.*?\n|)|(?:\n(.*?\n.*?)\n|))'
            dont_pattern = r'closeDon’t\s*(.*?)(?:\n|$)(?(1)(.*?\n|)|(?:\n(.*?\n.*?)\n|))'

            do_content = re.findall(do_pattern, section_content, flags=re.DOTALL)
            dont_content = re.findall(dont_pattern, section_content, flags=re.DOTALL)

            section_content = re.sub(do_pattern, '', section_content, flags=re.DOTALL)
            section_content = re.sub(dont_pattern, '', section_content, flags=re.DOTALL)

            section_content  = section_content.strip() 

            if level == '##':
                current_h2_key = heading_key
                current_h3_key = None
                # use setdefault() keep staying in current_h2_key
                component_info["guidelines"]["soft"].setdefault(current_h2_key, {})
                component_info["guidelines"]["soft"][current_h2_key].setdefault("general", {})
                # 
                component_info["guidelines"]["soft"][current_h2_key]["soft"] = {}
                component_info["guidelines"]["soft"][current_h2_key]["soft"] = section_content
                #save index
                # component_info["guidelines_indexs"].setdefault(current_h2_key, {})
                # component_info["guidelines_indexs"][current_h2_key]["general"] = {}
                guidelinecount += 1

            elif level == '###' and current_h2_key is not None:
                current_h3_key = heading_key
                component_info["guidelines"]["soft"][current_h2_key][current_h3_key] = {}
                component_info["guidelines"]["soft"][current_h2_key][current_h3_key] = section_content
                #save index
                # component_info["guidelines_indexs"][current_h2_key][current_h3_key] = {}
                guidelinecount += 1

            elif level == '####' and current_h3_key is not None:
                component_info["guidelines"]["soft"][current_h2_key][current_h3_key] += level + ' ' + heading + '\n' + section_content + '\n'

            # Save the extracted content
            if do_content:
                for item in do_content:
                    docount += 1
                    concatenated_str = ''.join(item)
                    if concatenated_str.endswith('\n'):
                        concatenated_str = concatenated_str[:-1]
                    combined_string = current_h2_key + "#" + str(current_h3_key) + "#" + concatenated_str
                    component_info["guidelines"]["hard"]["do"].extend([combined_string])
                
                # component_info["guidelines"]["constraints"]["do"].extend([current_h2_key, current_h3_key, do_content])
            if dont_content:
                for item in dont_content:
                    dontcount += 1
                    concatenated_str = ''.join(item)
                    if concatenated_str.endswith('\n'):
                        concatenated_str = concatenated_str[:-1]
                    combined_string = current_h2_key + "#" + str(current_h3_key) + "#" + concatenated_str
                    component_info["guidelines"]["hard"]["dont"].extend([combined_string])
                
                # component_info["guidelines"]["constraints"]["dont"].extend([current_h2_key, current_h3_key, dont_content])

    return component_info, docount, dontcount, guidelinecount



def analyze_guidelines(component_info):
    h2_keys = component_info["guidelines"]["soft"].keys()

    analysis_results = {}
    for h2_key in h2_keys:
        sub_items = component_info["guidelines"]["soft"][h2_key]
        analysis_results[h2_key] = {
            "sub_item_count": len(sub_items),
            "sub_item_lengths": {sub_item_key: len(sub_item_content) for sub_item_key, sub_item_content in sub_items.items()}
        }
    return analysis_results




def plot_h2_key_analysis(aggregated_h2_data):
    data = {
        "h2_key": [],
        "total_sub_item_count": [],
        "average_length": [],
        "min_length": [],
        "max_length": []
    }

    for h2_key, values in aggregated_h2_data.items():
        lengths = [length for sublist in values["sub_item_lengths"].values() for length in sublist]
        average_length = sum(lengths) / len(lengths) if lengths else 0
        non_zero_lengths = [length for length in lengths if length > 0]
        min_length = min(non_zero_lengths) if non_zero_lengths else 0
        max_length = max(lengths) if lengths else 0

        data["h2_key"].append(h2_key)
        data["total_sub_item_count"].append(values["total_sub_item_count"])
        data["average_length"].append(average_length)
        data["min_length"].append(min_length)
        data["max_length"].append(max_length)
        # print(f"H2 Key: {h2_key}, Total Sub Item Count: {values['total_sub_item_count']}, Average Length: {average_length}, Min Length: {min_length}, Max Length: {max_length}")

    df = pd.DataFrame(data)

    # max 5
    df_top5 = df.nlargest(5, 'total_sub_item_count')
    top5_keys = df_top5['h2_key'].tolist()
    print(top5_keys)

    # other
    other_data = df[~df['h2_key'].isin(top5_keys)].sum(numeric_only=True)
    other_data['h2_key'] = 'Other'
    # 使用 pd.concat 而不是 append
    df_top5_and_other = pd.concat([df_top5, pd.DataFrame([other_data])], ignore_index=True)

    plt.figure(figsize=(10, 6))
    plt.title("General Component Aspects Count", fontsize=16, fontweight='bold')
    bars = plt.bar(df_top5_and_other['h2_key'], df_top5_and_other['total_sub_item_count'], color='skyblue')
    plt.ylabel('Total Guidelines Count', fontsize=12)
    # Adding gridlines for better readability
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), va='bottom', ha='center', fontsize=10)
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.title("Average Guidelines Length", fontsize=16, fontweight='bold')
    x = range(len(df_top5))
    
    err_lower = np.clip(df_top5['average_length'] - df_top5['min_length'], 0, None)
    err_upper = np.clip(df_top5['max_length'] - df_top5['average_length'], 0, None)
    err = [err_lower, err_upper]

    bars = plt.bar(x, df_top5['average_length'], yerr=err, align='center', alpha=0.4, ecolor='grey', capsize=5, color='coral')
    # plt.xlabel('H2 Key', fontsize=12)
    plt.ylabel('Length', fontsize=12)
    plt.xticks(x, df_top5['h2_key'])
    # Adding gridlines for better readability
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center', fontsize=10)

    plt.tight_layout()
    plt.legend(['Average Length with Min/Max Range'])
    plt.show()



def plot_constraints_analysis(constraints_count):
    # Specific keys to consider
    specific_keys = ['Behavior', 'Usage', 'Anatomy', 'Placement', 'Responsive layout']

    # specific_keys=['Interaction & style', 'Use cases', 'Keyboard navigation', 'Labeling elements', 'Initial focus', 'Visual indicators']

    filtered_counts = {key: {'do': 0, 'dont': 0} for key in specific_keys}
    filtered_counts['Other'] = {'do': 0, 'dont': 0}  # Additional category for 'Other'

    # Filtering and re-categorizing the data
    for key, value in constraints_count.items():
        if key in specific_keys:
            filtered_counts[key]['do'] += value['do']
            filtered_counts[key]['dont'] += value['dont']
        else:
            filtered_counts['Other']['do'] += value['do']
            filtered_counts['Other']['dont'] += value['dont']

    labels = list(filtered_counts.keys())
    do_counts = [value['do'] for value in filtered_counts.values()]
    dont_counts = [value['dont'] for value in filtered_counts.values()]

    # Adjusting the figure size
    plt.figure(figsize=(10, 6))

    # New color scheme for publication
    # colors_do = ['#4daf4a', '#377eb8', '#ff7f00', '#984ea3', '#e41a1c', '#ffff33']  # Set of distinct colors for 'Do'
    # colors_dont = ['#a6cee3', '#1f78b4', '#fdbf6f', '#cab2d6', '#fb9a99', '#b2df8a']  # Different set for 'Don’t'
    colors_do = ['#ffff33']
    colors_dont = ['#b2df8a']

    x = range(len(labels))
    bars_do = plt.bar(x, do_counts, width=0.4, color=colors_do, label='Do', align='center')
    bars_dont = plt.bar(x, dont_counts, width=0.4, color=colors_dont, label='Don’t', align='edge')

    # Adding values on top of the bars
    for bar in bars_do + bars_dont:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, int(height), ha='center', va='bottom', fontsize=9)

    # Font size and style adjustments
    # plt.xlabel('Categories', fontsize=12)
    plt.ylabel('Count', fontsize=12)
    plt.title('Do and Don’t Constraints Count', fontsize=16, fontweight='bold')
    plt.xticks(x, labels, fontsize=10)
    plt.yticks(fontsize=10)

    # Adding gridlines for better readability
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Adjusting the legend
    plt.legend(fontsize=12)
    # Ensuring the plot is spaced adequately
    plt.tight_layout()
    # Save the plot with high resolution
    plt.savefig('constraints_analysis_plot.png', dpi=300)
    plt.show()



def get_description(file_path):
    descriptions = {}
    with open(file_path, 'r') as file:
        docs = file.read()
        sections = re.split(r'\n#+ ', docs)
        for section in sections:
            if not section.startswith(' \n'):
                # Split the section into the heading and the content
                heading, *content = section.split('\n\n', 1)
                # Remove "##" and strip whitespace from the heading
                key = heading.strip().lower()
                # Join the content back together if it was split
                content = '\n'.join(content).strip()
                # Add the heading and content to the dictionary
                descriptions[key] = content
    return descriptions





def comp_main(file_path, description_path):
    directories = ["Components"]
    components_list = []
    docount = 0
    dontcount = 0
    guidelinecount = 0
    aggregated_h2_data = {}
    constraints_count = {}

    descriptions = get_description(description_path)

    for directory in directories:
        for root, dirs, files in os.walk(os.path.join(file_path, directory)):
            for file in files:
                if file.endswith("_guidelines.md"):
                # if file.endswith("_accessibility.md"):
                    # init
                    new_component = copy.deepcopy(component_info)
                    new_component["component_type"] = file.split("_")[0].replace("-", " ")
                    new_component["guidelines"]["docs_path"] = file

                    # get description
                    if new_component["component_type"] in descriptions.keys():
                        new_component["description"] = descriptions[new_component["component_type"]]
                    elif new_component["component_type"][:-1] in descriptions.keys(): # remove "s"
                        new_component["description"] = descriptions[new_component["component_type"][:-1]]
                    else:
                        print(new_component["component_type"], "no description found")
                    
                    # structure guidelines
                    new_component, docount, dontcount, guidelinecount = process_comp_guidelines(os.path.join(root, file), new_component, docount, dontcount, guidelinecount)
                    components_list.append(new_component)

                    # Analyze and aggregate guidelines
                    analysis_results = analyze_guidelines(new_component)
                    for h2_key, data in analysis_results.items():
                        if h2_key not in aggregated_h2_data:
                            aggregated_h2_data[h2_key] = {"total_sub_item_count": 0, "sub_item_lengths": {}}
                        aggregated_h2_data[h2_key]["total_sub_item_count"] += data["sub_item_count"]
                        for sub_item_key, length in data["sub_item_lengths"].items():
                            aggregated_h2_data[h2_key]["sub_item_lengths"].setdefault(sub_item_key, []).append(length)

                    # Analyze and aggregate constraints
                    h2_keys = new_component["guidelines"]["soft"].keys()
                    for h2_key in h2_keys:
                        do_count = sum(h2_key in item for item in new_component["guidelines"]["hard"]["do"])
                        dont_count = sum(h2_key in item for item in new_component["guidelines"]["hard"]["dont"])
                        constraints_count[h2_key] = constraints_count.get(h2_key, {'do': 0, 'dont': 0})
                        constraints_count[h2_key]['do'] += do_count
                        constraints_count[h2_key]['dont'] += dont_count


    plot_h2_key_analysis(aggregated_h2_data)
    plot_constraints_analysis(constraints_count)

    print(docount, dontcount, guidelinecount, len(components_list))
    
    with open("components_knowledge_base.json", "w") as outfile:
        json.dump(components_list, outfile, indent=4)

    return



if __name__ == "__main__":
    file_path = r"doc_path"
    description_path = r"description_path"
    comp_main(file_path, description_path)