from any_agent import AnyAgent, AgentConfig
from any_agent.tools import search_web

tutor_agent = AnyAgent.create(
    "tinyagent",
    AgentConfig(
        model_id="anthropic:claude-sonnet-4-20250514",
        instructions="""You are a Socratic AI tutor for school students.
        NEVER give direct answers. Always respond with guiding questions and hints.
        Break complex topics into simple steps. Be age-appropriate.""",
        tools=[search_web]
    )
)

def run_tutor(question: str, subject: str, grade: str) -> str:
    prompt = f"Subject: {subject}\nGrade: {grade}\nQuestion: {question}"
    trace = tutor_agent.run(prompt)
    return str(trace)