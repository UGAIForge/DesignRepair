import asyncio
import re
from playwright.async_api import async_playwright
from playwright.sync_api import Playwright, expect, sync_playwright

import os
import json
from pydantic import BaseModel
from typing import Optional, List
from core.llm import stream_openai_response
from core.prompts import analysis_system
from core.prompts import property_analysis_content

class AnalysisProperty(BaseModel):
    bad_design_code: str
    detailed_reference_from_guidelines: str
    suggestion_fix_code: str

class AnalysisPropertySchema(BaseModel):
    bad_property_design: List[AnalysisProperty]


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

async def load_page(playwright, pageurl=None):
    
    browser = await playwright.chromium.launch(
        traces_dir=None,
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
        ])
    page = await browser.new_page()
    if pageurl:
        await page.goto(pageurl)
    else:
        await page.goto("https://www.google.com")
    print(await page.title())
    await asyncio.sleep(3)

    await page.bring_to_front()
    return page



def remove_extra_eol(text):
    # Replace EOL symbols
    text = text.replace('\n', ' ')
    return re.sub(r'\s{2,}', ' ', text)


def get_first_line(s):
    first_line = s.split('\n')[0]
    tokens = first_line.split()
    if len(tokens) > 8:
        return ' '.join(tokens[:8]) + '...'
    else:
        return first_line
    

async def get_element_description(element, tag_name, role_value, type_value):
    '''
         Asynchronously generates a descriptive text for a web element based on its tag type.
         Handles various HTML elements like 'select', 'input', and 'textarea', extracting attributes and content relevant to accessibility and interaction.
    '''

    salient_attributes = [
        "alt",
        "aria-describedby",
        "aria-label",
        "aria-role",
        "input-checked",
        # "input-value",
        "label",
        "name",
        "option_selected",
        "placeholder",
        "readonly",
        "text-value",
        "title",
        "value",
    ]

    parent_value = "parent_node: "
    parent_locator = element.locator('xpath=..')
    num_parents = await parent_locator.count()
    if num_parents > 0:
        # only will be zero or one parent node
        parent_text = (await parent_locator.inner_text(timeout=0) or "").strip()
        if parent_text:
            parent_value += parent_text
    parent_value = remove_extra_eol(get_first_line(parent_value)).strip()
    if parent_value == "parent_node:":
        parent_value = ""
    else:
        parent_value += " "

    if tag_name == "select":
        text1 = "Selected Options: "
        text2 = ""
        text3 = " - Options: "
        text4 = ""

        text2 = await element.evaluate(
            "select => select.options[select.selectedIndex].textContent", timeout=0
        )

        if text2:
            options = await element.evaluate("select => Array.from(select.options).map(option => option.text)",
                                             timeout=0)
            text4 = " | ".join(options)

            if not text4:
                text4 = await element.text_content(timeout=0)
                if not text4:
                    text4 = await element.inner_text(timeout=0)

            return parent_value+text1 + remove_extra_eol(text2.strip()) + text3 + text4

    input_value = ""

    none_input_type = ["submit", "reset", "checkbox", "radio", "button", "file"]

    if tag_name == "input" or tag_name == "textarea":
        if role_value not in none_input_type and type_value not in none_input_type:
            text1 = "input value="
            text2 = await element.input_value(timeout=0)
            if text2:
                input_value = text1 + "\"" + text2 + "\"" + " "

    text_content = await element.text_content(timeout=0)
    text = (text_content or '').strip()
    if text:
        text = remove_extra_eol(text)
        if len(text) > 80:
            text_content_in = await element.inner_text(timeout=0)
            text_in = (text_content_in or '').strip()
            if text_in:
                return input_value + remove_extra_eol(text_in)
        else:
            return input_value + text

    # get salient_attributes
    text1 = ""
    for attr in salient_attributes:
        attribute_value = await element.get_attribute(attr, timeout=0)
        if attribute_value:
            text1 += f"{attr}=" + "\"" + attribute_value.strip() + "\"" + " "

    text = (parent_value + text1).strip()
    if text:
        return input_value + remove_extra_eol(text.strip())


    # try to get from the first child node
    first_child_locator = element.locator('xpath=./child::*[1]')

    num_childs = await first_child_locator.count()
    if num_childs>0:
        for attr in salient_attributes:
            attribute_value = await first_child_locator.get_attribute(attr, timeout=0)
            if attribute_value:
                text1 += f"{attr}=" + "\"" + attribute_value.strip() + "\"" + " "

        text = (parent_value + text1).strip()
        if text:
            return input_value + remove_extra_eol(text.strip())

    return None


