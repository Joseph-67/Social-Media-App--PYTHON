#!/usr/bin/env python3
"""
Production startup script using Gunicorn
"""
import os
from website import create_app

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    # For production deployment with Gunicorn
    # Run with: gunicorn -w 4 -b 0.0.0.0:5000 run_production:app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)