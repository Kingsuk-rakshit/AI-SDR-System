# agents/conversation_agent_dummy.py

class ConversationAgent:
    def __init__(self, *args, **kwargs):
        print("✅ Dummy ConversationAgent initialized for testing.")

    def get_reply_summary(self):
        return [
            {
                "name": "Alice Johnson",
                "email": "alice@acmecorp.com",
                "status": "interested",
                "reason": "Interested in learning more about Newton AI’s automation features."
            },
            {
                "name": "Bob Smith",
                "email": "bob@betaindustries.io",
                "status": "not_interested",
                "reason": "Already using a competitor and not looking to switch."
            },
            {
                "name": "Carol Lee",
                "email": "carol@datahero.com",
                "status": "book_meeting",
                "reason": "Asked for a Calendly link to schedule a demo next week."
            },
            {
                "name": "David Wong",
                "email": "david@insightly.io",
                "status": "reply_received",
                "reason": "Thanks for reaching out. Will discuss with the team and get back."
            },
            {
                "name": "Evelyn Zhang",
                "email": "evelyn@analyticsplus.ai",
                "status": "unclear",
                "reason": "Generic reply without clear intent: 'Looks interesting, tell me more.'"
            }
        ]

    def simulate_reply_handling(self, replies):
        print("📩 Simulating reply handling with dummy data:")
        for reply in replies:
            print(f"- {reply['name']} ({reply['status']}): {reply['reason']}")
