from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Team, TeamMember
from production.models import Part, UAV
import random
import string
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = "Veritabanını ilk veriler ile oluşturur"

    def generate_serial_number(self):
        """Rastgele seri numarası oluşturur"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def handle(self, *args, **kwargs):
        # Takımları oluştur
        teams_data = [
            ('wing', 'Kanat Takımı'),
            ('body', 'Gövde Takımı'),
            ('tail', 'Kuyruk Takımı'),
            ('avionics', 'Aviyonik Takımı'),
            ('assembly', 'Montaj Takımı'),
        ]

        self.stdout.write('Takımlar oluşturuluyor...')
        teams = {}
        for team_code, team_name in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_code,
                defaults={'description': f'This is the {team_name}'}
            )
            teams[team_code] = team
            if created:
                self.stdout.write(f'Takım oluşturuldu: {team_name}')

        # Admin kullanıcısı oluştur
        self.stdout.write('Admin kullanıcısı oluşturuluyor...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Admin kullanıcısı şu parola ile oluşturuldu: admin123')

        # Her takım için bir kullanıcı ve takım üyesi oluştur
        for team_code, team in teams.items():
            username = f'{team_code}_user'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'}
            )
            if created:
                user.set_password('user123')
                user.save()
                self.stdout.write(f'Kullanıcı oluşturuldu: {username}')

            team_member, created = TeamMember.objects.get_or_create(
                user=user,
                team=team
            )
            if created:
                self.stdout.write(f'Takım üyesi oluşturuldu: {username}, şifre: user123')

        # Her UAV tipi için parçalar oluştur
        uav_types = ['tb2', 'tb3', 'akinci', 'kizilelma']
        part_types = ['wing', 'body', 'tail', 'avionics']

        self.stdout.write('Parçalar oluşturuluyor...')
        for uav_type in uav_types:
            for part_type in part_types:
                team = teams[part_type]
                team_member = TeamMember.objects.get(team=team)
                
                # Her tip için 25'ten büyük rastgele sayıda parça oluştur
                part_count= 25 + random.randint(0, 100)
                existing_parts = Part.objects.filter(
                    type=part_type,
                    uav_type=uav_type
                ).count()
                
                parts_to_create = part_count - existing_parts
                
                if parts_to_create > 0:
                    parts = [
                        Part(
                            type=part_type,
                            uav_type=uav_type,
                            serial_number=f'{uav_type.upper()}_{part_type.upper()}_{self.generate_serial_number()}',
                            produced_by=team_member
                        )
                        for _ in range(parts_to_create)
                    ]
                    Part.objects.bulk_create(parts)
                    self.stdout.write(f'{uav_type} için {parts_to_create} {part_type} parçası oluşturuldu')

        # UAV'ları oluştur
        self.stdout.write("İHA'lar oluşturuluyor...")
        assembly_team = teams['assembly']
        assembly_member = TeamMember.objects.get(team=assembly_team)

        # Her UAV tipi için 25'er adet UAV oluştur (toplam 100 UAV)
        for uav_type in uav_types:
            existing_uavs = UAV.objects.filter(type=uav_type).count()
            uavs_to_create = 20 - existing_uavs

            if uavs_to_create > 0:
                for _ in range(uavs_to_create):
                    # Her parça tipinden kullanılmamış bir parça seç
                    parts = {}
                    for part_type in part_types:
                        # Her parça tipi için doğru related name'i kullan
                        related_names = {
                            'wing': 'uav_wing',
                            'body': 'uav_body',
                            'tail': 'uav_tail',
                            'avionics': 'uav_avionics'
                        }
                        
                        part = Part.objects.filter(
                            type=part_type,
                            uav_type=uav_type,
                            **{f"{related_names[part_type]}__isnull": True}
                        ).first()
                        
                        if part:
                            # İHA modelindeki field isimlerini kullan
                            parts[part_type] = part

                    # Eğer tüm parça tipleri mevcutsa İHA oluştur
                    if len(parts) == len(part_types):
                        # Rastgele bir tarih oluştur (son 30 gün içinde)
                        random_days = random.randint(0, 30)
                        assembly_date = timezone.now() - timedelta(days=random_days)
                        
                        uav = UAV.objects.create(
                            type=uav_type,
                            serial_number=f'{uav_type.upper()}_UAV_{self.generate_serial_number()}',
                            assembled_by=assembly_member,
                            assembly_date=assembly_date,
                            **parts
                        )
                        self.stdout.write(f'İHA oluşturuldu: {uav.serial_number}')

        self.stdout.write(self.style.SUCCESS('Veritabanı başlangıç verileri oluşturuldu'))
