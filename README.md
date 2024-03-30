### Hi there 👋

<!--
**DesignRepair2024/DesignRepair2024** is a ✨ _special_ ✨ repository because its `README.md` (this file) appears on your GitHub profile.

Here are some ideas to get you started:

- 🔭 I’m currently working on ...
- 🌱 I’m currently learning ...
- 👯 I’m looking to collaborate on ...
- 🤔 I’m looking for help with ...
- 💬 Ask me about ...
- 📫 How to reach me: ...
- 😄 Pronouns: ...
- ⚡ Fun fact: ...
-->

## setup envs
<!-- conda create --name fkmd python=3.11
conda activate fkmd
pip install -r requirements.txt -->
Run the backend (I use Poetry for package management - `pip install poetry` if you don't have it):

```bash
cd backend
poetry install
poetry shell
poetry run uvicorn main:app --reload --port 7001
```

## 2 add openai key and ROOT_DIR
create file ".envs"
OPENAI_API_KEY="keyhere"