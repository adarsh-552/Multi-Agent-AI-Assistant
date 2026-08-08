import json
import os

MEMORY_FILE = "memory.json"


def load_memory():

    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as file:
            return json.load(file)

    return {}


def save_memory(memory):

    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def memory_agent(query):

    memory = load_memory()

    query = query.lower()

    # Save Name
    if "my name is" in query:

        name = query.replace("my name is", "").strip()

        memory["name"] = name

        save_memory(memory)

        return f"😊 Nice to meet you {name}! I'll remember your name."

    # Recall Name
    elif "what is my name" in query:

        if "name" in memory:
            return f"Your name is {memory['name']}."

        return "I don't know your name yet."

    return "Memory Agent is active."