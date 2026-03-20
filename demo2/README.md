# Demo 2: CrewAI Agent Workflow

This demo migrates the clinical document processing logic into the **CrewAI** framework, utilizing specialized agents to handle different stages of the workflow.

> **Action Required:** Update the `os.environ["VERTEXAI_PROJECT"]` value in `main_crewai.py` to your specific project ID before running the script (os.environ["VERTEXAI_PROJECT"] = "").

## Agents & Roles
* **Clinical Document Parser**: Meticulously parses documents into structured JSON.
* **Template Signal Analyst**: Specializes in table extraction and signal detection.
* **Workflow Reporter**: Summarizes generated artifacts and accomplishments.

## Configuration
Project settings like `MODEL_NAME` (e.g., `gemini-2.5-flash-lite`) and `VERTEXAI_PROJECT` can be configured directly in `main_crewai.py`.

## Run
```bash
python main_crewai.py
```