async def get_element_data(element, tag_name):
    tag_name_list = ['a', 'button',
                     'input',
                     'select', 'textarea', 'adc-tab']

    # await aprint(element,tag_name)
    if await element.is_hidden(timeout=0) or await element.is_disabled(timeout=0):
        return None

    tag_head = ""
    real_tag_name = ""
    if tag_name in tag_name_list:
        tag_head = tag_name
        real_tag_name = tag_name
    else:
        real_tag_name = await element.evaluate("element => element.tagName.toLowerCase()", timeout=0)
        if real_tag_name in tag_name_list:
            # already detected
            return None
        else:
            tag_head = real_tag_name

    role_value = await element.get_attribute('role', timeout=0)
    type_value = await element.get_attribute('type', timeout=0)
    # await aprint("start to get element description",element,tag_name )
    description = await get_element_description(element, real_tag_name, role_value, type_value)
    if not description:
        return None

    rect = await element.bounding_box() or {'x': 0, 'y': 0, 'width': 0, 'height': 0}

    if role_value:
        tag_head += " role=" + "\"" + role_value + "\""
    if type_value:
        tag_head += " type=" + "\"" + type_value + "\""

    box_model = [rect['x'], rect['y'], rect['x'] + rect['width'], rect['y'] + rect['height']]
    center_point = ((box_model[0] + box_model[2]) / 2, (box_model[1] + box_model[3]) / 2)
    selector = element


    return [center_point, description, tag_head, box_model, selector, real_tag_name]


async def get_text_from_element(element):
    """
    Extracts text content from a web element.
    """
    try:
        return await element.text_content()
    except Exception as e:
        return None


async def get_groups_with_playwright(page):
    interactive_elements_selectors = [
        'a', 'button',
        'input',
        'select', 'textarea', 'adc-tab', '[role="button"]', '[role="radio"]', '[role="option"]', '[role="combobox"]',
        '[role="textbox"]',
        '[role="listbox"]', '[role="menu"]',
        '[type="button"]', '[type="radio"]', '[type="combobox"]', '[type="textbox"]', '[type="listbox"]',
        '[type="menu"]',
        '[tabindex]:not([tabindex="-1"])', '[contenteditable]:not([contenteditable="false"])',
        '[onclick]', '[onfocus]', '[onkeydown]', '[onkeypress]', '[onkeyup]', "[checkbox]",
        '[aria-disabled="false"],[data-link]'
    ]

    tasks = []
    all_text_content = [] 

    seen_elements = set()
    for selector in interactive_elements_selectors:
        locator = page.locator(selector)
        element_count = await locator.count()
        for index in range(element_count):
            element = locator.nth(index)
            tag_name = selector.replace(":not([tabindex=\"-1\"])", "")
            tag_name = tag_name.replace(":not([contenteditable=\"false\"])", "")
            task = get_element_data(element, tag_name)
            # task = get_text_from_element(element)
            tasks.append(task)

    results = await asyncio.gather(*tasks)
    # for text in results:
    #     if text:
    #         all_text_content.append(text.strip())

    # print(results)
    return results

def check_and_repair(ctx):
    pass


async def get_all_xpaths(page):
    """
    get_all_xpaths XPath
    """
    script = """
    () => {
        const allElements = document.querySelectorAll('*');
        const getXPath = (element) => {
            if (element.id) return 'id(\"' + element.id + '\")';
            if (element === document.body) return element.tagName;

            var ix = 0;
            const siblings = element.parentNode ? element.parentNode.childNodes : [];
            for (var i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) 
                    return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
            }
        };

        return Array.from(allElements).map(el => getXPath(el)).filter(x => x != null);
    }
    """

    xpaths = await page.evaluate(script)
    return xpaths


async def get_text_properties(page):
    """
    Extract properties of text elements from the page, including their outer HTML and XPath, with deduplication based on XPath or content.
    """
    script = """
    () => {
        const getXPath = (element) => {
            if (element.id !== '') return 'id(\"' + element.id + '\")';
            if (element === document.body) return element.tagName;
            let ix = 0;
            const siblings = element.parentNode.childNodes;
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) 
                    return getXPath(element.parentNode) + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
            }
            return null;
        };

         const getTextContent = (element) => {
            return element.childNodes.length === 1 && element.childNodes[0].nodeType === Node.TEXT_NODE
                ? element.textContent.trim()
                : Array.from(element.childNodes)
                    .filter(e => e.nodeType === Node.TEXT_NODE)
                    .map(e => e.textContent.trim())
                    .join('');
        };

        const allTextElements = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, a, div'));
        const elementsData = [];

        allTextElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const xpath = getXPath(element);
            const content = getTextContent(element);

            if (content) {
                elementsData.push({
                    outerHTML: element.outerHTML,
                    xpath: xpath,
                    content: content,
                    fontSize: computedStyle.fontSize,
                    fontFamily: computedStyle.fontFamily,
                    fontWeight: computedStyle.fontWeight,
                    color: computedStyle.color,
                    backgroundColor: computedStyle.backgroundColor, 
                    tagName: element.tagName,
                    class: element.className
                });
            }
        });

        return elementsData;
    }
    """
    return await page.evaluate(script)

