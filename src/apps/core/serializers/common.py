from rest_framework import serializers


class PointField(serializers.ListField):
    child = serializers.FloatField()

    def __init__(self, **kwargs):
        kwargs['max_length'] = 2
        kwargs['min_length'] = 2
        super().__init__(**kwargs)


class LineField(serializers.ListField):
    child = PointField()

    def __init__(self, **kwargs):
        kwargs['max_length'] = 2
        kwargs['min_length'] = 2
        super().__init__(**kwargs)


class PolygonField(serializers.ListField):
    child = PointField()

    def __init__(self, **kwargs):
        kwargs['min_length'] = 3
        super().__init__(**kwargs)
