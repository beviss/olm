import datetime
import jinja2


def render_template(data, template_filename, output_filename):
    template_loader = jinja2.FileSystemLoader(searchpath="/")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_filename)
    rendered = template.render({'data': data, 'date': datetime.datetime.now().isoformat()})
    output_file = open(output_filename, 'w')
    output_file.write(rendered)
    output_file.close()
