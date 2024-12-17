from django.db import models
from accounts.models import Team, TeamMember

class Part(models.Model):
    PART_TYPES = [
        ('wing', 'Wing'),
        ('body', 'Body'),
        ('tail', 'Tail'),
        ('avionics', 'Avionics'),
    ]
    
    UAV_TYPES = [
        ('tb2', 'TB2'),
        ('tb3', 'TB3'),
        ('akinci', 'AKINCI'),
        ('kizilelma', 'KIZILELMA'),
    ]
    
    type = models.CharField(max_length=20, choices=PART_TYPES)
    uav_type = models.CharField(max_length=20, choices=UAV_TYPES)
    serial_number = models.CharField(max_length=50, unique=True)
    produced_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True)
    production_date = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_uav_type_display()} - {self.get_type_display()} ({self.serial_number})"
    
    class Meta:
        unique_together = ('type', 'serial_number')

class UAV(models.Model):
    UAV_TYPES = [
        ('tb2', 'TB2'),
        ('tb3', 'TB3'),
        ('akinci', 'AKINCI'),
        ('kizilelma', 'KIZILELMA'),
    ]
    
    type = models.CharField(max_length=20, choices=UAV_TYPES)
    serial_number = models.CharField(max_length=50, unique=True)
    wing = models.OneToOneField(Part, on_delete=models.PROTECT, related_name='uav_wing')
    body = models.OneToOneField(Part, on_delete=models.PROTECT, related_name='uav_body')
    tail = models.OneToOneField(Part, on_delete=models.PROTECT, related_name='uav_tail')
    avionics = models.OneToOneField(Part, on_delete=models.PROTECT, related_name='uav_avionics')
    assembled_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True)
    assembly_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_type_display()} ({self.serial_number})"
    
    def save(self, *args, **kwargs):
        # Validate that all parts belong to the same UAV type
        parts = [self.wing, self.body, self.tail, self.avionics]
        if not all(part.uav_type == self.type for part in parts):
            raise ValueError("All parts must belong to the same UAV type")
        
        # Mark all parts as used
        for part in parts:
            part.is_used = True
            part.save()
        
        super().save(*args, **kwargs)
