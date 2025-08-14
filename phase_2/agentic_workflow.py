from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent,
)

import os
from dotenv import load_dotenv

# Load OpenAI key
load_dotenv()
# Also try loading from Phase 1 if needed
try:
    here = os.path.dirname(__file__)
    load_dotenv(os.path.join(here, "..", "phase_1", ".env"))
except Exception:
    pass

openai_api_key = os.getenv("OPENAI_API_KEY")

# load the product spec
spec_path = os.path.join(os.path.dirname(__file__), "Product-Spec-Email-Router.txt")
with open(spec_path, "r", encoding="utf-8") as f:
    product_spec = f.read()

# Instantiate all the agents

# Action Planning Agent
knowledge_action_planning = (
    "Stories are defined from a product spec by identifying a "
    "persona, an action, and a desired outcome for each story. "
    "Each story represents a specific functionality of the product "
    "described in the specification. \n"
    "Features are defined by grouping related user stories. \n"
    "Tasks are defined for each story and represent the engineering "
    "work required to develop the product. \n"
    "A development Plan for a product contains all these components"
)
action_planning_agent = ActionPlanningAgent(openai_api_key, knowledge_action_planning)

# Product Manager - Knowledge Augmented Prompt Agent
persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."
knowledge_product_manager = (
    "Stories are defined by writing sentences with a persona, an action, and a desired outcome. "
    "The sentences always start with: As a "
    "Write several stories for the product spec below, where the personas are the different users of the product. "
    + "\n\nProduct Spec:\n" + product_spec
)
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_product_manager, knowledge_product_manager
)

# Product Manager - Evaluation Agent
pm_eval_persona = "You are an evaluation agent that checks the answers of other worker agents"
pm_eval_criteria = (
    "The answer should be stories that follow the following structure: "
    "As a [type of user], I want [an action or feature] so that [benefit/value]."
)
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key, pm_eval_persona, pm_eval_criteria, product_manager_knowledge_agent, 10
)

# Program Manager - Knowledge Augmented Prompt Agent
persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."
knowledge_program_manager = "Features of a product are defined by organizing similar user stories into cohesive groups."
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_program_manager, knowledge_program_manager
)

# Program Manager - Evaluation Agent
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."
pm_feature_eval_criteria = (
    "The answer should be product features that follow the following structure: "
    "Feature Name: A clear, concise title that identifies the capability\n"
    "Description: A brief explanation of what the feature does and its purpose\n"
    "Key Functionality: The specific capabilities or actions the feature provides\n"
    "User Benefit: How this feature creates value for the user"
)
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key, persona_program_manager_eval, pm_feature_eval_criteria, program_manager_knowledge_agent, 10
)

# Development Engineer - Knowledge Augmented Prompt Agent
persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."
knowledge_dev_engineer = "Development tasks are defined by identifying what needs to be built to implement each user story."
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key, persona_dev_engineer, knowledge_dev_engineer
)

# Development Engineer - Evaluation Agent
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."
dev_task_eval_criteria = (
    "The answer should be tasks following this exact structure: "
    "Task ID: A unique identifier for tracking purposes\n"
    "Task Title: Brief description of the specific development work\n"
    "Related User Story: Reference to the parent user story\n"
    "Description: Detailed explanation of the technical work required\n"
    "Acceptance Criteria: Specific requirements that must be met for completion\n"
    "Estimated Effort: Time or complexity estimation\n"
    "Dependencies: Any tasks that must be completed first"
)
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key, persona_dev_engineer_eval, dev_task_eval_criteria, development_engineer_knowledge_agent, 10
)


# Job function persona support functions
def product_manager_support_function(query: str) -> str:
    generated = product_manager_knowledge_agent.respond(query)
    evaluated = product_manager_evaluation_agent.evaluate(generated)
    return evaluated.get("final_response", generated)


def program_manager_support_function(query: str) -> str:
    generated = program_manager_knowledge_agent.respond(query)
    evaluated = program_manager_evaluation_agent.evaluate(generated)
    return evaluated.get("final_response", generated)


def development_engineer_support_function(query: str) -> str:
    generated = development_engineer_knowledge_agent.respond(query)
    evaluated = development_engineer_evaluation_agent.evaluate(generated)
    return evaluated.get("final_response", generated)


# Routing Agent
routing_agent = RoutingAgent(openai_api_key, {})
routing_agent.agents = [
    {
        "name": "Product Manager",
        "description": (
            "Responsible for defining product personas and user stories only. "
            "Does not define features or tasks. Does not group stories."
        ),
        "func": lambda step: product_manager_support_function(step),
    },
    {
        "name": "Program Manager",
        "description": (
            "Responsible for defining product features only, by grouping related user stories. "
            "Does not define development tasks."
        ),
        "func": lambda step: program_manager_support_function(step),
    },
    {
        "name": "Development Engineer",
        "description": (
            "Responsible for defining development tasks only, based on user stories and features."
        ),
        "func": lambda step: development_engineer_support_function(step),
    },
]


# Run the workflow
print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
workflow_prompt = "What would the development tasks for this product be?"
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

print("\nDefining workflow steps from the workflow prompt")

# Implement the workflow
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)
completed_steps = []

for idx, step in enumerate(workflow_steps, start=1):
    print(f"\n--- Executing step {idx}: {step} ---")
    result = routing_agent.route(step)
    completed_steps.append(result)
    print(f"Step {idx} result:\n{result}\n")

if completed_steps:
    print("Final output of the workflow:\n")
    print(completed_steps[-1])