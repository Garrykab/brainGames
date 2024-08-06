from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Equipe, Questions, Configurations, Trainings
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
import ollama
import csv
import uuid
from datetime import date
import smtplib
from email.message import EmailMessage

def home(request):
    equipes = Equipe.objects.all()
    questions = Questions.objects.all()
    context = {'equipes': equipes, 'questions': questions, 'current_page': 'home'}
    return render(request, "index.html", context)

def about(request):
    return render(request, "about.html", {'current_page': 'about'})

def user_login(request):
    if request.user.is_authenticated:
        return render(request, "dashboard.html", {'current_page': 'dashboard'})
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('dashboard')
        
        messages.error(request, "Nom utilisateur ou mot de passe incorrect.")
        return render(request, "auth.html", {'current_page': 'login'})
    
    return render(request, "auth.html", {'current_page': 'login'})

@login_required
def dashboard(request):
    equipes = Equipe.objects.all()
    questions = Questions.objects.all()
    configs = Configurations.objects.first()
    
    context = {
        'equipes': equipes, 
        'questions': questions, 
        'configs': configs, 
        'current_page': 'dashboard'
    }
    return render(request, "dashboard.html", context)

@login_required
def editEquipe(request):
    token = request.GET.get('token')
    try:
        equipe = Equipe.objects.get(token=token)
    except Equipe.DoesNotExist:
        messages.error(request, "Équipe non trouvée.")
        return redirect('dashboard')
    
    context = {
        'equipe': equipe,
        'current_page': 'dashboard'
    }
    return render(request, "edit-equipe.html", context)

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def addEquipe(request):
    if request.method == "POST":
        nom = request.POST.get('name-equipe').lower()
        promotion = request.POST.get('promotion-equipe').lower()
        email = request.POST.get('email').lower()
        token = str(uuid.uuid4())
        
        try:
            with transaction.atomic():
                equipe = Equipe(name=nom, promotion=promotion, token=token)
                equipe.save()
                send_email(request, email, token)
                messages.success(request, "Équipe ajoutée avec succès.")
        except Exception as e:
            transaction.rollback()
            messages.error(request, f"Erreur lors de l'ajout de l'équipe: {str(e)}")
        
        return redirect('dashboard')

@login_required
def deleteEquipe(request):
    id = request.GET.get('id')
    try:
        equipe = Equipe.objects.get(id=id)
        equipe.delete()
        messages.success(request, "Équipe supprimée avec succès.")
    except Equipe.DoesNotExist:
        raise Http404("Équipe non trouvée.")
    return redirect('dashboard')


@login_required
def checkedNameEquipeExist(request):
    if request.method == "POST":
        name = request.POST.get('param')
        if Equipe.objects.filter(name=name).exists():
            return JsonResponse({"exists": True})
        else:
            return JsonResponse({"exists": False})
        
@login_required
def checkedPromotionEquipeExist(request):
    if request.method == "POST":
        promotion = request.POST.get('param')
        if Equipe.objects.filter(promotion=promotion).exists():
            return JsonResponse({"exists": True})
        else:
            return JsonResponse({"exists": False})

@login_required
def generatorQuestionIA(request):
    if request.method == "POST":
        try:
            nombre_qst = int(request.POST.get('nombre-question'))
            prompt = f"""Génères moi {nombre_qst} questions en français dans
                        le domaine d'informatique pour un jeu intitulé the brain games. 
                        Ne rajoute rien d'autre, juste les questions et ne numérote pas
                        et puis fais varier la taille de question,
                        le contenu aussi de la question, que ça soit des questions qui peuvent 
                        poussé la personne a réflechir, donc fais varier.
                    """
            response = ollama.chat(
                model='llama3',
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ]
            )
            
            # Filtrage des questions à partir de la réponse
            raw_content = response['message']['content']
            lines = raw_content.split('\n')
            questions = [line.strip() for line in lines if line.strip().endswith('?')]
            
            for question in questions[:nombre_qst]:  # Limiter au nombre de questions souhaité
                if question.strip():
                    Questions.objects.create(question=question.strip())
            
            messages.success(request, f"{nombre_qst} questions ont été générées avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération des questions: {str(e)}")
    
    return redirect('dashboard')

@login_required
def deleteAllQuestion(request):
    try:
        questions = Questions.objects.all()
        questions.delete()
        messages.success(request, "Toutes les questions ont été supprimées avec succès.")
    except Questions.DoesNotExist:
        raise Http404("Questions non trouvées.")
    return redirect('dashboard')

@login_required
def deleteQuestion(request):
    if request.method == "POST":
        try:
            id = request.POST.get('id_question')
            question = Questions.objects.get(id=id)
            question.delete()
            questions = list(Questions.objects.values())  # Convertir en liste de dictionnaires
            return JsonResponse({"success": True, "message": "Question supprimée avec succès.", "questions": questions})
        except Questions.DoesNotExist:
            return JsonResponse({"success": False, "message": "Question non trouvée.", "questions": []})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Une erreur est survenue: {str(e)}", "questions": []})
    return JsonResponse({"success": False, "message": "Requête invalide.", "questions": []})


@login_required
def questionnaire(request):
    if request.method == "POST":
        questions = Questions.objects.all()
        context = {'questions': questions}
        return render(request, "liste-question.html", context)

@login_required
def addQuestion(request):
    if request.method == "POST":
        question = request.POST.get('question').lower()
        questions = Questions(question=question)
        questions.save()
        messages.success(request, "Question ajoutée avec succès.")
        return redirect('dashboard')
    
