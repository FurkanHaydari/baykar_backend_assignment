from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from production.models import Part, UAV
from .serializers import PartSerializer, UAVSerializer
from accounts.models import TeamMember
from django.db.models import Q

class PartViewSet(viewsets.ModelViewSet):
    serializer_class = PartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        team_member = TeamMember.objects.get(user=self.request.user)
        queryset = Part.objects.all()

        # Montaj ekibi tüm parçaları görebilir
        if team_member.team.name != 'assembly':
            # Diğer ekipler sadece kendi parçalarını görebilir
            queryset = queryset.filter(type=team_member.team.name)
        
        # Filter by part type if specified
        part_type = self.request.query_params.get('type', None)
        if part_type:
            queryset = queryset.filter(type=part_type)
        
        # Filter by UAV type if specified
        uav_type = self.request.query_params.get('uav_type', None)
        if uav_type:
            queryset = queryset.filter(uav_type=uav_type)
        
        # Filter by usage status if specified
        is_used = self.request.query_params.get('is_used', None)
        if is_used is not None:
            queryset = queryset.filter(is_used=is_used.lower() == 'true')
        
        return queryset

    def perform_create(self, serializer):
        team_member = TeamMember.objects.get(user=self.request.user)
        serializer.save(produced_by=team_member, type=team_member.team.name)

    @action(detail=False, methods=['get'])
    def datatable_data(self, request):
        # Datatable parametreleri
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Başlangıç queryset
        queryset = self.get_queryset()
        total_records = queryset.count()
        
        # Arama filtresi
        if search_value:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_value) |
                Q(uav_type__icontains=search_value) |
                Q(type__icontains=search_value) |
                Q(produced_by__user__username__icontains=search_value)
            )
        
        filtered_records = queryset.count()
        
        # Sıralama ve sayfalama
        queryset = queryset[start:start + length]
        
        # Veriyi hazırla
        data = []
        for part in queryset:
            data.append({
                'serial_number': part.serial_number,
                'uav_type': part.get_uav_type_display(),
                'type': part.get_type_display(),
                'production_date': part.production_date.strftime('%Y-%m-%d %H:%M'),
                'is_used': part.is_used,
                'id': part.id,
                'produced_by': part.produced_by.user.username
            })
        
        return Response({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })

class UAVViewSet(viewsets.ModelViewSet):
    queryset = UAV.objects.all()
    serializer_class = UAVSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        team_member = TeamMember.objects.get(user=self.request.user)
        if team_member.team.name != 'assembly':
            raise permissions.PermissionDenied("Only assembly team members can create UAVs")
        serializer.save(assembled_by=team_member)

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        uav_types = dict(UAV.UAV_TYPES)
        status = {}
        
        for uav_code, uav_name in uav_types.items():
            status[uav_code] = {
                'name': uav_name,
                'parts': {
                    'wing': Part.objects.filter(type='wing', uav_type=uav_code, is_used=False).count(),
                    'body': Part.objects.filter(type='body', uav_type=uav_code, is_used=False).count(),
                    'tail': Part.objects.filter(type='tail', uav_type=uav_code, is_used=False).count(),
                    'avionics': Part.objects.filter(type='avionics', uav_type=uav_code, is_used=False).count(),
                }
            }
        
        return Response(status)

    @action(detail=False, methods=['get'])
    def datatable_data(self, request):
        # Datatable parametreleri
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Başlangıç queryset
        queryset = UAV.objects.all()
        total_records = queryset.count()
        
        # Arama filtresi
        if search_value:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_value) |
                Q(type__icontains=search_value) |
                Q(assembled_by__user__username__icontains=search_value)
            )
        
        filtered_records = queryset.count()
        
        # Sıralama ve sayfalama
        queryset = queryset[start:start + length]
        
        # Veriyi hazırla
        data = []
        for uav in queryset:
            data.append({
                'serial_number': uav.serial_number,
                'type': uav.get_type_display(),
                'assembly_date': uav.assembly_date.strftime('%Y-%m-%d %H:%M'),
                'assembled_by': uav.assembled_by.user.username,
                'parts': {
                    'wing': uav.wing.serial_number,
                    'body': uav.body.serial_number,
                    'tail': uav.tail.serial_number,
                    'avionics': uav.avionics.serial_number
                },
                'id': uav.id
            })
        
        return Response({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })
