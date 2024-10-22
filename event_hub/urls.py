from django.urls import path
from . import views

app_name = 'event_hub'
urlpatterns = [
    path("", views.EventListView.as_view(), name='event_list'),
    path("login", views.UserLoginView.as_view(), name='login'),
    path("signup", views.SignUpView.as_view(), name='signup'),
    path("users/<str:username>",
         views.UserDisplayView.as_view(), name='user_display'),
    path("account/edit", views.UserUpdateView.as_view(), name='user_update'),
    path("events/create", views.EventCreateView.as_view(), name='event_create'),
    path("events/<slug:slug>", views.EventDisplayView.as_view(), name='event_display'),
    path("events/update/<slug:slug>",
         views.EventUpdateView.as_view(), name='event_update'),
    path("events/delete/<slug:slug>",
         views.EventDeleteView.as_view(), name='event_delete'),
    path("tags/create", views.tag_create_view, name='tag_create'),
    path("logout", views.UserLogoutView.as_view(), name='logout')
]
