



# DesignRepair2024

## Description

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
    <img src="hhttps://github.com/DesignRepair2024/DesignRepair2024/blob/main/image/exp5after.gif" width="300">
</div>

## How to use

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
create file ".envs"
OPENAI_API_KEY="keyhere"

### Usage

To run the project, execute the `test.py` script:

```bash
python test.py