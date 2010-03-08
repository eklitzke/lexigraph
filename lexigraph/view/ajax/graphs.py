from lexigraph.view import add_route
from lexigraph.handler import SessionHandler, TagsMixin

class RenderGraph(TagsMixin, SessionHandler):

    requires_login = True

    def get(self):
        tags = [x.strip() for x in self.request.get('tags').split(',')]
        self.env['names'] = names = self.datasets_by_tags(tags)
        self.render_ajax('ajax/graphs.html', extra={'names': names})
        
add_route(RenderGraph, '/ajax/graphs')
