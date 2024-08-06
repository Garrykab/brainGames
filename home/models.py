from django.db import models

class Equipe(models.Model):
    name = models.CharField(max_length=50)
    promotion = models.CharField(max_length=50)
    point = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # score = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, null=True, blank=True)  # Champ nullable
    token = models.CharField(max_length=255)
    # training = models.IntegerField(default=0)
    # debut_training = models.DateTimeField(null=True, blank=True)
    # training_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Questions(models.Model):
    question = models.CharField(max_length=255)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.question

class Configurations(models.Model):
    nombre_question = models.IntegerField(default=0)
    duree = models.IntegerField(default=0)
    difficulte = models.CharField(max_length=50, default='facile')
    # categorie = models.CharField(max_length=100, default='Général')
    # mode_jeu = models.CharField(max_length=50, default='chronométré')
    # langue = models.CharField(max_length=50, default='français')
    # score_maximum = models.IntegerField(default=100)
    # penalites = models.IntegerField(default=0)
    # nombre_joueurs = models.IntegerField(default=1)
    
    def __str__(self):
        return f"Configurations: {self.nombre_question} questions, {self.duree} secondes"

class Trainings(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)