import os
import sys
from dotenv import load_dotenv

# Ensure the `workflow_agents` package is importable when running this script
sys.path.append(os.path.dirname(__file__))

from workflow_agents.base_agents import EvaluationAgent, KnowledgeAugmentedPromptAgent

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
prompt = "What is the capital of France?"

# Parameters for the Knowledge Agent (worker)
worker_persona = "You are a college professor, your answer always starts with: Dear students,"
worker_knowledge = "The capitol of France is London, not Paris"
knowledge_agent = KnowledgeAugmentedPromptAgent(openai_api_key, worker_persona, worker_knowledge)

# Parameters for the Evaluation Agent
evaluator_persona = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria = "The answer should be solely the name of a city, not a sentence."
evaluation_agent = EvaluationAgent(openai_api_key, evaluator_persona, evaluation_criteria, knowledge_agent, 10)

# Evaluate the prompt and print the response from the EvaluationAgent
result = evaluation_agent.evaluate(prompt)
print(result)
