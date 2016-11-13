from django.conf.urls import include, url
from .views import DonnaBot, AITasks

urlpatterns = [
    url(r'^eda9871d5f3b03e41012dbfdff1f8eccb7c5e171c7b4031759/?$', DonnaBot.as_view()),
    url(r'^b4c83fda2c82768e5fc16f7164d13fef5e6abbf767ba110215/?$', AITasks.as_view())
]
