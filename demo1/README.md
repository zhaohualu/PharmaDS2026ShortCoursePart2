# Demo 1: Plain Python Pipeline

This demo implements the earliest runnable checkpoint for the clinical document processing project using a linear Python approach.

> **Action Required:** Ensure you update the Vertex AI Project ID in your configuration or environment variables before execution.

## Functionality
* Parses `protocol.docx` and the target reporting template.
* Extracts structured protocol tables.
* Detects template update/remove signals based on formatting (blue/green text) and bracketed placeholders.
* Outputs structured JSON artifacts to the `outputs/` directory.

## Run
```bash
python main.py
```