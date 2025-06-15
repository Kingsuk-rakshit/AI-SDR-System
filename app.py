# app.py

from flask import Flask, render_template, request, redirect, url_for
import os
import sys
import json

# Allow relative imports for agent modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from agents.prospector_agent import ProspectorAgent
from agents.outreach_agent import OutreachAgent
from agents.qualification_agent import QualificationAgent
from agents.human_handoff_agent import HumanHandoffAgent
from workflows.lead_pipeline import run_full_pipeline

app = Flask(__name__)
LEADS_PATH = "data/leads.json"

# Utility to load saved leads
def load_leads():
    if os.path.exists(LEADS_PATH):
        with open(LEADS_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# ------------------------ ROUTES ------------------------

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return redirect("https://www.ravian.ai", code=302)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    leads = load_leads()
    message = ""
    added = False

    if request.method == "POST":
        # Handle run pipeline request
        if "run_pipeline" in request.form:
            try:
                run_full_pipeline()
                message = "✅ Pipeline executed successfully!"
            except Exception as e:
                message = f"❌ Pipeline error: {e}"

        # Handle add lead form
        elif "add_lead" in request.form:
            name = request.form.get("name")
            company = request.form.get("company")
            domain = request.form.get("domain")
            role = request.form.get("role")

            if not all([name, company, domain, role]):
                message = "⚠️ Please fill in all fields."
            else:
                new_lead = {"name": name, "company": company, "domain": domain, "role": role}
                prospector = ProspectorAgent()
                prospector.add_new_leads([new_lead])
                added = True
                message = f"✅ Lead '{name}' added successfully!"

    return render_template("dashboard.html", leads=load_leads(), message=message, added=added)

@app.route('/handoff')
def human_handoff():
    agent = HumanHandoffAgent()
    handoff_leads = agent.route_to_human()
    return render_template("handoff.html", leads=handoff_leads)

# ------------------------ RUN SERVER ------------------------

if __name__ == "__main__":
    app.run(debug=True)
