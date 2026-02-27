# File: ./tools/firestore_tool.py
from google.cloud import firestore

# Initialize the client globally so the container reuses the connection
db = firestore.Client()

def save_task_to_firestore(task_title: str, notes: str = "") -> str:
    """Saves an extracted action item to the Firestore database."""
    try:
        # Create a new document in the 'action_items' collection
        db.collection("action_items").add({
            "title": task_title,
            "notes": notes,
            "status": "pending"
        })
        return f"Success: Task '{task_title}' saved to Firestore."
    except Exception as e:
        return f"Error saving to Firestore: {str(e)}"

def get_tasks_by_assignee(assignee_name: str) -> str:
    """Retrieves action items assigned to a specific person from the database."""
    try:
        # Pull all documents from the action_items collection
        docs = db.collection("action_items").stream()
        tasks = []
        
        for doc in docs:
            data = doc.to_dict()
            # Simple python filter to check if the name is in the title or notes
            if assignee_name.lower() in str(data).lower():
                tasks.append(f"- {data.get('title')}: {data.get('notes')} (Status: {data.get('status')})")
        
        if not tasks:
            return f"I couldn't find any tasks assigned to {assignee_name}."
            
        return "\n".join(tasks)
        
    except Exception as e:
        return f"Error reading from Firestore: {str(e)}"