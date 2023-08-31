import datetime
import time
import threading

class ReleaseStep:
    def __init__(self, name, estimated_duration):
        self.name = name
        self.estimated_duration = estimated_duration
        self.start_time = None
        self.end_time = None

class ReleasePlan:
    def __init__(self):
        self.steps = []

    def add_step(self, step: ReleaseStep):
        self.steps.append(step)

class ReleaseEngine:
    def __init__(self, release_plan: ReleasePlan):
        self.release_plan = release_plan
        self.stakeholders = []

    def add_stakeholder(self, email):
        self.stakeholders.append(email)

    def start_step(self, step: ReleaseStep):
        step.start_time = datetime.datetime.now()
        print(f"Starting step: {step.name}")

    def complete_step(self, step: ReleaseStep):
        step.end_time = datetime.datetime.now()
        print(f"Completed step: {step.name}")
        print(f"Duration: {step.end_time - step.start_time}")

    def execute_release_step(self, step: ReleaseStep):
        self.start_step(step)
        time.sleep(step.estimated_duration)  # Simulating step execution time
        self.complete_step(step)

    def execute_release(self):
        print("Release execution started.")
        for step in self.release_plan.steps:
            self.execute_release_step(step)
            print("=" * 40)
        print("Release execution completed.")
        self.notify_stakeholders()

    def notify_stakeholders(self):
        print("Notifying stakeholders about release completion.")
        for email in self.stakeholders:
            print(f"Notifying {email}...")
            # Implement notification logic here, such as sending emails.
            time.sleep(1)  # Simulating notification time
            print(f"Notification sent to {email}")

def main():
    # Create release steps
    steps = [
        ReleaseStep("Code Compilation", 2),
        ReleaseStep("Database Migration", 3),
        ReleaseStep("Testing", 4),
        ReleaseStep("Deployment", 2),
    ]

    # Create release plan and add steps
    release_plan = ReleasePlan()
    for step in steps:
        release_plan.add_step(step)

    # Create and configure release engine
    release_engine = ReleaseEngine(release_plan)
    release_engine.add_stakeholder("stakeholder1@example.com")
    release_engine.add_stakeholder("stakeholder2@example.com")

    # Execute release in a separate thread to allow for notifications to be sent concurrently
    release_thread = threading.Thread(target=release_engine.execute_release)
    release_thread.start()
    release_thread.join()

if __name__ == "__main__":
    main()
