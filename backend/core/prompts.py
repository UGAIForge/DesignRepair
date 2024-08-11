
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



get_related_components_prompt_web_page_simpler = """
Here is the web page you need to analyze:
'''{file_content}'''
    -Summarize the web page, break it down into smaller components.
    -Carefully analyze the Tags, import library and function (HTML elements like div, img, p, section, svg, and h1 (and comment containers) are not considered UI components, wheras other special HTML elements are considered UI components, like input).
    -Further more, You need to analyze is there any simpler UI components of the following web components:

    [badges: Small labels that display information or status. (Often implemented using HTML elements with CSS styling),
    buttons: Interactive elements that trigger actions. (Can be achieved using HTML button elements and CSS),
    checkbox: A UI element that allows users to select one or more options from a set. (Implemented with HTML checkbox elements and potentially CSS for styling),
    date pickers: Components that allow users to select a date. (Usually involve HTML input elements with specialized JavaScript libraries for date selection),
    text fields: Input areas for users to enter text. (Simply HTML input elements with type="text or input"),
    time pickers: Components that allow users to select a time. (Similar to date pickers, using HTML input elements and JavaScript libraries),
    sliders: Components that allow users to select a value from a range. (Often involve HTML input elements with type="range" and CSS),
    radio button: UI elements where only one option can be selected at a time from a group. (Implemented with HTML radio buttons and potentially CSS),
    icon buttons: Buttons that display an icon instead of text. (Can be achieved using HTML button elements, CSS for styling, and potentially Font Awesome or other icon libraries),
    extended fab: An extended floating action button with additional functionality. (Usually a custom component using HTML, CSS, and JavaScript),
    floating action button: A circular button that typically performs a primary action. (Can be implemented with HTML button),
    progress Indicators: Visual elements that show the status of an ongoing process. (Can be implemented with HTML, CSS, and JavaScript)]

        
    Extract all the components name from the web page, save it in a list {"components"}.
"""

get_related_components_prompt_web_page_complex = """
Here is the web page you need to analyze:
'''{file_content}'''
    -You need to analyze is there any complex UI components of the following web components name in the web page:

    [bottom app bar: A bar at the bottom of the screen that provides essential actions for the current view. (Requires multiple HTML elements and CSS styles),
    bottom sheets: Modal sheets that slide up from the bottom of the screen. (Requires a combination of HTML, CSS, and potentially JavaScript for interactivity),
    cards: Informative elements that showcase content and actions. (Often involve various HTML elements and CSS for styling and layout),
    carousel: A component that automatically or manually cycles through a series of content items. (Involves HTML, CSS, and JavaScript for animation and interaction),
    chips: Compact components that represent a choice, attribute, or action. (Multiple HTML elements and CSS for styling),
    dialogs: Modal windows that provide focused content and require user interaction. (Usually involve multiple HTML elements, CSS for styling, and JavaScript for behavior),
    divider: A visual separator between sections of content. (Often implemented using HTML elements with CSS styling),
    lists: Ordered or unordered lists of items that can be interactive or non-interactive. (Can be achieved with HTML ul and li elements, potentially with CSS),
    menus: Overlays that display navigation or options. (Typically involve HTML, CSS, and JavaScript for dynamic behavior),
    navigation bar: A horizontal bar at the top or bottom of a web page that provides primary navigation links. (Requires HTML elements and CSS for styling),
    navigation drawer: A vertical panel that slides in from the side of the screen for navigation. (Usually involves HTML, CSS, and JavaScript for animation and interaction),
    navigation rail: A persistent navigation bar that appears on the side of the screen. (Requires HTML elements and CSS for styling),
    search: A component that allows users to search for content. (Often implemented using HTML input elements, potentially with JavaScript for advanced search functionality),
    segmented buttons: A group of buttons where only one can be selected at a time. (Requires a combination of HTML elements and CSS for styling),
    side sheets: Modal sheets that slide in from the side of the screen. (Similar to bottom sheets, involving HTML, CSS, and potentially JavaScript),
    snackbar: A brief temporary message that appears at the bottom of the screen. (Usually involves HTML, CSS animations, and potentially JavaScript for timing),
    switch: A toggle component that can be switched on or off. (Can be implemented with HTML checkboxes and CSS styling),
    tabs: A component that allows users to switch between different views. (Requires HTML elements, CSS for styling, and JavaScript for tab switching functionality),
    tooltips: Informative popups that appear on hover or click. (Involve HTML elements with CSS positioning and JavaScript for behavior),
    top app bar: A bar at the top of the screen that often includes the application title and actions. (Similar to bottom app bar, requiring HTML elements and CSS styles)]

    Only extract the most related complex components name from the web page, save it in a list {"components"}.
"""


