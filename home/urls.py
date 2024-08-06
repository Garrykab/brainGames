from django.urls import path
from . import views

urlpatterns = [
    path('add.equipe', views.addEquipe, name='add.equipe'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('delete.equipe', views.deleteEquipe, name='delete.equipe'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('name.equipe.existe', views.checkedNameEquipeExist, name='name.equipe.existe'),
    path('promotion.equipe.existe', views.checkedNameEquipeExist, name='promotion.equipe.existe'),
    path('generator-question-ia', views.generatorQuestionIA, name='generatorQuestionIA'),
    path("equipe.training", views.training, name='equipe.training'),
]