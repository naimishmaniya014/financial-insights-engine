import os

from dotenv import load_dotenv

from crewai import LLM, Agent, Crew, Process, Task


load_dotenv()

inf_cloud_api_key = os.getenv("INFERENCE_CLOUD_API_KEY")
inf_cloud_endpoint = os.getenv("INFERENCE_CLOUD_ENDPOINT")

os.environ["OTEL_SDK_DISABLED"] = "true"

llm = LLM(model="openai/Llama-3.1-8B", base_url=inf_cloud_endpoint, api_key=inf_cloud_api_key, max_tokens=1024)

research = Agent(
    role="researcher",
    goal="the goal of this agent is to research about new AI models and their applications",
    backstory="this agent is a data scientist researcher and is interested in AI models",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    max_retry_limit=2,
)

writer = Agent(
    role="writer",
    goal="the goal of this agent is to write about AI models and their applications",
    backstory="this agent is a writer for a blog and is interested in AI models",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    max_retry_limit=2,
)

task1 = Task(
    description="research about new AI models and their applications",
    agent=research,
    expected_output="give a list of the top 5 AI models and their specific applications, do a short answer",
)
task2 = Task(
    description="write about AI models and their applications",
    agent=writer,
    expected_output="a blog post with at least 3 main parts, in markdown format, use the list given by the researcher",
)

crew = Crew(
    name="AI Models Crew",
    agents=[research, writer],
    tasks=[task1, task2],
    verbose=True,
    share_crew=False,
    process=Process.sequential,
)

result = crew.kickoff()

print("-----------------------------")
print("Crew execution result:")
print("-----------------------------")
print(result)