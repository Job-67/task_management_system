from abc import ABC, abstractmethod

class TaskStorage(ABC):
    @abstractmethod
    def load_tasks(self):
        pass

    @abstractmethod
    def save_tasks(self, tasks):
        pass

class FileTaskStorage(TaskStorage):
    def __init__(self, filename="tasks.txt"):
        self.filename = filename

    def load_tasks(self):
        loaded_tasks = []
        try:
            with open(self.filename, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 4:
                        task_id = int(parts[0])
                        description = parts[1]
                        due_date = parts[2] if parts[2] != 'None' else None
                        completed = parts[3] == 'True'
                        # Handle priority - default to 'medium' if not present
                        priority = parts[4] if len(parts) > 4 else 'medium'
                        loaded_tasks.append(Task(task_id, description, due_date, completed, priority))
        except FileNotFoundError:
            print(f"No existing task file '{self.filename}' found. Starting fresh.")
        return loaded_tasks

    def save_tasks(self, tasks):
        with open(self.filename, "w") as f:
            for task in tasks:
                f.write(f"{task.id},{task.description},{task.due_date},{task.completed},{task.priority}\n")
        print(f"Tasks saved to {self.filename}")

class Task:
    def __init__(self, task_id, description, due_date=None, completed=False, priority='medium'):
        self.id = task_id
        self.description = description
        self.due_date = due_date
        self.completed = completed
        self.priority = priority.lower() if priority else 'medium'
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high']
        if self.priority not in valid_priorities:
            print(f"Warning: Invalid priority '{priority}'. Setting to 'medium'.")
            self.priority = 'medium'

    def mark_completed(self):
        self.completed = True
        print(f"Task {self.id} '{self.description}' marked as completed.")

    def __str__(self):
        status = "✓" if self.completed else " "
        due = f" (Due: {self.due_date})" if self.due_date else ""
        
        # Priority display with visual indicators
        priority_indicators = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        priority_display = f" [{priority_indicators.get(self.priority, '🟡')} {self.priority.upper()}]"
        
        return f"[{status}] {self.id}. {self.description}{due}{priority_display}"
    
class TaskManager:
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.tasks = self.storage.load_tasks()
        self.next_id = max([t.id for t in self.tasks] + [0]) + 1 if self.tasks else 1
        print(f"Loaded {len(self.tasks)} tasks. Next ID: {self.next_id}")

    def add_task(self, description, due_date=None, priority='medium'):
        task = Task(self.next_id, description, due_date, False, priority)
        self.tasks.append(task)
        self.next_id += 1
        self.storage.save_tasks(self.tasks)
        print(f"Task '{description}' added with priority: {priority.upper()}")
        return task

    def list_tasks(self):
        print("\n--- Current Tasks ---")
        if not self.tasks:
            print("No tasks available.")
            return
        
        # Sort tasks by priority (high -> medium -> low) and then by completion status
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_tasks = sorted(self.tasks, 
                            key=lambda t: (t.completed, -priority_order.get(t.priority, 2)))
        
        for task in sorted_tasks:
            print(task)
        print("---------------------")

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def mark_task_completed(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            task.mark_completed()
            self.storage.save_tasks(self.tasks)
            return True
        print(f"Task {task_id} not found.")
        return False

    def list_tasks_by_priority(self, priority):
        """List tasks filtered by specific priority"""
        filtered_tasks = [task for task in self.tasks if task.priority == priority.lower()]
        print(f"\n--- {priority.upper()} Priority Tasks ---")
        if not filtered_tasks:
            print(f"No {priority.lower()} priority tasks found.")
            return
        
        for task in filtered_tasks:
            print(task)
        print("---------------------")
    
if __name__ == "__main__":
    file_storage = FileTaskStorage("my_tasks.txt")
    manager = TaskManager(file_storage)
    
    # Display current tasks
    manager.list_tasks()
    
    # Add tasks with different priorities
    manager.add_task("Review SOLID Principles", "2024-08-10", "high")
    manager.add_task("Prepare for Final Exam", "2024-08-15", "high")
    manager.add_task("Read Python documentation", "2024-08-20", "medium")
    manager.add_task("Organize workspace", priority="low")  # No due date
    
    # List all tasks (will be sorted by priority)
    manager.list_tasks()
    
    # Mark a task as completed
    manager.mark_task_completed(1)
    
    # List all tasks again to see the change
    manager.list_tasks()
    
    # List tasks by specific priority
    manager.list_tasks_by_priority("high")
    manager.list_tasks_by_priority("low")