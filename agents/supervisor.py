from agents.pdf_agent import pdf_agent
from agents.search_agent import search_agent
from agents.code_agent import code_agent
from agents.calculator_agent import calculator_agent
from agents.memory_agent import memory_agent


def supervisor(query):

    query = query.lower()

    if "pdf" in query or "document" in query:
        return pdf_agent(query)

    elif "news" in query or "latest" in query:
        return search_agent(query)

    elif "python" in query or "code" in query or "java" in query:
        return code_agent(query)

    elif "calculate" in query or "math" in query:
        return calculator_agent(query)

    # 👇 NEW CODE
    elif "my name is" in query or "remember" in query:
        return memory_agent(query)

    elif "what is my name" in query:
        return memory_agent(query)

    else:
        return "❌ Sorry, I don't know which agent should handle this request."