# workflows/lead_pipeline.py

from agents.outreach_agent import OutreachAgent
from agents.qualification_agent import QualificationAgent
from agents.conversation_agent_dummy import ConversationAgent
from agents.scheduler_agent import SchedulerAgent

def run_full_pipeline(simulate_replies=True):
    print("\n✉️  Sending outreach emails...")
    outreach = OutreachAgent()
    outreach.send_cold_emails()

    print("\n🧠 Scoring and qualifying leads...")
    qualification = QualificationAgent()
    qualification.score_leads()

    print("\n📨 Handling replies...")
    conversation = ConversationAgent()

    if simulate_replies:
        simulated_replies = conversation.get_reply_summary()
        conversation.simulate_reply_handling(simulated_replies)
    else:
        print("⚠️ No real reply ingestion pipeline yet. Add Gmail integration here.")

    print("\n📅 Scheduling meetings...")
    scheduler = SchedulerAgent()
    meetings = scheduler.schedule_meetings()

    print("\n✅ Pipeline completed.")
    if meetings:
        print("📌 Meetings Scheduled:")
        for m in meetings:
            print(f" - {m['name']} at {m['time']}")
    else:
        print("No meetings scheduled.")

if __name__ == "__main__":
    run_full_pipeline()
