from django.db import models
from accounts.models import Team, TeamMember

class Part(models.Model):
    PART_TYPES = [
        ('wing', 'Kanat'),
        ('body', 'Gövde'),
        ('tail', 'Kuyruk'),
        ('avionics', 'Aviyonik'),
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
        verbose_name = 'Parça'
        verbose_name_plural = 'Parçalar'

class UAV(models.Model):
    UAV_TYPES = [
        ('tb2', 'TB2'),
        ('tb3', 'TB3'),
        ('akinci', 'AKINCI'),
        ('kizilelma', 'KIZILELMA'),
    ]
    
    type = models.CharField('İHA Tipi', max_length=20, choices=UAV_TYPES)
    serial_number = models.CharField('Seri Numarası', max_length=50, unique=True)
    wing = models.OneToOneField(Part, verbose_name='Kanat', on_delete=models.PROTECT, related_name='uav_wing')
    body = models.OneToOneField(Part, verbose_name='Gövde', on_delete=models.PROTECT, related_name='uav_body')
    tail = models.OneToOneField(Part, verbose_name='Kuyruk', on_delete=models.PROTECT, related_name='uav_tail')
    avionics = models.OneToOneField(Part, verbose_name='Aviyonik', on_delete=models.PROTECT, related_name='uav_avionics')
    assembled_by = models.ForeignKey(TeamMember, verbose_name='Montajı Yapan', on_delete=models.SET_NULL, null=True)
    assembly_date = models.DateTimeField('Montajlanma Tarihi', auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_type_display()} ({self.serial_number})"
    
    class Meta:
        verbose_name = 'İHA'
        verbose_name_plural = 'İHA\'lar'
    
    def save(self, *args, **kwargs):
        # Validate that all parts belong to the same UAV type
        parts = [self.wing, self.body, self.tail, self.avionics]
        if not all(part.uav_type == self.type for part in parts):
            raise ValueError("Tüm parçalar aynı İHA tipine ait olmalıdır")
        
        # Mark all parts as used
        for part in parts:
            part.is_used = True
            part.save()
        
        super().save(*args, **kwargs)
