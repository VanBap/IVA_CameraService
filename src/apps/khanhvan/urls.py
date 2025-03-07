from django.urls import path, include
from .views import (
    camera_view,
    camera_group_view,
    camera_alert_view,
    rule_view,
    vlm_model_view,
    prompt_view
)

app_name = ('khanhvan')

# camera
camera_urls = [
    path('', camera_view.CameraListView.as_view()),  # list, create, bulk delete
    path('list', camera_view.CameraFilterView.as_view()), # filter
    path('<int:pk>', camera_view.CameraDetailView.as_view()),
    path('snapshot', camera_view.CameraSnapShotView.as_view()),
]

# camera group
camera_group_urls = [
    path('', camera_group_view.CameraGroupView.as_view()),
    path('<int:pk>', camera_group_view.CameraGroupDetailView.as_view()),
    path('<int:pk>/cameras', camera_group_view.CameraGroupListCameraView.as_view()),

]

# camera alert
camera_alert_urls = [
    path('', camera_alert_view.CameraAlertListView.as_view()),
    path('<int:pk>', camera_alert_view.CameraAlertDetailView.as_view()),

]

# rule
rule_urls = [
    path('', rule_view.RuleListView.as_view()),
    path('<int:pk>', rule_view.RuleDetailView.as_view()),

    path('version', rule_view.RuleVersionView.as_view()),
    path('<int:pk>/versions', rule_view.RuleVersionDetailListView.as_view()),
    path('<int:rule_pk>/versions/<int:version_pk>', rule_view.RuleVersionDetailView.as_view()),

]
# ai model
vlm_model_urls =[
    path('', vlm_model_view.VLMListView.as_view()),
    path('<int:pk>', vlm_model_view.VLMDetailView.as_view()),
]

# prompt
prompt_urls = [
    path('', prompt_view.PromptListView.as_view()),
    path('<int:pk>', prompt_view.PromptDetailView.as_view()),
]


urlpatterns = [
    path('vannhkcameras/', include(camera_urls)),
    path('vannhkcameragroups/', include(camera_group_urls)),
    path('vannhkcameraalerts/', include(camera_alert_urls)),
    path('vannhkcamerarules/', include(rule_urls)),

    path('vannhkvlmmodels/', include(vlm_model_urls)),

    path('vannhkprompts/', include(prompt_urls))
]
