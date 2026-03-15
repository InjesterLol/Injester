"""Auto-generate benchmark questions and agent tasks for any website using LLM.

When a user provides an arbitrary URL (not united/airbnb), we use the extracted
content to generate relevant benchmark questions and agent task definitions.
"""

import json

import openai

from app.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

nebius_client = openai.OpenAI(
    api_key=NEBIUS_API_KEY,
    base_url=NEBIUS_BASE_URL,
)


def generate_questions(content: str, num_questions: int = 5, objective: str | None = None) -> list[str]:
    """Generate benchmark questions from page content, optionally focused on an objective."""
    objective_clause = ""
    if objective:
        objective_clause = f"""
The user's objective is: "{objective}"
Focus the questions on information the agent would need to accomplish this objective.
"""

    prompt = f"""Given this webpage content, generate {num_questions} questions that an AI agent
should be able to answer after reading an optimized version of this page.
The questions should test whether the restructured content preserves key information
like page structure, available actions, navigation options, pricing, and important details.
{objective_clause}
Return ONLY a JSON array of question strings. No markdown fencing.

Content (first 4000 chars):
{content[:4000]}"""

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    try:
        questions = json.loads(raw)
        if isinstance(questions, list):
            return [q for q in questions if isinstance(q, str)][:num_questions]
    except json.JSONDecodeError:
        pass

    # Fallback: generic questions
    return [
        "What is the main purpose of this page?",
        "What are the key prices or costs mentioned?",
        "What actions can a user take on this page?",
        "What are the important dates or deadlines?",
        "What contact information is available?",
    ]


def generate_agent_tasks(content: str) -> list[dict]:
    """Generate agent task definitions from page content.

    Returns tasks in the same format as agent_tasks.py TASK_SETS entries.
    """
    prompt = f"""Given this webpage content, generate 5 tasks that an AI booking/browsing agent
should attempt on this page. Each task should have realistic actions like clicking buttons,
filling forms, or reading information.

Return ONLY valid JSON — an array of task objects with this structure:
[
  {{
    "id": "short_snake_case_id",
    "name": "Human readable task name",
    "description": "What the agent should do",
    "actions": [
      {{"type": "read", "target": "what to read"}},
      {{"type": "click", "target": "what to click"}},
      {{"type": "fill", "target": "field to fill", "value": "value to enter"}}
    ],
    "success_condition": "How to verify the task succeeded"
  }}
]

Tasks should progress from simple (reading info) to complex (completing a transaction).
Use realistic mock data for any form values (names, emails, dates).
No markdown fencing in your response.

Content (first 4000 chars):
{content[:4000]}"""

    response = nebius_client.chat.completions.create(
        model=NEBIUS_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    try:
        tasks = json.loads(raw)
        if isinstance(tasks, list) and len(tasks) > 0:
            return tasks[:5]
    except json.JSONDecodeError:
        pass

    # Fallback: generic browsing tasks
    return [
        {
            "id": "read_page",
            "name": "Read page content",
            "description": "Read and understand the main content of the page",
            "actions": [{"type": "read", "target": "main page content"}],
            "success_condition": "Page content is visible and readable",
        },
        {
            "id": "find_key_info",
            "name": "Find key information",
            "description": "Locate prices, dates, or important details",
            "actions": [{"type": "read", "target": "prices or key details"}],
            "success_condition": "Key information found on the page",
        },
        {
            "id": "find_action",
            "name": "Find primary action",
            "description": "Locate the main call-to-action button or link",
            "actions": [{"type": "read", "target": "primary action button"}],
            "success_condition": "Primary action button or link identified",
        },
        {
            "id": "interact",
            "name": "Interact with the page",
            "description": "Click the main action button or fill a form",
            "actions": [{"type": "click", "target": "primary action button"}],
            "success_condition": "Page responded to interaction",
        },
        {
            "id": "verify_result",
            "name": "Verify result",
            "description": "Check that the interaction produced a meaningful result",
            "actions": [{"type": "read", "target": "result or confirmation"}],
            "success_condition": "Result or next step is visible",
        },
    ]
