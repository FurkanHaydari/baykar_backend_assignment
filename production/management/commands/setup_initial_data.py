from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Team, TeamMember
from production.models import Part
import random
import string

class Command(BaseCommand):
    help = 'Populates the database with initial data'

    def generate_serial_number(self):
        """Rastgele seri numarası oluşturur"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def handle(self, *args, **kwargs):
        # Takımları oluştur
        teams_data = [
            ('wing', 'Wing Team'),
            ('body', 'Body Team'),
            ('tail', 'Tail Team'),
            ('avionics', 'Avionics Team'),
            ('assembly', 'Assembly Team'),
        ]

        self.stdout.write('Creating teams...')
        teams = {}
        for team_code, team_name in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_code,
                defaults={'description': f'This is the {team_name}'}
            )
            teams[team_code] = team
            if created:
                self.stdout.write(f'Created team: {team_name}')

        # Admin kullanıcısı oluştur
        self.stdout.write('Creating admin user...')
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
            self.stdout.write('Created admin user with password: admin123')

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
                self.stdout.write(f'Created user: {username}')

            team_member, created = TeamMember.objects.get_or_create(
                user=user,
                team=team
            )
            if created:
                self.stdout.write(f'Created team member for: {username}')

        # Her UAV tipi için parçalar oluştur
        uav_types = ['tb2', 'tb3', 'akinci', 'kizilelma']
        part_types = ['wing', 'body', 'tail', 'avionics']

        self.stdout.write('Creating parts...')
        for uav_type in uav_types:
            for part_type in part_types:
                # Her tip için 25'er parça oluştur (toplam 400 parça)
                team = teams[part_type]
                team_member = TeamMember.objects.get(team=team)
                
                existing_parts = Part.objects.filter(
                    type=part_type,
                    uav_type=uav_type
                ).count()
                
                parts_to_create = 25 - existing_parts
                
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
                    self.stdout.write(f'Created {parts_to_create} {part_type} parts for {uav_type}')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with initial data'))
