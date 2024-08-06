from django.contrib import admin
from django.urls import path
from home.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name='home'),
    path("about", about, name='about'),
    path("login", user_login, name='login'),
    path("logout", user_logout, name='logout'),
    path("dashboard", dashboard, name='dashboard'),
    path("edit.equipe", editEquipe, name='edit.equipe'),
    path("add.equipe", addEquipe, name='add.equipe'),
    path("delete.equipe", deleteEquipe, name='delete.equipe'),
    path("name.equipe.existe", checkedNameEquipeExist, name='name.equipe.existe'),
    path("promotion.equipe.existe", checkedPromotionEquipeExist, name='promotion.equipe.existe'),
    path("questionnaire", questionnaire, name='questionnaire'),
    path('generator-question-ia', generatorQuestionIA, name='generatorQuestionIA'),
    path("add.question", addQuestion, name='add.question'),
    path("add.question.csv", addQuestionCSV, name='add.question.csv'),
    path("delete.question", deleteQuestion, name='delete.question'),
    path("delete.all.question", deleteAllQuestion, name='delete.all.question'),
    path("configs", configurations, name='configs'),
    path("equipe.training", training, name='equipe.training'),
    path("submit.training", submitTraining, name='submit.training'),
]
