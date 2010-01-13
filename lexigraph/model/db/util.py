class LexigraphModel(db.Model):

    log = ClassLogger()

    def to_python(self):
        d = {'id': self.key().id(), 'kind': self.__class__.__name__}
        for k in self.properties().iterkeys():
            d[k] = getattr(self, k)
        return to_python(d)

