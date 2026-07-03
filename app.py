from agent.prompts import PLANNER_PROMPT

prompt = PLANNER_PROMPT.format(
    request="Create a business proposal for an AI healthcare chatbot."
)

print(prompt)