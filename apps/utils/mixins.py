PUBLIC = 'public'
PRIVATE = 'private'
ORG_ONLY = 'org-only'
ORG_ONLY_NO_EXTERNAL = 'org-only-no-external'
VISIBILTY_CHOICES = (
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
    (ORG_ONLY, 'Organization only'),
    (ORG_ONLY_NO_EXTERNAL, 'Organization only (No external)'),
)


class VisibilityMixin(object):
    """Mixin that adds some functionality for controlling visibility of
    objects.  Requires organization and primary_organization to be
    defined on object."""

    @classmethod
    def get_available_to_user(cls, user):
        primary = user.get_primary_org()
        objs = cls.objects.filter(primary_organization=primary)
        ids = []
        # Public
        ids.extend(objs.filter(visibility=PUBLIC).values('pk'))
        # Private
        related = cls.shared_with.field.related.get_accessor_name()
        manager = getattr(user, related)
        ids.extend((objs.filter(visibility=PRIVATE) &
                   manager.all()).values('pk'))
        # Org only
        ids.extend(
            objs.filter(
                visibility=ORG_ONLY,
                organization__in=user.organizations.all()
            ).values('pk')
        )
        # Org only except for external
        if not user.external:
            ids.extend(cls.objects.filter(
                visibility=ORG_ONLY_NO_EXTERNAL,
                organization__in=user.organizations.all()).values('pk'))
        ids = map(lambda x: x['pk'], ids)
        return cls.objects.filter(pk__in=ids)