# save uniqueElementsWithColor
async def get_all_colors2(page):
    script = """
    () => {
        const findColor = (element) => {
            let node = element;
            let color = null, backgroundColor = null;
            while (node && node instanceof Element) {
                const computedStyle = window.getComputedStyle(node);
                if (!color && computedStyle.color !== 'rgba(0, 0, 0, 0)' && computedStyle.color !== 'rgb(0, 0, 0)') {
                    color = computedStyle.color;
                }
                if (!backgroundColor && computedStyle.backgroundColor !== 'rgba(0, 0, 0, 0)' && computedStyle.backgroundColor !== 'transparent') {
                    backgroundColor = computedStyle.backgroundColor;
                }
                if (color && backgroundColor) break;
                node = node.parentNode;
            }
            return { color, backgroundColor };
        };

        const getXPath = (element) => {
            if (!element || !element.parentNode) {
                return null;
            }
            if (element.id) {
                return `id("${element.id}")`;
            }
            if (element === document.body) {
                return element.tagName.toLowerCase();
            }
            let ix = 1;
            const siblings = element.parentNode.childNodes;
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) {
                    return `${getXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${ix}]`;
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
            return null;
        };


        const isElementVisible = (element) => {
            return element.offsetWidth > 0 || element.offsetHeight > 0 || element.getClientRects().length > 0;
        };

        const uniqueElementsWithColor = new Map();
        const traverseDOM = (element, parentXPath = '') => {
            const xpath = parentXPath ? `${parentXPath}/${getXPath(element)}` : getXPath(element);
            if (isElementVisible(element)) {
                const { color, backgroundColor } = findColor(element);
                if (color || backgroundColor) {
                    // If the parent element has the same color, don't add this element
                    const parentXpath = parentXPath ? parentXPath : getXPath(element.parentNode);
                    const parentData = uniqueElementsWithColor.get(parentXpath);
                    if (!parentData || parentData.color !== color || parentData.backgroundColor !== backgroundColor) {
                        uniqueElementsWithColor.set(xpath, {
                            element: element.outerHTML,
                            backgroundColor: backgroundColor,
                            color: color
                        });
                    }
                }
            }
            Array.from(element.children).forEach(child => {
                traverseDOM(child, xpath);
            });
        };

        traverseDOM(document.body);
        return Array.from(uniqueElementsWithColor.values());
    }
    """
    return await page.evaluate(script)

# save all colors
async def get_all_colors(page):
    script = """
    () => {
        const findColor = (element) => {
            let node = element;
            let color = null, backgroundColor = null;
            while (node && node instanceof Element) {  // Ensure node is a DOM element
                const computedStyle = window.getComputedStyle(node);
                if (!color && computedStyle.color !== 'rgba(0, 0, 0, 0)' && computedStyle.color !== 'rgb(0, 0, 0)') {
                    color = computedStyle.color;
                }
                if (!backgroundColor && computedStyle.backgroundColor !== 'rgba(0, 0, 0, 0)' && computedStyle.backgroundColor !== 'transparent') {
                    backgroundColor = computedStyle.backgroundColor;
                }
                if (color && backgroundColor) break;
                node = node.parentNode;
            }
            return { color, backgroundColor };
        };


        const getXPath = (element) => {
            if (element.id) {
                return `id("${element.id}")`;
            }
            if (element === document.body) {
                return element.tagName.toLowerCase();
            }
            let ix = 1;
            const siblings = element.parentNode.childNodes;
            for (let i = 0; i < siblings.length; i++) {
                const sibling = siblings[i];
                if (sibling === element) {
                    return `${getXPath(element.parentNode)}/${element.tagName.toLowerCase()}[${ix}]`;
                }
                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                    ix++;
                }
            }
            return null;
        };

        const isElementVisible = (element) => {
            return element.offsetWidth > 0 || element.offsetHeight > 0 || element.getClientRects().length > 0;
        };

        const traverseDOM = (element, parentXPath = '') => {
            const xpath = parentXPath ? `${parentXPath}/${getXPath(element)}` : getXPath(element);
            if (isElementVisible(element)) {
                const { color, backgroundColor } = findColor(element);
                if (color || backgroundColor) {
                    uniqueElementsWithColor.set(xpath, {
                        element: element.outerHTML,
                        // xpath: xpath,
                        backgroundColor: backgroundColor,
                        color: color
                    });
                }
            }
            Array.from(element.children).forEach(child => {
                traverseDOM(child, xpath);
            });
        };

        const uniqueElementsWithColor = new Map();
        traverseDOM(document.body);
        return Array.from(uniqueElementsWithColor.values());
    }
    """
    return await page.evaluate(script)


