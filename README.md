



# DesignRepair2024

## Description

| Section of Pipeline | File Path | Info |
| --- | --- | --- |
| Component Knowledge Base | [`.\library\component\knowledge_base.json`](https://github.com/DesignRepair2024/DesignRepair2024/blob/main/library/component_knowledge_base.json) | Extracted from https://m3.material.io/components of the Material Design official documents, it includes 24 component types, and their corresponding guidelines  |
| System Knowledge Base | [`.\library\component\system_base.csv`](https://github.com/DesignRepair2024/DesignRepair2024/blob/main/library/system_design_knowledge_base.csv) | Extracted from https://m3.material.io/foundations and https://m3.material.io/styles of the Material Design official documents, and formed into 7 types of Property Groups: Group, Clickable, Spacing, Platform, Label, Text, and Color. The mapping relationship can be visualized in Neo4j using .\scripts\create_knowledge_graph.md. |
| Prompts | [`.\backend\core\prompts.py`](https://github.com/DesignRepair2024/DesignRepair2024/blob/main/backend/core/prompts.py) | All prompts, including P_comp_extra, P_map_kb, P_individual, P_all |
|  Knowledge Base Extraction  | [`.\scripts\prepare_kb_dump.py`](https://github.com/DesignRepair2024/DesignRepair2024/blob/main/scripts/prepare_kb_dump.py) | Document processing script, structured into knowledge database |

### Prompts Detail 

The prompts' content is located in the file `.\backend\core\prompts.py`. 

The following table outlines the prompt names in the paper, their corresponding variable names in the code, and their respective information:

| Prompt Name in Paper | Variable Name in Code | Information |
| --- | --- | --- |
| P_comp_extra | get_related_components_prompt_web_page | For step B1, extract related components type list |
| P_map_kb | get_related_components_prompt_library | For step C1, map page components list to library component name list |
| P_individual_components | components_analysis_content | For step C2, analyze components-level design issues |
| P_individual_property | property_analysis_content | For step C2, analyze system-level design issues |
| P_all | regenerate_file_content | For step C3, summarize and analyze all design issues and generate fixed page code |


### Vercel's V0 projects

| ID | url |
| --- | --- |
| 1 | https://v0.dev/t/0W13RkH |
| 2 | https://v0.dev/t/CF6CtRGlgJi |
| 3 | https://v0.dev/t/OKXb3ACML6t |
| 4 | https://v0.dev/t/itf6aBV |
| 5 | https://v0.dev/t/YKiZgaUISA3 |
| 6 | https://v0.dev/t/zJO10z7wUTe |
| 7 | https://v0.dev/t/x4SRZe6 |
| 8 | https://v0.dev/t/9tk0WDvMrYm |
| 9 | https://v0.dev/t/xiSjIAI |
| 10 | https://v0.dev/t/W5ak7S2nJ9y |
| 11 | https://v0.dev/t/gYyJyeY |
| 12 | https://v0.dev/t/sAfLDnh |
| 13 | https://v0.dev/t/Xx6DE3L |
| 14 | https://v0.dev/t/LnxRCcq |
| 15 | https://v0.dev/t/AfXYpLG |
| 16 | https://v0.dev/t/y37cnlJ |
| 17 | https://v0.dev/t/IIDP1z3aQjw |
| 18 | https://v0.dev/t/fi5AQgx |
| 19 | https://v0.dev/t/rRBlufM |
| 20 | https://v0.dev/t/VT395Yf4lhX |


### Github projects

| ID | url |
| --- | --- |
| 1 | https://github.com/cypress-io/cypress-realworld-app |
| 2 | https://github.com/gothinkster/react-redux-realworld-example-app |
| 3 | https://github.com/jgudo/ecommerce-react?tab=readme-ov-file |
| 4 | https://github.com/oldboyxx/jira_clone |
| 5 | https://github.com/HospitalRun/hospitalrun-frontend |
| 6 | https://github.com/bbc/simorgh |

## Configuration

### Installation

Follow these steps to install and setup the project:

1. Clone the repository:
    ```bash
    git clone https://github.com/DesignRepair2024/DesignRepair2024.git
    ```

2. Navigate to the project directory:
    ```bash
    cd DesignRepair2024
    ```

3. Install the required packages:
    ```bash
    cd backend
    poetry install
    poetry shell
    ```

### add openai key 
    create file `.envs`

    OPENAI_API_KEY="keyhere"

### Usage

Update the content of `text.py` to configure your local environment to run the code:

```python
    if __name__ == "__main__":
        file_dir = r"..\examples" # Your frontend code file folder
        file_name = "example1.tsx" # Your frontend code file

        # page to be tested
        pageurl = "http://localhost:3000" # Your rendered page url
```

To run the project, execute the `test.py` script:

```bash
python test.py
```

### Abstract 
The rise of Large Language Models (LLMs) has streamlined frontend interface creation through tools like Vercel's V0, yet surfaced challenges in design quality (e.g., accessibility, and usability). Current solutions, often limited by their focus, generalisability, or data dependency, fall short in addressing these complexities comprehensively. Moreover, none of them examine the quality of LLM-generated UI design.
In this work, we introduce DesignRepair, a novel dual-stream design guideline-aware system to examine and repair the UI design quality issues from both code aspect and rendered page aspect. We utilised the mature and popular Material Design as our knowledge base to guide this process. Specifically, we first constructed a comprehensive knowledge base encoding Google's Material Design principles into low-level component knowledge base and high-level system design knowledge base. After that, DesignRepair employs a LLM for the extraction of key components and utilizes the Playwright tool for precise page analysis, aligning these with the established knowledge bases. Finally, we integrate Retrieval-Augmented Generation with state-of-the-art LLMs like GPT-4 to holistically refine and repair frontend code through a strategic divide and conquer approach.
Our extensive evaluations validated the efficacy and utility of our approach, demonstrating significant enhancements in adherence to design guidelines, accessibility, and user experience metrics. 

### Approach

![Framework Overview of DesignRepair](https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/overview.png)

The overview illustrates the overview of our approach, DesignRepair, which consists of three phases, namely, an offline knowledge base construction, online page extraction and knowledge-driven repair phases. 

For the offline knowledge base construction phase A in picture, we built a two-part knowledge base (KB): a low-level Component Knowledge Base (KB-Comp) and a high-level System Design Knowledge Base (KB-System). This knowledge base functions as a domain expert, offering guidance for addressing potential UI issues. 
Given the frontend code and rendered page, we enter the second phase, where we use a parallel dual-pipe method to extract the used components and their corresponding property groups B in picture.
Finally, we implement a knowledge-driven, LLM-based repair method enhanced with Retrieval-Augmented Generation (RAG) techniques (C in picture). This approach allows us to meticulously analyze and repair issues concurrently. By employing a divide and conquer strategy, we tackle each component/property group individually before synthesizing the repairs. This ensures a cohesive, optimized final output, achieved through a thorough and scrutinized repair process.

## Here are some compare results of our DesignRepair


### example1 before vs after
<div align="center">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp1before.gif" width="300">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp1after.gif" width="300">
</div>

### example2 before vs after
<div align="center">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp2before.gif" width="300">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp2after.gif" width="300">
</div>

### example3 before vs after
<div align="center">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp3before.gif" width="300">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp3after.gif" width="300">
</div>

### example4 before vs after
<div align="center">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp4before.gif" width="300">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp4after.gif" width="300">
</div>

### example5 before vs after
<div align="center">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp5before.gif" width="300">
    <img src="https://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp5after.gif" width="300">
</div>
