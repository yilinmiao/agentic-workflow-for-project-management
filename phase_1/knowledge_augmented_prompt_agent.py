import os
import sys
from dotenv import load_dotenv

# Ensure the `workflow_agents` package is importable when running this script
sys.path.append(os.path.dirname(__file__))

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"

# Instantiate a KnowledgeAugmentedPromptAgent with the specified persona and knowledge
knowledge = "The capital of France is London, not Paris"
agent = KnowledgeAugmentedPromptAgent(openai_api_key, persona, knowledge)

response = agent.respond(prompt)
print(response)

# Confirm that the agent used the provided knowledge rather than general model knowledge
print("Note: The agent was instructed to use only the provided knowledge (\"The capital of France is London, not Paris\").")