async def get_label_properties(page):
    script = """
    () => {
        const allElements = document.querySelectorAll('img, video, button, input, select, textarea, label');
        const labelData = [];

        allElements.forEach(element => {
            let labelText = '';
            if (element.tagName.toLowerCase() === 'img') {
                labelText = element.alt; // Alternative text for images
            } else if (element.tagName.toLowerCase() === 'video') {
                labelText = element.getAttribute('aria-label') || element.title; // ARIA label or title for videos
            } else if (element.tagName.toLowerCase() === 'button') {
                labelText = element.textContent.trim() || element.getAttribute('aria-label'); // Text content or ARIA label for buttons
            } else if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'select' || element.tagName.toLowerCase() === 'textarea') {
                const label = document.querySelector(`label[for='${element.id}']`);
                labelText = label ? label.textContent.trim() : '';
            }

            if (labelText) {
                labelData.push({
                    element: element.outerHTML,
                    label: labelText
                });
            }
        });

        return labelData;
    }
    """
    return await page.evaluate(script)


async def get_clickable_properties(page):
    script = """
    () => {
        const allClickableElements = document.querySelectorAll('a, button, input[type="button"], input[type="submit"], [onclick], [role="button"]');
        const clickableData = [];

        allClickableElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);
            const rect = element.getBoundingClientRect();

            let isLargeEnough = false;
            const MIN_TOUCH_SIZE = 44; // 44x44 pixels is a common touch target size recommendation
            if (rect.width >= MIN_TOUCH_SIZE && rect.height >= MIN_TOUCH_SIZE) {
                isLargeEnough = true;
            }

            // Check for elevation (e.g., box-shadow or non-zero z-index)
            const hasElevation = computedStyle.boxShadow !== 'none' || parseInt(computedStyle.zIndex, 10) > 0;
            let elevationColor = null;
            if (hasElevation && computedStyle.boxShadow !== 'none') {
                elevationColor = computedStyle.boxShadow.split(' ')[3]; // Assuming the color is the 4th value in boxShadow
            }

            clickableData.push({
                element: element.outerHTML,
                touchSize: {
                    width: rect.width,
                    height: rect.height,
                },
                isLargeEnough: isLargeEnough,
                focusable: 'tabIndex' in element && element.tabIndex >= 0,
                hasElevation: hasElevation,
                elevationColor: elevationColor
            });
        });

        return clickableData;
    }
    """
    return await page.evaluate(script)



async def get_layout_properties(page):
    script = """
    () => {
        const allElements = document.querySelectorAll('*');
        const layoutData = new Map();

        allElements.forEach(element => {
            const computedStyle = window.getComputedStyle(element);

            const layoutInfo = {
                margin: {
                    top: computedStyle.marginTop,
                    right: computedStyle.marginRight,
                    bottom: computedStyle.marginBottom,
                    left: computedStyle.marginLeft
                },
                padding: {
                    top: computedStyle.paddingTop,
                    right: computedStyle.paddingRight,
                    bottom: computedStyle.paddingBottom,
                    left: computedStyle.paddingLeft
                },
                border: {
                    top: computedStyle.borderTopWidth,
                    right: computedStyle.borderRightWidth,
                    bottom: computedStyle.borderBottomWidth,
                    left: computedStyle.borderLeftWidth
                }
            };

            // Skip if all values are zero
            if (Object.values(layoutInfo.margin).every(val => val === '0px') &&
                Object.values(layoutInfo.padding).every(val => val === '0px') &&
                Object.values(layoutInfo.border).every(val => val === '0px')) {
                return;
            }

            const layoutString = JSON.stringify(layoutInfo);
            let isChildOfExistingElement = false;

            // Check if an element with the same layout already exists
            layoutData.forEach((data, key) => {
                if (key === layoutString) {
                    const existingElement = document.createElement('div');
                    existingElement.innerHTML = data.element;
                    if (existingElement.firstChild.contains(element)) {
                        isChildOfExistingElement = true;
                    }
                }
            });

            if (!isChildOfExistingElement) {
                layoutData.set(layoutString, {
                    element: element.outerHTML,
                    layoutInfo
                });
            }
        });


        return Array.from(layoutData.values());
    }
    """
    return await page.evaluate(script)


