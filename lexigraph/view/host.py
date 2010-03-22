from lexigraph.view import add_route
from lexigraph.handler import AccountHandler, SessionHandler, InteractiveHandler
from lexigraph import model
from lexigraph.model import maybe_one
from django.utils import simplejson

class NewHost(SessionHandler):

    requires_login = True

    def create_series(self):
        pass

    def post(self):
        hostname = self.form_required('hostname')
        host_class = self.request.get('host_class')
        group = self.request.get('group')
        populate = self.request.get('populate', False)

        if not group:
            groups = model.AccessGroup.all().filter('account =', self.account)
            for group in groups:
                if self.user.user_id() in group.users:
                    break
            else:
                raise ValueError("Failed to see user %s in any groups" % (self.user,))
        else:
            group = model.AccessGroup.decode(group)

        def new_dataset(name, aggregate, tags=[]):
            ds = model.DataSet(name=name, hostname=hostname, aggregate=aggregate, account=self.account, tags=tags)
            ds.put()

            access = model.AccessControl.new(group, ds, read=True, write=True, delete=True)
            access.put()

            model.DataSeries(dataset=ds, interval=60, max_age=86400).put()
            return ds

        def new_composite(name, datasets, tags=[]):
            dataset_ids = [ds.key().id() for ds in datasets]
            model.CompositeDataSet(name=name, datasets=dataset_ids, tags=tags, account=self.account, hostname=datasets[0].hostname).put()

        if populate == 'on':
            new_composite('load', [
                    new_dataset('load1', 'max', ['load']),
                    new_dataset('load5', 'max', ['load']),
                    new_dataset('load15', 'max', ['load']),
                    new_dataset('cpu_count', 'new', ['load', 'cpu'])],
                          ['dashboard', 'load'])
            new_composite('cpu', [
                    new_dataset('cpu_total', 'min', ['cpu']),
                    new_dataset('cpu_user', 'max', ['cpu']),
                    new_dataset('cpu_system', 'max', ['cpu']),
                    new_dataset('cpu_nice', 'max', ['cpu']),
                    new_dataset('cpu_iowait', 'max', ['cpu'])],
                          ['dashboard', 'cpu'])
            new_composite('memory', [
                    new_dataset('mem_total', 'new', ['mem']),
                    new_dataset('mem_buffers', 'new', ['mem']),
                    new_dataset('mem_cached', 'new', ['mem']),
                    new_dataset('mem_resident', 'new', ['mem']),
                    new_dataset('mem_used', 'new', ['mem'])],
                          ['dashboard', 'mem'])

        self.redirect('/dashboard')

add_route(NewHost, '/new/host')
