# Demo 4: End-to-End LangGraph Pipeline

Demo 4 represents the complete clinical document processing pipeline, extending the LangGraph workflow to produce a physical Word document.

> **Action Required:** You must update the `VERTEXAI_PROJECT` setting in `main_langgraph.py` with your own project ID before executing this demo (os.environ["VERTEXAI_PROJECT"] = "").

## Key Enhancements
* **Drafting Content**: Includes a step to draft content for identified update units.
* **Document Generation**: Utilizes a document builder to inject drafted content into a template.

## Outputs
In addition to the standard JSON artifacts, this demo produces:
* `Draft_v1.docx`: The final processed clinical document.

## Run
```bash
python main_langgraph.py
```