def assemble_analysis_property_prompt(file_content, related_guidelines, property_type, property_list):
    print (f"-----ANALYZE PROPERTIES : {property_type}-------")
    
    property_analysis_content_prompt = property_analysis_content
    property_analysis_content_prompt = property_analysis_content_prompt.replace("{file_content}", file_content)
    property_analysis_content_prompt = property_analysis_content_prompt.replace("{property_type}", property_type)
    property_analysis_content_prompt = property_analysis_content_prompt.replace("{properties}", str(property_list))
    property_analysis_content_prompt = property_analysis_content_prompt.replace("{hard_constraints}", str(related_guidelines['hard']))

    prompt =[
        {
            "role": "system",
            "content": analysis_system,
        },
        { 
            "role": "user",
            "content": property_analysis_content_prompt
        },
        {
            "role": "system",
            "content": "Please respond ONLY with valid json that conforms to this pydantic json_schema: {model_class.schema_json()}.\n"
        }]

    functions=[
        {
          "name": "analyze_components",
          "description": "analyze ",
          "parameters": AnalysisPropertySchema.schema()
        },
    ]
    return prompt, functions


def is_json_file(file):
    try:
        json.loads(file)
        return True
    except ValueError:
        return False


async def analysis_groups(ctx, high_level_guidelines, pageurl):
    result_data = []

    # define log file
    folder_name = ctx.file_name.split(".")[0]
    log_file = os.path.join(folder_name, "property.log")

    async with async_playwright() as playwright:
        # playwright load page
        page = await load_page(playwright, pageurl)

        property_results = {}

        # text property
        text_properties = await get_text_properties(page)
        # for item in text_properties:
        #     print(item)
            # print(item['content'])
        print(len(text_properties))
        property_results["Text"] = text_properties

        # color property
        all_colors = await get_all_colors(page)
        # for item in all_colors:
        #     print(item)
        print(len(all_colors))
        property_results["Color"] = all_colors

        # label property
        label_properties = await get_label_properties(page)
        # for item in label_properties:
        #     print(item)
        print(len(label_properties))
        property_results["Label"] = label_properties

        # clickable property
        clickable_properties = await get_clickable_properties(page)
        # for item in clickable_properties:
        #     print(item)
        print(len(clickable_properties))
        property_results["Clickable"] = clickable_properties

        # spacing property
        spacing_properties = await get_layout_properties(page)
        # for item in spacing_properties:
        #     print(item)
        print(len(spacing_properties))
        property_results["Spacing"] = spacing_properties
        
        # 3 import related guidelines
        for property in ["Group", "Clickable", "Spacing", "Platform","Label","Text","Color"]:
            if property in high_level_guidelines and property in property_results and len(property_results[property]) > 0:

                with open(log_file, "a") as file:
                    guidelines_len = (len(high_level_guidelines[property]['soft'])+len(high_level_guidelines[property]['hard']))
                    file.write( property + ": " + str(len(property_results[property])) + "   "+ str(guidelines_len) + "\n")

                # 4 analysis and repair
                analysis_property_prompt, property_schema = assemble_analysis_property_prompt(ctx.file_content, high_level_guidelines[property], property, property_results[property])
                completion = await get_response(analysis_property_prompt, property_schema)
                # print(completion)

                # result validation
                max_attempts = 2
                for _ in range(max_attempts):
                    if is_json_file(completion):
                        break
                    print("result has problem, regenerate")
                    completion = await get_response(analysis_property_prompt, property_schema)

                if not is_json_file(completion):
                    continue  
                else:
                    res_content = json.loads(completion)

                #####################
                new_key = f"bad_{property}_property_design"
                res_content = res_content["bad_property_design"]
                res = {new_key: res_content}
                result_data.append(res)

            elif property == "Group": # or property == "Platform":
                # 4 analysis and repair
                analysis_property_prompt, property_schema = assemble_analysis_property_prompt(ctx.file_content, high_level_guidelines[property], property, ["analyze code directly"])
                completion = await get_response(analysis_property_prompt, property_schema)
                # print(completion)

                res_content = json.loads(completion)
                new_key = f"bad_{property}_property_design"
                res_content = res_content["bad_property_design"]
                res = {new_key: res_content}
                result_data.append(res)

        await page.close()

        # print(result_data)
        return result_data
    
    