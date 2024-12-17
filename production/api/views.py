from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from production.models import Part, UAV
from .serializers import PartSerializer, UAVSerializer
from accounts.models import TeamMember

class PartViewSet(viewsets.ModelViewSet):
    serializer_class = PartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Part.objects.all()
        
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