get_related_components_prompt_library = """
Multiple component guidelines can be used while checking the component in order to help find the mistake and improve.
You have the following list of [library component name]: 
'''{components_list}'''
    -Map web page components you got, to the corresponding library components. save it in a list {"components"}.

    Notice, the web page component name and the library component name do not correspond exactly. 
    Tip: You can decompose components or combine components to find the corresponding components in the library.
    Please try your best to find it.
    Only save the exact library component name in the list {"components"}
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

test = """

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

####
Use the above instructions to analyze the supplied files, and provide detailed suggestions to fix all the bad design.
To suggest changes to a file you MUST return the bad design code snippet with its filename, detailed reference guidelines, and fix code suggestion. in the json format.
'''{bad_design_code_filename}'''
'''{bad_design_code}'''
'''{detailed_reference_from_guidelines}'''
'''{suggestion_fix_code}'''
find as many bad design as possible.
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

####
Use the above instructions to analyze the supplied files, and provide detailed suggestions to fix all the bad design.
To suggest changes to a file you MUST return the bad design code snippet, with its filename, detailed reference guidelines, and fix code suggestion. in the json format.
'''{bad_design_code_filename}'''
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
You MUST make the color, layout in beatiful and consistent design, and readability!!!

Return only the full code you improved. 
Do not include markdown "```" or "```jsx" at the start or end.
"""

merge_suggestions = """
Here is the current content of the files you need to modify:
'''{file_content}'''

Here are the bad design code snippet, detailed reference guidelines, and suggested fixes.
'''{suggestions}'''

- There may be conflicts between the bad design code snippets. Please try your best to resolve these conflicts and merge suggestions to provide the best improvement results.

Review the suggestions and rethink how to fix the bad design using a consistent approach.
To suggest changes to a file, you MUST return the bad design code snippet, with its filename, detailed reference guidelines, and suggested fix in JSON format.
For code snippets being fixed in the same file, use the exact same filename and try to place the fixed code in adjacent order.
'''{bad_design_code_filename}'''
'''{bad_design_code}'''
'''{detailed_reference_from_guidelines}'''
'''{suggested_fix_code}'''
"""

#  - check all the suggestions one by one and fix the file.
regenerate_file_content_multi = """
To suggest changes to a file you MUST return the entire content of the updated file.

Here is the current content of the files you need to modify:
'''{file_content}'''

Here are the bad design code snippet, detailed reference guidelines, and fix code suggestion.
'''{suggestions}'''

- Do not add comments in the code such as "<!-- Add other navigation links as needed -->" and "<!-- ... other news items ... -->" in place of writing the full code. WRITE THE FULL CODE.
- Repeat elements as needed. For example, if there are 15 items, the code should have 15 items. DO NOT LEAVE comments like "<!-- Repeat for each news item -->" or bad things will happen.

To suggest changes to a file you MUST return the entire content of the updated file. 
Every file listing MUST use this format: with the filename with any originally provided path and entire content of the file in the json format.
'''{filename_with_path}'''
'''{repaired_code_file}'''
"""
