class AdvancedAPIMixin(object):
    def get_serializer_class(self, instance=None):
        if self.request.method == 'GET' and 'pk' not in self.kwargs:
            return self.condensed_serializer
        elif instance:
            return self.full_serializer
        else:
            if hasattr(self, 'create_serializer'):
                return self.create_serializer
            return self.full_serializer
