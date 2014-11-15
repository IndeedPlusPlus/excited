from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
                       url(r'^register/', views.register, name='register'),
                       url(r'^login/', views.login, name='login'),
                       url(r'^create-item/', views.create_item, name='create_item'),
                       url(r'^get-items/', views.get_items, name='get_items'),
                       url(r'^pick-item/', views.get_items, name='pick_item'),
)