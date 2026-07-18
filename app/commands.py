"""Custom Flask CLI commands."""
import click
from flask import Flask
from app import db
from app.models import Item

def hello() -> None:
    """Register custom commands with the Flask CLI."""
    pass

@click.command('seed-db')
def seed_db() -> None:
    """Seed the database with sample data."""
    sample_items = [
        ('Python Basics', 'Learn Python fundamentals'),
        ('Flask Web Development', 'Build web applications with Flask'),
        ('Database Design', 'Learn SQL and database design patterns'),
        ('RESTful APIs', 'Design and build RESTful APIs'),
        ('Testing Python Apps', 'Write tests for Python applications'),
    ]
    
    for name, description in sample_items:
        item = Item(name=name, description=description)
        db.session.add(item)
    
    db.session.commit()
    click.echo(f'Added {len(sample_items)} sample items to the database!')