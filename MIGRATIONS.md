# Database Migrations with Alembic

This project uses Alembic for database schema migrations.

## Commands

### Initialize migrations (already done)
```bash
alembic init alembic
```

### Create a new migration
```bash
alembic revision -m "description of changes"
```

### Run migrations
```bash
alembic upgrade head
```

### Rollback last migration
```bash
alembic downgrade -1
```

### Show current migration version
```bash
alembic current
```

### Show migration history
```bash
alembic history
```

## Initial Migration

The initial migration (`001_initial_migration.py`) creates:
- `payments` table with id, phone_number, status, timestamp
- `rent_records` table with phone_number, reply, timestamp

## Environment Setup

Make sure `DATABASE_URL` is set in your environment variables before running migrations:

```bash
export DATABASE_URL="postgresql://user:password@host/database"
```

Or add it to your `.env` file (already configured).

## On Render

Migrations can be run automatically on deployment by adding to your build command:
```
pip install -r requirements.txt && alembic upgrade head
```
