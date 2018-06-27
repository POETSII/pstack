import jinja2


def read_file(file):
    with open(file, 'r') as fid:
        return fid.read()


def generate_code(template, content):

    template_str = read_file(template)

    # Prepare jinja environment
    loader = jinja2.PackageLoader(__name__, '')
    env = jinja2.Environment(loader=loader)
    # env.globals['include'] = include_template_file
    # env.globals.update(env_globals)

    # Return rendered template
    return env.get_template(template).render(**content)
