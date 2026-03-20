# Demo 3: LangGraph Workflow Version

Demo 3 introduces a state-driven approach to clinical document processing using **LangGraph**, providing more structure and control than a pure Python pipeline or an autonomous agent crew.

> **Action Required:** Update the `VERTEXAI_PROJECT` environment variable in `main_langgraph.py` to match your Google Cloud project (os.environ["VERTEXAI_PROJECT"] = "").

## Design Goals
* **Deterministic Nodes**: The first four nodes (parsing, extraction, detection) are pure Python logic for reliability.
* **Strategic LLM Usage**: The LLM is only utilized in the final summary node to interpret the results.
* **State Management**: Uses a centralized state to pass data between nodes.

## Workflow Nodes
1. `parse_protocol`
2. `parse_template`
3. `extract_tables`
4. `detect_signals`
5. `summarize`

## Run
```bash
python main_langgraph.py
```