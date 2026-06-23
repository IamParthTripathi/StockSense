"""
agent.py — StockSense
---------------------
Builds and runs the LangChain ReAct tool-calling agent.

How the agent works:
  1. Receives the user's analysis request
  2. REASONS: decides which tools to call and in what order
  3. ACTS: calls tools to get live data (price, company info, news)
  4. OBSERVES: reads tool outputs
  5. Repeats until enough information is gathered
  6. Generates the final structured analysis report

This "Reasoning + Acting" (ReAct) loop is what makes it an agent
rather than a fixed pipeline — the LLM controls the execution flow.
"""

import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

from stock_tools import get_stock_price, get_company_info, get_latest_news

load_dotenv()

# All tools available to the agent
TOOLS = [get_stock_price, get_company_info, get_latest_news]

# System prompt — instructs the agent on its role and output format
SYSTEM_PROMPT = """You are StockSense, an expert financial analyst AI assistant.

Your job is to analyze stocks and provide structured investment briefs.

When a user asks you to analyze a stock or company:
1. ALWAYS start by fetching the current stock price using get_stock_price
2. ALWAYS fetch company fundamentals using get_company_info
3. ALWAYS fetch the latest news using get_latest_news with the company name as query
4. Then synthesize all gathered data into a structured analysis report

Your final report MUST follow this exact format:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STOCKSENSE ANALYSIS — [COMPANY NAME] ([TICKER])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 PRICE SNAPSHOT
[Current price, day change, 5-day change, 52-week position]

🏢 COMPANY OVERVIEW  
[Sector, market cap, P/E ratio, key financial metrics]

📰 SENTIMENT ANALYSIS
[Based on latest news — Bullish / Bearish / Neutral with reasoning]
News Summary: [2-3 key points from recent headlines]

💡 KEY CATALYSTS
[Positive factors that could drive the stock up]

⚠️ RISK FACTORS
[Negative factors or concerns to watch]

📋 VERDICT
Recommendation: [BUY / HOLD / SELL]
Reasoning: [2-3 sentence justification based on data]
Confidence: [HIGH / MEDIUM / LOW]

⚠️ DISCLAIMER: This is AI-generated analysis for educational purposes only.
Not financial advice. Always consult a qualified financial advisor.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Be specific, data-driven, and cite the exact numbers you retrieved from tools.
Never make up numbers — only use data from tool outputs.
"""


def build_agent() -> AgentExecutor:
    """
    Build a LangChain ReAct agent with tool-calling capability.

    Uses create_openai_tools_agent which leverages OpenAI's native
    function-calling API — more reliable than text-based ReAct.
    """
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,       # Low temp for factual, consistent analysis
        max_tokens=2000,     # Enough for the full structured report
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),  # Required for ReAct loop
    ])

    agent = create_openai_tools_agent(llm, TOOLS, prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=False,        # Set True to see the full ReAct reasoning in terminal
        max_iterations=8,     # Prevent infinite tool-calling loops
        return_intermediate_steps=True,  # So we can show which tools were called
        handle_parsing_errors=True,      # Graceful handling of malformed outputs
    )


def analyze_stock(company: str, ticker: str) -> dict:
    """
    Run the StockSense agent to analyze a given stock.

    Returns:
        dict with keys:
          - report: str (the final formatted analysis)
          - tools_used: list of str (which tools were called)
          - error: str or None
    """
    agent_executor = build_agent()

    query = (
        f"Please analyze {company} (ticker symbol: {ticker}). "
        f"Fetch current price, company info, and latest news, "
        f"then provide a complete investment brief in the required format."
    )

    try:
        result = agent_executor.invoke({
            "input": query,
            "chat_history": [],
        })

        # Extract which tools were called (from intermediate steps)
        tools_used = []
        for step in result.get("intermediate_steps", []):
            action = step[0]
            if hasattr(action, "tool"):
                tools_used.append(action.tool)

        return {
            "report":     result.get("output", "No output generated."),
            "tools_used": list(dict.fromkeys(tools_used)),  # Deduplicate
            "error":      None,
        }

    except Exception as e:
        return {
            "report":     "",
            "tools_used": [],
            "error":      str(e),
        }
