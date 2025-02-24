# DesignRepair: Dual-Stream Design Guideline-Aware Frontend Repair with Large Language Models



**Authors:** Mingyue Yuan, Jieshan Chen\*, Zhenchang Xing, Aaron Quigley, Yuyu Luo, Tianqi Luo, Gelareh Mohammadi, Qinghua Lu, Liming Zhu

DesignRepair is a **dual-stream, knowledge-driven** approach leveraging **Large Language Models (LLMs)** to detect and repair design quality issues in frontend code. It incorporates both **source code analysis** and **user-perceived rendered view analysis**, guided by **Material Design 3** guidelines.

### Key Features:

- **Dual-Stream Analysis**: Simultaneously analysis the source code and its properties of rendered output to identify design issues.
- **Knowledge-Driven Repair**: Integrates Material Design 3 guidelines to ensure repairs align with modern design standards.
- **LLM-Powered Enhancements**: Utilizes the power of Large Language Models to detect and fix design issues effectively.

For more details, read our [paper](https://arxiv.org/abs/2411.01606) on arXiv.

## Abstract 

The rise of Large Language Models (LLMs) has streamlined frontend interface creation through tools like Vercel's V0, yet surfaced challenges in design quality (e.g., accessibility, and usability). Current solutions, often limited by their focus, generalisability, or data dependency, fall short in addressing these complexities comprehensively. Moreover, none of them examine the quality of LLM-generated UI design.
In this work, we introduce DesignRepair, a novel dual-stream design guideline-aware system to examine and repair the UI design quality issues from both code aspect and rendered page aspect. We utilised the mature and popular Material Design as our knowledge base to guide this process. Specifically, we first constructed a comprehensive knowledge base encoding Google's Material Design principles into low-level component knowledge base and high-level system design knowledge base. After that, DesignRepair employs a LLM for the extraction of key components and utilizes the Playwright tool for precise page analysis, aligning these with the established knowledge bases. Finally, we integrate Retrieval-Augmented Generation with state-of-the-art LLMs like GPT-4 to holistically refine and repair frontend code through a strategic divide and conquer approach.
Our extensive evaluations validated the efficacy and utility of our approach, demonstrating significant enhancements in adherence to design guidelines, accessibility, and user experience metrics. 

## Approach

<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/overview.png" height="600">
    <br>
    <p>Framework Overview of DesignRepair</p>
</div>

The overview illustrates the overview of our approach, DesignRepair, which consists of three phases, namely, an offline knowledge base construction, online page extraction and knowledge-driven repair phases. 

For the offline knowledge base construction phase A in picture, we built a two-part knowledge base (KB): a low-level Component Knowledge Base (KB-Comp) and a high-level System Design Knowledge Base (KB-System). This knowledge base functions as a domain expert, offering guidance for addressing potential UI issues. 
Given the frontend code and rendered page, we enter the second phase, where we use a parallel dual-pipe method to extract the used components and their corresponding property groups B in picture.
Finally, we implement a knowledge-driven, LLM-based repair method enhanced with Retrieval-Augmented Generation (RAG) techniques (C in picture). This approach allows us to meticulously analyze and repair issues concurrently. By employing a divide and conquer strategy, we tackle each component/property group individually before synthesizing the repairs. This ensures a cohesive, optimized final output, achieved through a thorough and scrutinized repair process.

## Description

| Section of Pipeline | File Path | Info |
| --- | --- | --- |
| Component Knowledge Base | [`.\library\component\knowledge_base.json`](https://github.com/UGAIForge/DesignRepair/blob/main/library/component_knowledge_base.json) | Extracted from https://m3.material.io/components of the Material Design official documents, it includes 24 component types, and their corresponding guidelines  |
| System Knowledge Base | [`.\library\component\system_base.csv`](https://github.com/UGAIForge/DesignRepair/blob/main/library/system_design_knowledge_base.csv) | Extracted from https://m3.material.io/foundations and https://m3.material.io/styles of the Material Design official documents, and formed into 7 types of Property Groups: Group, Clickable, Spacing, Platform, Label, Text, and Color. The mapping relationship can be visualized in Neo4j using .\scripts\create_knowledge_graph.md. |
| Prompts | [`.\backend\core\prompts.py`](https://github.com/UGAIForge/DesignRepair/blob/main/backend/core/prompts.py) | All prompts, including P_comp_extra, P_map_kb, P_individual, P_all |
|  Knowledge Base Extraction  | [`.\scripts\prepare_kb_dump.py`](https://github.com/UGAIForge/DesignRepair/blob/main/scripts/prepare_kb_dump.py) | Document processing script, structured into knowledge database |

### Prompts Detail 

The prompts' content is located in the file `.\backend\core\prompts.py`. 

The following table outlines the prompt names in the paper, their corresponding variable names in the code, and their respective information:

| Prompt Name in Paper | Variable Name in Code | Information |
| --- | --- | --- |
| P_comp_extra | get_related_components_prompt_web_page_simpler, get_related_components_prompt_web_page_complex  | For step B1, extract related components type list |
| P_map_kb | get_related_components_prompt_library | For step C1, map page components list to library component name list |
| P_individual_components | components_analysis_content | For step C2, analyze components-level design issues |
| P_individual_property | property_analysis_content | For step C2, analyze system-level design issues |
| P_all | regenerate_file_content or regenerate_file_content_multi | For step C3, summarize and analyze all design issues and generate fixed page code |


## Configuration

### Installation

Follow these steps to install and setup the project:

1. Clone the repository:
    ```bash
    git clone https://github.com/UGAIForge/DesignRepair.git
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

To test multiple files simultaneously, execute the `test_multi.py` script:

```bash
python test_multi.py
```



## Here are some compare results of our DesignRepair


### example1 before vs after
<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp1before.gif" width="300">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp1after.gif" width="300">
</div>

### example2 before vs after
<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp2before.gif" width="300">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp2after.gif" width="300">
</div>

### example3 before vs after
<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp3before.gif" width="300">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp3after.gif" width="300">
</div>

### example4 before vs after
<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp4before.gif" width="300">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp4after.gif" width="300">
</div>

### example5 before vs after
<div align="center">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp5before.gif" width="300">
    <img src="https://github.com/UGAIForge/DesignRepair/blob/main/image/exp5after.gif" width="300">
</div>


## Citation
```
@article{yuan2024designrepair,
  title={DesignRepair: Dual-Stream Design Guideline-Aware Frontend Repair with Large Language Models},
  author={Yuan, Mingyue and Chen, Jieshan and Xing, Zhenchang and Quigley, Aaron and Luo, Yuyu and Luo, Tianqi and Mohammadi, Gelareh and Lu, Qinghua and Zhu, Liming},
  journal={arXiv preprint arXiv:2411.01606},
  year={2024}
}
```

