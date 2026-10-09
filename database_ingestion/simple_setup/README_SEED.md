# Simple Database Seeding

Add sample exam data to the database with minimal code.

## Prerequisites

- Database must be set up first (`./setup.sh` from simple_setup/)
- Python 3 installed

## Quick Start

```bash
cd simple_setup
pip install -r seed_requirements.txt
python3 seed.py
```

That's it - sample exams, scholarships, and scraping sources will be added.

## What gets added

- 10+ Indian entrance exams (JEE, NEET, CUET, CAT, GATE, etc.)
- 7 scholarships linked to relevant exams
- NTA scraping sources
- Basic data to test with

## View the data

```bash
psql -h localhost -p 5433 -U edunova_user -d edunova_db
# Then run: SELECT * FROM exams;
```