from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    TEAM_CHOICES = [
        ('wing', 'Wing Team'),
        ('body', 'Body Team'),
        ('tail', 'Tail Team'),
        ('avionics', 'Avionics Team'),
        ('assembly', 'Assembly Team'),
    ]
    
    name = models.CharField(max_length=50, choices=TEAM_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()

class TeamMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    join_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.team}"
