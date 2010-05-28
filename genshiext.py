
from flask import Flask, current_app
from werkzeug import cached_property
from genshi.template import TemplateLoader, loader


class GenshiFlask(Flask):

    def __init__(self, *args, **kwargs):
        Flask.__init__(self, *args, **kwargs)
        self.config.update(
            GENSHI_LOADER=dict(auto_reload=True),
            GENSHI_TEMPLATES_PATH='templates',
            GENSHI_DEFAULT_DOCTYPE='html',
            GENSHI_DEFAULT_METHOD='html',
            GENSHI_DEFAULT_TYPE='html',
            GENSHI_TYPES={
                'html': dict(method='html', doctype='html',
                             mimetype='text/html'),
                'html5': dict(method='html', doctype='html5',
                              mimetype='text/html'),
                'xhtml': dict(method='xhtml', doctype='xhtml',
                              mimetype='application/xhtml+xml'),
                'xml': dict(method='xml', mimetype='application/xml'),
                'text': dict(method='text', mimetype='text/plain')
            }
        )

    @cached_property
    def genshi_loader(self):
        path = loader.package(self.import_name,
                              self.config['GENSHI_TEMPLATES_PATH'])
        return TemplateLoader(path, **self.config['GENSHI_LOADER'])


def render_template(template_name, context, **render_args):
    """Render a Genshi template under GENSHI_TEMPLATES_PATH."""
    for k, v in current_app.jinja_env.globals.iteritems():
        context.setdefault(k, v)
    context.setdefault('filters', current_app.jinja_env.filters)
    context.setdefault('tests', current_app.jinja_env.tests)

    render_args.setdefault('method',
                           current_app.config['GENSHI_DEFAULT_METHOD'])
    if render_args['method'] not in ('xml', 'text'):
        render_args.setdefault('doctype',
                               current_app.config['GENSHI_DEFAULT_DOCTYPE'])

    template = current_app.genshi_loader.load(template_name)
    return template.generate(**context).render(**render_args)


def render_response(template, context={}, type=None):
    """Render to a Response with correct mimetype."""
    config = current_app.config
    if type is None:
        type = config['GENSHI_TYPES'][config['GENSHI_DEFAULT_TYPE']]
    else:
        type = config['GENSHI_TYPES'][type]

    render_args = dict(method=type['method'])
    if 'doctype' in type:
        render_args['doctype'] = type['doctype']

    body = render_template(template, context, **render_args)
    return current_app.response_class(body, mimetype=type['mimetype'])

