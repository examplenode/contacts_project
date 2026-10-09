from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("db/", views.db_list, name="db_list"),
    path("ajax/search/", views.ajax_search, name="ajax_search"),
    path("db/<int:pk>/edit/", views.edit_contact, name="edit_contact"),
    path("db/<int:pk>/delete/", views.delete_contact, name="delete_contact"),
]