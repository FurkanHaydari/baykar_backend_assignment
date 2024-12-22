from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Part, UAV, TeamMember, Team
from datetime import datetime

class ProductionTests(TestCase):
    def setUp(self):
        # Test kullanıcıları ve takımları oluştur
        self.client = Client()
        
        # Takımları oluştur
        self.wing_team = Team.objects.create(name='wing')
        self.body_team = Team.objects.create(name='body')
        self.assembly_team = Team.objects.create(name='assembly')
        
        # Test kullanıcıları
        self.wing_user = User.objects.create_user(username='wing_user', password='user123')
        self.body_user = User.objects.create_user(username='body_user', password='user123')
        self.assembly_user = User.objects.create_user(username='assembly_user', password='user123')
        
        # Takım üyeleri
        self.wing_member = TeamMember.objects.create(user=self.wing_user, team=self.wing_team)
        self.body_member = TeamMember.objects.create(user=self.body_user, team=self.body_team)
        self.assembly_member = TeamMember.objects.create(user=self.assembly_user, team=self.assembly_team)

    def test_part_creation(self):
        """Parça oluşturma testi"""
        self.client.login(username='wing_user', password='user123')
        
        # Kanat takımı kanat parçası oluşturabilmeli
        response = self.client.post(reverse('part_create'), {
            'type': 'wing',
            'uav_type': 'tb2',
            'serial_number': 'WING001'
        })
        self.assertEqual(response.status_code, 302)  # Başarılı yönlendirme
        self.assertTrue(Part.objects.filter(serial_number='WING001').exists())
        
        # Kanat takımı gövde parçası oluşturamamalı
        response = self.client.post(reverse('part_create'), {
            'type': 'body',
            'uav_type': 'tb2',
            'serial_number': 'BODY001'
        })
        self.assertEqual(response.status_code, 403)  # İzin hatası
        
    def test_uav_assembly(self):
        """İHA montaj testi"""
        # Parçaları oluştur
        wing = Part.objects.create(
            type='wing',
            uav_type='tb2',
            serial_number='WING001',
            produced_by=self.wing_member
        )
        body = Part.objects.create(
            type='body',
            uav_type='tb2',
            serial_number='BODY001',
            produced_by=self.body_member
        )
        tail = Part.objects.create(
            type='tail',
            uav_type='tb2',
            serial_number='TAIL001',
            produced_by=self.body_member
        )
        avionics = Part.objects.create(
            type='avionics',
            uav_type='tb2',
            serial_number='AVIONICS001',
            produced_by=self.body_member
        )
        
        self.client.login(username='assembly_user', password='user123')
        
        # Montaj işlemi
        response = self.client.post(reverse('uav_create'), {
            'type': 'tb2',
            'serial_number': 'TB2001',
            'wing': wing.id,
            'body': body.id,
            'tail': tail.id,
            'avionics': avionics.id,
        })
        
        # Parçaların kullanımda olduğunu kontrol et
        wing.refresh_from_db()
        body.refresh_from_db()
        tail.refresh_from_db()
        avionics.refresh_from_db()
        self.assertTrue(wing.is_used)
        self.assertTrue(body.is_used)
        self.assertTrue(tail.is_used)
        self.assertTrue(avionics.is_used)
        
    def test_inventory_status(self):
        """Envanter durumu testi"""
        # TB2 için parçalar oluştur
        Part.objects.create(
            type='wing',
            uav_type='tb2',
            serial_number='WING001',
            produced_by=self.wing_member
        )
        Part.objects.create(
            type='body',
            uav_type='tb2',
            serial_number='BODY001',
            produced_by=self.body_member
        )
        
        self.client.login(username='assembly_user', password='user123')
        response = self.client.get(reverse('home'))
        
        # Envanter uyarılarını kontrol et
        self.assertIn('inventory_status', response.context)
        status = response.context['inventory_status']
        self.assertIn('tb2', status)
        
    def test_part_recycling(self):
        """Parça geri dönüşüm testi"""
        # Parça oluştur
        part = Part.objects.create(
            type='wing',
            uav_type='tb2',
            serial_number='WING001',
            produced_by=self.wing_member
        )
        
        self.client.login(username='wing_user', password='user123')
        
        # Parçayı geri dönüşüme gönder
        response = self.client.post(reverse('part_delete', args=[part.id]))
        self.assertEqual(response.status_code, 302)
        
        # Parçanın silindiğini kontrol et
        self.assertFalse(Part.objects.filter(id=part.id).exists())
