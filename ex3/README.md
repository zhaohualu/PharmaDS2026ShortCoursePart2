# Exercise 3: LangGraph Conditional Routing

In this exercise, you will enhance the clinical document processing workflow from Demo 3 by adding conditional logic to control the flow of execution.

> **Action Required:** Update the `VERTEXAI_PROJECT` ID in the setup cell of `Exercise.ipynb` before running the notebook (os.environ["VERTEXAI_PROJECT"] = "").

## Objectives
1.  **Implement a Routing Function**: Write the `should_summarize` function to check for the presence of update units.
2.  **Add a Conditional Edge**: Configure the graph to skip the LLM summary step if no update units are detected (enabling a "Fast Exit").
3.  **Graph Visualization**: Use `get_graph().draw_ascii()` to verify the new conditional structure.

## Getting Started
Work through the `TODO` items in the `Exercise.ipynb` notebook to complete the graph building function.