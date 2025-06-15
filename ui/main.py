# ui/main.py

import streamlit as st
import json
import os
import sys

# Allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.prospector_agent import ProspectorAgent
from agents.outreach_agent import OutreachAgent
from agents.qualification_agent import QualificationAgent
# from agents.conversation_agent import ConversationAgent  # ❌ Temporarily disabled due to import error
from agents.human_handoff_agent import HumanHandoffAgent
from workflows.lead_pipeline import run_full_pipeline

st.set_page_config(page_title="SDR Dashboard - Ravian AI", layout="wide")
st.title("📊 SDR Agent Dashboard - Ravian AI")

LEADS_PATH = "data/leads.json"

# --- Load Leads ---
def load_leads():
    if os.path.exists(LEADS_PATH):
        with open(LEADS_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

leads = load_leads()

# --- SECTION 1: Lead Overview ---
st.subheader("📬 Current Leads")

if not leads:
    st.info("No leads found. Add a test lead or run the pipeline.")
else:
    for lead in leads:
        st.markdown(f"""
        **👤 Name**: {lead.get("name")}
        - 🏢 Company: {lead.get("company")}
        - 📨 Email: `{lead.get("email") or "Not available"}`
        - 🧠 Role: {lead.get("role")}`
        - 🏁 Status: `{lead.get("status", "Not yet qualified")}`
        - 💯 Score: `{lead.get("score", "N/A")}`
        - 📈 Sales Stage: `{lead.get("sales_stage", "N/A")}`
        - 💬 LLM Reason: {lead.get("llm_reason", "N/A")}
        ---
        """)

# --- SECTION 2: Full Pipeline Execution ---
st.subheader("⚙️ Run Full SDR Pipeline")
if st.button("🚀 Run Pipeline"):
    with st.spinner("Running SDR agents..."):
        run_full_pipeline()
    st.success("✅ Pipeline executed successfully! Please refresh to see updated leads.")

# --- SECTION 3: Add Manual Test Lead ---
st.subheader("➕ Add a Test Lead")
with st.form("add_lead_form"):
    name = st.text_input("Name")
    company = st.text_input("Company")
    domain = st.text_input("Domain")
    role = st.text_input("Role")
    submitted = st.form_submit_button("Add Lead")

    if submitted:
        if not all([name, company, domain, role]):
            st.warning("Please fill in all fields.")
        else:
            new_lead = {"name": name, "company": company, "domain": domain, "role": role}
            prospector = ProspectorAgent()
            prospector.add_new_leads([new_lead])
            st.success(f"✅ Lead '{name}' added successfully! Refresh to see updates.")

# --- SECTION 4: View LLM-Classified Replies ---
st.subheader("📨 Lead Reply Summaries (LLM-classified)")
st.warning("🛑 Reply classification temporarily disabled due to LLM import issue.")
# try:
#     conversation_agent = ConversationAgent()
#     reply_summary = conversation_agent.get_reply_summary()
#     if not reply_summary:
#         st.info("No classified replies found yet.")
#     else:
#         for r in reply_summary:
#             st.markdown(f"""
#             - 👤 **{r['name']}**
#             - 📨 Email: `{r['email']}`
#             - 🏁 Status: `{r['status']}`
#             - 💡 Reason: {r['reason']}
#             ---
#             """)
# except Exception as e:
#     st.error(f"❌ Error loading ConversationAgent: {e}")

# --- SECTION 5: Route Qualified Leads to Human SDR ---
st.subheader("🧑‍💼 Human Handoff")
if st.button("🤝 Route Qualified Leads to Human"):
    handoff_agent = HumanHandoffAgent()
    handoff_leads = handoff_agent.route_to_human()

    if handoff_leads:
        st.success(f"✅ {len(handoff_leads)} leads handed off to human SDRs.")
        st.json(handoff_leads)
    else:
        st.info("No qualified leads to hand off.")