@login_required
def addQuestionCSV(request):
    if request.method == "POST":
        try:
            fichiercsv = request.FILES['fichiercsv']
            decoded_file = fichiercsv.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            if 'question' not in reader.fieldnames:
                messages.error(request, "Le fichier CSV doit contenir une colonne 'question'.")
                return redirect('dashboard')

            for row in reader:
                question_text = row.get('question')
                if question_text:
                    Questions.objects.create(question=question_text.strip())
            
            messages.success(request, "Questions ajoutées avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout des questions: {str(e)}")
            
@login_required
def configurations(request):
    if request.method == "POST":
        try:
            nombre_qst = int(request.POST.get('nombre_qst'))
            duree = request.POST.get('duree')
            difficulte = request.POST.get('difficulte')
            total_questions = Questions.objects.count()
            total_equipes = Equipe.objects.count()

            # Vérifier si le nombre de questions par équipe est possible avec le nombre total de questions
            if total_questions < total_equipes * nombre_qst:
                return JsonResponse({"success": False, "message": "Le nombre total de questions est insuffisant pour que chaque équipe reçoive le nombre de questions spécifié."})

            # Vérifier si une configuration existe déjà et mettre à jour ou créer une nouvelle configuration
            config, created = Configurations.objects.update_or_create(
                defaults={'nombre_question': nombre_qst, 'duree': duree, 'difficulte': difficulte},
                id=1  # Assurez-vous d'avoir un seul enregistrement de configuration
            )

            if config:
                return JsonResponse({"success": True, "message": "Configurations enregistrées."})
            else:
                return JsonResponse({"success": False, "message": "Une erreur est survenue."})
            
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Une erreur est survenue: {str(e)}"})
        
def send_email(request, email, token):
    server = "smtp.gmail.com"
    port = 465
    username = "garrykabeya000@gmail.com"
    password = "eyeywinhivluuzty"

    # Obtenez le domaine actuel et construisez l'URL complète avec le token
    domain = get_current_site(request).domain
    url = reverse('equipe.training')
    full_url = f"http://{domain}{url}?token={token}"

    # Rendre le template avec les variables nécessaires
    html_content = render_to_string('email.html', {'lien': full_url})

    message = EmailMessage()
    message['To'] = email
    message['From'] = username
    message['Subject'] = 'Entraînement de l\'équipe'
    message.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP_SSL(server, port) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
            print('Message envoyé')
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        
def training(request):
    token = request.GET.get('token')
    try:
        equipe = Equipe.objects.get(token=token)
        
        if Trainings.objects.filter(created_at=date.today(), equipe_id=equipe.id).exists():
            return render(request, 'resultat_training.html')
            
    except Equipe.DoesNotExist:
        messages.error(request, "Équipe non trouvée.")
        return render(request, '404.html')
    
    # Récupérer les questions dont le statut est 0 et les limiter à 10
    questions = Questions.objects.filter(status=0)[:10]
    print("Question: ",questions)
    if not questions:
        messages.error(request, "Aucune question trouvée.")
        return render(request, '404.html')

    # Récupérer les IDs des questions pour mise à jour
    # question_ids = questions.values_list('id', flat=True)
    
    # Mettre à jour le statut de ces questions à 1
    # Questions.objects.filter(id__in=question_ids).update(status=1)
    
    context = {
        'equipe': equipe,
        'questions': questions,
        'current_page': 'training'
    }
    
    return render(request, "entrainement.html", context)

def submitTraining(request):
    equipe_id = request.POST.get('equipe_id')
    question_ids = request.POST.getlist('questions')
    
    try:
        equipe = Equipe.objects.get(id=equipe_id)
        
        if Trainings.objects.filter(created_at=date.today(), equipe_id=equipe.id).exists():
            return render(request, 'resultat_training.html')
        
        # Questions.objects.filter(id__in=question_ids).update(status=1)
        
    except Equipe.DoesNotExist:
        messages.error(request, "Équipe non trouvée.")
        return render(request, '404.html')

    last_score = 0
    training = Trainings.objects.filter(equipe_id=equipe_id).order_by('-created_at').first()
    
    if training:
        last_score = training.score

    questions_reponses = []
    for question_id in question_ids:
        question = Questions.objects.get(id=question_id)
        question.status = 1
        question.save()
        answer = request.POST.get(f'answer_{question_id}')
        if answer:
            questions_reponses.append({
                'question': question.question,
                'answer': answer
            })
    
    # Convertir les questions et réponses en un format que l'API peut comprendre
    formatted_questions = "\n".join(
        [f"Question: {item['question']}\nRéponse: {item['answer']}" for item in questions_reponses]
    )
    
    # Appeler l'API Ollama
    scores = evaluate_answer_with_ollama(formatted_questions)
    new_score = int(scores) + last_score

    new_training = Trainings(score=scores, equipe_id=equipe_id, created_at=date.today())
    new_training.save()

    messages.success(request, "Vos réponses ont été soumises avec succès.")
    return render(request, 'resultat_training.html', 
                {
                    'total_score': scores,
                    'new_score': new_score,
                }
            )

def evaluate_answer_with_ollama(questions):
    # prompt = f"""
    # Évaluez les réponses suivantes sur une échelle de 0 à 1000 points, où 1000 points représentent une réponse parfaite.
    
    # Voici les questions et leurs réponses :
    # {questions}
    
    
    # Notez la réponse en fonction de sa précision, de sa pertinence et de sa complétude.
    # """
    prompt = f"""
    Évaluez les réponses suivantes sur une échelle de 0 à 1000 points, où 1000 points représentent une réponse parfaite.
    
    Voici les questions et leurs réponses :
    {questions}
    
    retourne moi juste le score total (chiffre) et rien d'autre.
    """
    
    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': prompt,
            }
        ]
    )
    
    return response['message']['content']
    
