# Database & Data Ingestion Module

This module contains the complete schema, pgvector setup, and data population pipeline copied from the original prototype.

## Included Files
- \`schema.sql\`: PostgreSQL schema & vector indexes
- \`scripts/setup_db.sh\`: Sets up database and loads extensions
- \`scripts/populate.py\`: Runs data ingestion
- \`scripts/api_verify.py\` & \`demo_match.py\`: Verification & testing

## Setup Instructions
\`\`\`fish
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate.fish
pip install -r requirements.txt
\`\`\`
