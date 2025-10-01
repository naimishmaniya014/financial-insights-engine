import os
import yfinance as yf
from newsapi import NewsApiClient
from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OTEL_SDK_DISABLED"] = "true"

inf_cloud_api_key = os.getenv("INFERENCE_CLOUD_API_KEY")
inf_cloud_endpoint = os.getenv("INFERENCE_CLOUD_ENDPOINT")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# User input
company_name = input("Enter a company name (e.g., Apple, Tesla): ")
ticker_symbol = input("Enter the stock ticker symbol (e.g., AAPL, TSLA): ")

# Fetch financial data
stock = yf.Ticker(ticker_symbol)
financials = stock.info

# Fetch recent news
newsapi = NewsApiClient(api_key=NEWS_API_KEY)
articles = newsapi.get_everything(q=company_name, language='en', page_size=5)['articles']
news_text = "\n".join([f"{a['title']} - {a['source']['name']}" for a in articles])

# Prepare LLM
llm = LLM(model="openai/Llama-3.1-8B", base_url=inf_cloud_endpoint, api_key=inf_cloud_api_key, max_tokens=1024)

# Researcher Agent
researcher = Agent(
    role="researcher",
    goal=f"Research detailed insights on {company_name}",
    backstory="A financial analyst interested in company data and news",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Writer Agent
writer = Agent(
    role="writer",
    goal=f"Summarize insights on {company_name} into a readable report",
    backstory="A business writer producing reports for investors",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Tasks
task1 = Task(
    description=f"""
    Gather insights on {company_name} including:
    1. Current financial data: {financials}
    2. Summarized news: {news_text}
    3. Future sentiment predictions for the company
    """,
    agent=researcher,
    expected_output="Structured insights with financial summary, news, and sentiment"
)

task2 = Task(
    description=f"Write a readable, well-structured report for {company_name} using the researcher's findings",
    agent=writer,
    expected_output="Markdown formatted report summarizing financials, news, and sentiment"
)

# Crew
crew = Crew(
    name=f"{company_name} Insights Crew",
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True,
    share_crew=False,
    process=Process.sequential
)

# Execute
result = crew.kickoff()

print("\n\n==================== REPORT ====================")
print(result)
