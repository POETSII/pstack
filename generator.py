import jinja2

def generate_code(template, content):
    """Generate code from template file and content dict."""
    loader = jinja2.PackageLoader(__name__, 'templates')
    env = jinja2.Environment(loader=loader)
    return env.get_template(template).render(**content)
