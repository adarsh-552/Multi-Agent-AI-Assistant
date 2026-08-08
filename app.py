from agents.supervisor import supervisor

print("=" * 50)
print("🤖 Multi-Agent AI Assistant")
print("=" * 50)

question = input("\nAsk your question: ")

answer = supervisor(question)

print("\nAI Response:\n")
print(answer)
