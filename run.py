#!/usr/bin/env python
"""Application entry point."""
import os
from app import create_app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'default'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)