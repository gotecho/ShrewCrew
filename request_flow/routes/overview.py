import os
from flask import Blueprint, render_template
from request_flow.services.firestore_service import get_all_cases
from request_flow.services.salesforce_service import get_case_status
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask blueprint
overview_bp = Blueprint('overview_bp', __name__)

# valid categories
VALID_CATEGORIES = [
    "Abandoned Vehicle",
    "Dead Animal",
    "Junk Pickup",
    "General Report",
    "Q&A",
    "Case Switching",
    "Case Selection Fallback"
]

@overview_bp.route('/overview', methods=['GET'])
def get_overview():
    try:
        # Step 1: Retrieve case data from Firestore
        cases = get_all_cases()
        if not cases:
            return "<h2>No cases found</h2>"

        # Step 2: Categorize cases by type and status
        categorized_data = defaultdict(list)
        summary_data = defaultdict(int)

        for case in cases:
            # Pull type from Salesforce or Firestore
            case_type = case.get('type') or "Unknown"
            status = case.get('status', 'Unknown')
            user = case.get('user', 'Anonymous')

            # Use Salesforce 'Subject' if available
            if case_type == "Unknown":
                case_id = case.get('case_id')
                sf_data = get_case_status(case_id)
                case_type = sf_data.get("subject", "Other")

            # Ensure only valid categories are counted
            if case_type not in VALID_CATEGORIES:
                case_type = "Other"

            # Group cases by type
            categorized_data[case_type].append({
                'case_id': case.get('case_id'),
                'status': status,
                'description': case.get('description'),
                'user': user
            })

            # Count cases by type
            summary_data[case_type] += 1

        # Step 3: Render to HTML using Flask template
        return render_template(
            'overview.html',
            total_cases=len(cases),
            case_summary=summary_data,
            categorized_cases=categorized_data
        )

    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"