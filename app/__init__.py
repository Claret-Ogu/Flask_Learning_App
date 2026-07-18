"""Flask application factory module."""
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config

# Initialize extensions
db: SQLAlchemy = SQLAlchemy()
csrf: CSRFProtect = CSRFProtect()

def create_app(config_name: str = 'default') -> Flask:
    """Application factory pattern for scalability.
    
    Args:
        config_name: The configuration environment to use
        
    Returns:
        A configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    
    # Register blueprints (for modularity)
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app