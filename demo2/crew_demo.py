from crewai import Agent, Task, Crew, Process

from config.llm_config import get_llm
from tools.crewai_tools import (
    ParseDocxTool,
    ExtractProtocolTablesTool,
    DetectTemplateSignalsTool,
)

def build_second_demo_crew() -> Crew:
    llm = get_llm()

    parse_docx_tool = ParseDocxTool()
    extract_tables_tool = ExtractProtocolTablesTool()
    detect_signals_tool = DetectTemplateSignalsTool()

    # 1. Define Agents (Set max_rpm=15 to respect Google Cloud Quotas)
    document_parser_agent = Agent(
        role="Clinical Document Parser",
        goal="Parse protocol and SAP template documents into structured JSON artifacts.",
        backstory=(
            "You are meticulous about document structure, formatting, and reproducible parsing. "
            "You rely on your tools to process the files accurately."
        ),
        llm=llm,
        tools=[parse_docx_tool],
        verbose=True,
        allow_delegation=False,
        max_rpm=1, 
    )

    signal_detection_agent = Agent(
        role="Template Signal Analyst",
        goal="Extract protocol tables and detect SAP template update/remove signals.",
        backstory=(
            "You specialize in converting parsed clinical documents into structured workflow artifacts, "
            "including table extractions and update-unit lists."
        ),
        llm=llm,
        tools=[extract_tables_tool, detect_signals_tool],
        verbose=True,
        allow_delegation=False,
        max_rpm=1, 
    )

    workflow_reporter_agent = Agent(
        role="Workflow Reporter",
        goal="Summarize the generated artifacts and explain what the demo accomplished.",
        backstory=(
            "You create concise, accurate summaries of automation outputs for training and demonstration."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_rpm=1, 
    )

    # 2. Define Tasks (Using EXACT argument names for Pydantic schema validation)
    parse_protocol_task = Task(
        description=(
            "Use the parse_docx_tool to parse the protocol DOCX file.\n"
            "- file_path: {protocol_path}\n"
            "- output_json_path: {protocol_json_path}\n"
            "Return a short confirmation that includes paragraph count and table count."
        ),
        expected_output="A short confirmation JSON-like summary for the parsed protocol file.",
        agent=document_parser_agent,
    )

    parse_template_task = Task(
        description=(
            "Use the parse_docx_tool to parse the SAP template DOCX file.\n"
            "- file_path: {template_path}\n"
            "- output_json_path: {template_json_path}\n"
            "Return a short confirmation that includes paragraph count and table count."
        ),
        expected_output="A short confirmation JSON-like summary for the parsed SAP template file.",
        agent=document_parser_agent,
    )

    extract_tables_task = Task(
        description=(
            "Use the extract_protocol_tables_tool on the parsed protocol JSON.\n"
            "- parsed_protocol_json_path: {protocol_json_path}\n"
            "- output_json_path: {protocol_tables_json_path}\n"
            "Return a short confirmation with the number of extracted tables."
        ),
        expected_output="A short confirmation JSON-like summary for extracted protocol tables.",
        agent=signal_detection_agent,
        context=[parse_protocol_task],
    )

    detect_signals_task = Task(
        description=(
            "Use the detect_template_signals_tool on the parsed template JSON.\n"
            "- parsed_template_json_path: {template_json_path}\n"
            "- output_json_path: {update_units_json_path}\n"
            "Current signal rules: blue text = update placeholder, green text = guidance/remove.\n"
            "Return a short confirmation with the number of detected update units."
        ),
        expected_output="A short confirmation JSON-like summary for detected template update units.",
        agent=signal_detection_agent,
        context=[parse_template_task],
    )

    summarize_task = Task(
        description=(
            "Summarize what artifacts were created in this second demo. "
            "Use the prior task results and produce a concise operational summary "
            "that explains what the CrewAI version accomplished."
        ),
        expected_output=(
            "A concise summary of the generated outputs, counts, and the purpose of this second demo."
        ),
        agent=workflow_reporter_agent,
        context=[
            parse_protocol_task,
            parse_template_task,
            extract_tables_task,
            detect_signals_task,
        ],
    )

    # 3. Assemble the Crew
    return Crew(
        agents=[
            document_parser_agent,
            signal_detection_agent,
            workflow_reporter_agent,
        ],
        tasks=[
            parse_protocol_task,
            parse_template_task,
            extract_tables_task,
            detect_signals_task,
            summarize_task,
        ],
        process=Process.sequential,
        verbose=True,
        max_rpm=1, 
    )
