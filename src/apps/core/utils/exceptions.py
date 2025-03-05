from rest_framework.exceptions import ValidationError


class AreaContainCrossingEdge(ValidationError):
    default_code = 'area_contain_crossing_edge'
    default_detail = 'The area contains crossing edges'


class AreaContainTooShortEdge(ValidationError):
    default_code = 'area_contain_too_short_edge'
    default_detail = 'The area contains a very short edge'


class AreaContainVertexTooCloseEdge(ValidationError):
    default_code = 'area_contain_vertex_too_close_edge'
    default_detail = 'The area contains vertexes which are too close with a edge'


class AreaIsTooSmall(ValidationError):
    default_code = 'area_is_too_small'
    default_detail = 'The area is too small'


class LineIsTooShort(ValidationError):
    default_code = 'line_is_too_short'
    default_detail = 'Invalid line crossing'
