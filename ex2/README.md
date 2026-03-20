# Exercise 2: CrewAI QA Integration

This exercise challenges you to extend the clinical document processing workflow from Demo 2 by adding a clinical review step.

> **Action Required:** In the first code cell of `exercise.ipynb`, ensure you update the `VERTEXAI_PROJECT` ID to your own project ID (os.environ["VERTEXAI_PROJECT"] = "").

## Objectives
1.  **Define a QA Reviewer Agent**: Create an agent with the role of "Clinical QA Reviewer" and a senior clinical data manager backstory.
2.  **Define a QA Task**: Create a task that reviews detected update units for clinical clarity before final summarization.
3.  **Update the Crew**: Integrate the new agent and task into the sequential process.

## Getting Started
Follow the instructions in `exercise.ipynb` to complete the `TODO` sections.