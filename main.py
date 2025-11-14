from website import create_app
from markupsafe import Markup  

app = create_app()

def nl2br(value):
    """Custom filter function to convert newlines to <br> tags."""
    try:
        paragraphs = value.split('\n')
        paragraphs_html = '<br>'.join(paragraphs)
        return Markup(paragraphs_html)  
    except AttributeError:
        return '' 

# Register the custom Jinja filter
app.jinja_env.filters['nl2br'] = nl2br

if __name__ == "__main__":
    import os
    # Get port from environment variable (for deployment) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # For local network access, use host='0.0.0.0'
    # For production, set debug=False
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
