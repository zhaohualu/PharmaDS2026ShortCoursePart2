# PharmaDS 2026 Short Course Part 2: Clinical Document Processing

This repository contains materials for the second part of the PharmaDS 2026 Short Course "Information Extraction and Document Preparation in Clinical Trial Development Using RAG-based LLMs", focusing on **clinical document processing** and automated drafting. The project demonstrates how to transition from traditional Python pipelines to advanced AI-agentic and state-driven workflows.

> **Note for Users:** Before running any code in this repository, you must update the `VERTEXAI_PROJECT` ID in the respective `main.py` or `.ipynb` files (os.environ["VERTEXAI_PROJECT"] = "") to match your specific Google Cloud project.

## Project Overview
The core objective is to apply clinical document processing to research protocols and reporting templates to automatically identify update placeholders and draft content using LLMs (specifically Gemini via Vertex AI).

## Repository Structure

### Demos
* **[Demo 1](./demo1/)**: A foundational Python pipeline for document parsing and signal detection.
* **[Demo 2](./demo2/)**: An agentic implementation of clinical document processing using the **CrewAI** framework.
* **[Demo 3](./demo3/)**: A structured, state-driven workflow using **LangGraph** with deterministic nodes.
* **[Demo 4](./demo4/)**: A complete end-to-end clinical document processing pipeline that generates a final processed Word document.

### Exercises
* **[Exercise 2](./ex2/)**: Extending the CrewAI workflow with a **QA Reviewer Agent**.
* **[Exercise 3](./ex3/)**: Implementing **Conditional Routing** in LangGraph to optimize the processing workflow.

