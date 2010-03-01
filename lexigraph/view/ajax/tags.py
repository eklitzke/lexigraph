import re

from lexigraph.view import add_route
from lexigraph.handler import SessionHandler
from lexigraph import model
from lexigraph.model.query import *

from lexigraph.view.ajax.graphs import TagQueryCache

class TagBase(SessionHandler):

    requires_login = True

    def parse_form(self):
        self.name = self.form_required('name')
        dataset = self.form_required('dataset')

        self.dataset = maybe_one(model.DataSet.all().filter('name =', dataset).filter('account =', self.account))
        assert self.dataset
        assert self.dataset.is_allowed(write=True)
       
    def finish(self):
        # XXX: break the tags cache

        # get the new color list
        self.env['tags'] = model.TagColors.colors_for_tags(self.user, self.dataset.tags)
        
        extra_tags = [{'name': tag.name, 'red': tag.red, 'blue': tag.blue, 'green': tag.green} for tag in self.env['tags']]
        self.render_ajax('ajax/tags.html', extra={'tags': extra_tags})

class AddTag(TagBase):

    def post(self):
        self.parse_form()

        assert self.name not in self.dataset.tags
        self.dataset.tags.append(self.name)
        self.dataset.put()

        self.finish()

class RemoveTag(TagBase):

    def post(self):
        self.parse_form()

        assert self.name in self.dataset.tags
        self.dataset.tags.remove(self.name)
        self.dataset.put()

        self.finish()
 
add_route(AddTag, '/ajax/add/tag')
add_route(RemoveTag, '/ajax/remove/tag')
