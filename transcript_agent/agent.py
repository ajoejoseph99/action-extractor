from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import LlmAgent
from tools import save_task_to_firestore, get_tasks_by_assignee

root_agent = LlmAgent(
    name="action_extractor",
    model="gemini-3-flash",
    tools=[save_task_to_firestore, get_tasks_by_assignee],
    instruction=(
        "You are an AI assistant that manages meeting action items. "
        "1. If given a meeting transcript, extract the action items and use the "
        "`save_task_to_firestore` tool to save them to the database. "
        "2. If a user asks what tasks are assigned to a specific person, use the "
        "`get_tasks_by_assignee` tool to look them up and summarize them."
    )
)