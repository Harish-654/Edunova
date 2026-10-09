# Simple Database Setup (Cross-Platform)

Just two files to get the database running locally on Windows, macOS, or Linux.

## What this does

Creates a PostgreSQL database on port 5433 with:
- Database: `edunova_db`
- User: `edunova_user` 
- Password: `edunova_pass`
- pgvector extension (if available on your system)

## Prerequisites

1. **PostgreSQL installed** and in your PATH
   - Linux: `sudo apt install postgresql`
   - macOS: `brew install postgresql`
   - Windows: [Download from postgresql.org](https://www.postgresql.org/download/windows/) - make sure to check "Add to PATH" during install

## Quick Start

```bash
cd simple_setup
python setup.py
```

That's it! Works on all platforms.

## Connect to the database

```bash
psql -h localhost -p 5433 -U edunova_user -d edunova_db
```

Password: `edunova_pass`

## Add sample data

```bash
pip install -r seed_requirements.txt
python seed.py
```

## Notes

- Creates a local database cluster in `../.data/db` (separate from your system PostgreSQL)
- Uses port 5433 to avoid conflicts with default PostgreSQL (port 5432)
- Schema is loaded automatically from `../schema.sql`
- All code is simple Python - easy to read and explain to your team