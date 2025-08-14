import os
import sys
from dotenv import load_dotenv

# Ensure the `workflow_agents` package is importable when running this script
sys.path.append(os.path.dirname(__file__))

from workflow_agents.base_agents import AugmentedPromptAgent

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# Instantiate an object of AugmentedPromptAgent with the required parameters
agent = AugmentedPromptAgent(openai_api_key, persona)

# Send the 'prompt' to the agent and store the response in a variable named 'augmented_agent_response'
augmented_agent_response = agent.respond(prompt)

# Print the agent's response
print(augmented_agent_response)

# Explanation:
# - Knowledge used: The agent relied on the general world knowledge of the LLM (gpt-3.5-turbo).
# - Persona effect: The system prompt enforced the "college professor" persona, so the response should begin with
#   "Dear students," and maintain a professor-like tone.
