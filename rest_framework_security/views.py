class IsOwnerViewSetMixin:
    def get_queryset(self):
        queryset = super(IsOwnerViewSetMixin, self).get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        else:
            return queryset.filter(user=self.request.user)
