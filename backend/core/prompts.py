
analysis_system = """
You are an expert frontend developer. 
Your task is to analyze the web page and provide suggestions to fix the bad design.
"""


get_related_components_prompt_web_page = """
Here is the web page you need to analyze:
'''{file_content}'''
    -Summarize the web page, break it down into smaller components.
    Extract all the components from the web page, save it in a list {"components"}.
"""


get_related_components_prompt_library = """
Multiple component guidelines can be used while checking the component in order to help find the mistake and improve.
You have the following list of library components: 
'''{components_list}'''
    -Map web page components you got, to the corresponding library components. save it in a list {"components"}.

    Notice, the web page component name and the library component name do not correspond exactly. 
    Tip: You can decompose components or combine components to find the corresponding components in the library.
    Please try your best to find it.
"""

components_soft_analysis_content = """

####
Here is the current content of the files you need to analyze:
'''{file_content}'''

####
Multiple component guidelines can be used while checking the component in order to help find the mistake and improve.
[Anatomy, Behavior, Placement, Responsive layout, Usage] are the most common component guidelines you need to check.

Here are the related guidelines:

Here are the general guidelines you can use, we name it "soft constraints",
REMEMBER THIS IS NOT MANDATORY, REGARDED AS OPTIONAL.
'''{soft_constraints}'''

"""


components_analysis_content = """

####
Here is the current content of the files you need to analyze:
'''{file_content}'''

####
Multiple component guidelines can be used while checking the component in order to help find the mistake and improve.
[Anatomy, Behavior, Placement, Responsive layout, Usage] are the most common component guidelines you need to check.

Here are the related guidelines:

Here are the guidelines you must follow, we name it "hard constraints",
REMEMBER THIS IS MANDATORY, ONCE YOU FIND A BAD DESIGN NOT FOLLOWING THE GUIDELINE, YOU MUST FIX IT. FIND AS MANY BAD DESIGN AS POSSIBLE.
'''{hard_constraints}'''

Here are the general guidelines you can use, we name it "soft constraints",
REMEMBER THIS IS NOT MANDATORY, REGARDED AS OPTIONAL.
'''{soft_constraints}'''

####
Use the above instructions to analyze the supplied files, and provide detailed suggestions to fix all the bad design.
To suggest changes to a file you MUST return the bad design code snippet, reference_components_name, detailed reference guidelines, and fix code suggestion. in the json format.
'''{bad_design_code}'''
'''{detailed_reference_from_guidelines}'''
'''{suggestion_fix_code}'''
find as many bad design as possible.
"""


# - For images, use placeholder images from https://placehold.co and include a detailed description of the image in the alt text so that an image generation AI can generate the image later.
regenerate_file_content = """
To suggest changes to a file you MUST return the entire content of the updated file.

Here is the current content of the files you need to modify:
'''{file_content}'''

Here are the bad design code snippet, detailed reference guidelines, and fix code suggestion.
'''{suggestions}'''

- There may be conflicts between bad design code snippets. Please try your best to merge the conflicts to give the best improvement results.
- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.

Remember, You are an expert frontend developer, and frontend designer. 
Only focusing on the most important aspect to improve.
You MUST make the color, layout in beatiful design, and readability!!!

Return only the full code you improved. 
Do not include markdown "```" or "```jsx" at the start or end.
Do not include markdown "```" or "```jsx" at the start or end.
Do not include markdown "```" or "```jsx" at the start or end.
"""

property_analysis_content = """
####
Here is the current content of the files you need to analyze:
'''{file_content}'''

####
Here is the detailed properties of '''{property_type}''' we extracted from the above web page you need to analyze:
'''{properties}'''

####
Multiple High level guidelines related to '''{property_type}''' properties can be used while checking in order to help find the mistake and improve.
'''{property_type}''' is the most important aspect you need to check.

Here are the related guidelines:

Here are the guidelines you must follow, we name it "hard constraints",
REMEMBER THIS IS MANDATORY, ONCE YOU FIND A BAD DESIGN NOT FOLLOWING THE GUIDELINE, YOU MUST FIX IT. FIND AS MANY BAD DESIGN AS POSSIBLE.
'''{hard_constraints}'''

Here are the general guidelines you can use, we name it "soft constraints",
REMEMBER THIS IS NOT MANDATORY, REGARDED AS OPTIONAL.
'''{soft_constraints}'''

####
Use the above instructions to analyze the supplied files, and provide detailed suggestions to fix all the bad design.
To suggest changes to a file you MUST return the bad design code snippet, reference_components_name, detailed reference guidelines, and fix code suggestion. in the json format.
'''{bad_design_code}'''
'''{detailed_reference_from_guidelines}'''
'''{suggestion_fix_code}'''
find as many bad design as possible.
"""

# We will release full details once the paper is published. Thank you for your interest.
