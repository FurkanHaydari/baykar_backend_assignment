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

    def get_queryset(self):
        queryset = UAV.objects.select_related(
            'wing', 'body', 'tail', 'avionics',
            'assembled_by', 'assembled_by__user',
            'wing__produced_by', 'wing__produced_by__user',
            'body__produced_by', 'body__produced_by__user',
            'tail__produced_by', 'tail__produced_by__user',
            'avionics__produced_by', 'avionics__produced_by__user'
        )

        # Arama
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(serial_number__icontains=search) |
                Q(type__icontains=search) |
                Q(assembled_by__user__username__icontains=search)
            )

        # Sıralama
        ordering = self.request.query_params.get('ordering', '-id')
        if ordering:
            ordering_fields = ordering.split(',')
            queryset = queryset.order_by(*ordering_fields)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Sayfalama
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = queryset.count()
        results = list(queryset[start:end].values(
            'id', 'type', 'serial_number', 'assembly_date',
            'assembled_by__user__username'
        ))
        
        # assembled_by formatını düzelt
        for result in results:
            result['assembled_by'] = {
                'user': {
                    'username': result.pop('assembled_by__user__username', None)
                }
            } if result.get('assembled_by__user__username') else None

        return Response({
            'results': results,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })

    def create(self, request, *args, **kwargs):
        try:
            # Parçaları al
            wing = Part.objects.get(id=request.data.get('wing_id'))
            body = Part.objects.get(id=request.data.get('body_id'))
            tail = Part.objects.get(id=request.data.get('tail_id'))
            avionics = Part.objects.get(id=request.data.get('avionics_id'))

            # Parçaların UAV tipi kontrolü
            parts = [wing, body, tail, avionics]
            uav_type = request.data.get('type')
            
            for part in parts:
                if part.uav_type != uav_type:
                    return Response(
                        {'error': f'Seçilen {part.get_type_display()} parçasının UAV tipi uyumsuz'},
                        status=400
                    )
                if part.is_used:
                    return Response(
                        {'error': f'Seçilen {part.get_type_display()} parçası zaten kullanılmış'},
                        status=400
                    )

            # UAV oluştur
            uav = UAV.objects.create(
                type=uav_type,
                serial_number=request.data.get('serial_number'),
                wing=wing,
                body=body,
                tail=tail,
                avionics=avionics,
                assembled_by=TeamMember.objects.get(user=request.user)
            )

            # Parçaları kullanıldı olarak işaretle
            for part in parts:
                part.is_used = True
                part.save()

            return Response(UAVSerializer(uav).data, status=201)

        except Part.DoesNotExist:
            return Response({'error': 'Seçilen parçalardan biri bulunamadı'}, status=400)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    def perform_create(self, serializer):
        team_member = TeamMember.objects.get(user=self.request.user)
        if team_member.team.name != 'assembly':
            raise PermissionError('Sadece montaj ekibi UAV oluşturabilir')
        serializer.save(assembled_by=team_member)

    @action(detail=False, methods=['get'])
    def inventory_status(self, request):
        """Her UAV tipi için stok durumunu döndürür"""
        status = {}
        for uav_type, _ in UAV.UAV_TYPES:
            status[uav_type] = {
                'wing': Part.objects.filter(type='wing', uav_type=uav_type, is_used=False).count(),
                'body': Part.objects.filter(type='body', uav_type=uav_type, is_used=False).count(),
                'tail': Part.objects.filter(type='tail', uav_type=uav_type, is_used=False).count(),
                'avionics': Part.objects.filter(type='avionics', uav_type=uav_type, is_used=False).count(),
            }
        return Response(status)

    @action(detail=False, methods=['get'])
    def datatable_data(self, request):
        # Parametreleri al
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        order_column = request.GET.get('order[0][column]', 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')

        # Sıralama için kolon adını al
        column_index_to_name = {
            '0': 'serial_number',
            '1': 'type',
            '2': 'assembly_date',
            '3': 'assembled_by__user__username',
            '4': 'id'
        }
        order_column_name = column_index_to_name.get(str(order_column), 'id')
        if order_dir == 'desc':
            order_column_name = f'-{order_column_name}'

        # Queryset oluştur
        queryset = self.get_queryset()

        # Arama filtresi
        if search_value:
            queryset = queryset.filter(
                Q(serial_number__icontains=search_value) |
                Q(type__icontains=search_value) |
                Q(assembled_by__user__username__icontains=search_value)
            )

        # Toplam kayıt sayısı
        total_records = queryset.count()
        filtered_records = total_records

        # Sıralama ve sayfalama
        queryset = queryset.order_by(order_column_name)[start:start + length]

        # Sonuçları hazırla
        data = []
        for uav in queryset:
            data.append({
                'id': uav.id,
                'serial_number': uav.serial_number,
                'type': uav.type,
                'assembly_date': uav.assembly_date,
                'assembled_by': uav.assembled_by.user.username if uav.assembled_by else '-'
            })

        return Response({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })

    @action(detail=False, methods=['get'])
    def available_parts(self, request):
        """Belirli bir UAV tipi için kullanılabilir parçaları döndürür"""
        uav_type = request.GET.get('uav_type')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        part_type = request.GET.get('part_type')

        if not uav_type or not part_type:
            return Response({'error': 'UAV tipi ve parça tipi belirtilmedi'}, status=400)

        # Parçaları filtrele
        queryset = Part.objects.filter(
            type=part_type,
            uav_type=uav_type,
            is_used=False
        )
        
        # Arama filtresi
        if search:
            queryset = queryset.filter(
                Q(serial_number__icontains=search) |
                Q(produced_by__user__username__icontains=search)
            )
        
        # Toplam kayıt sayısı
        total = queryset.count()
        
        # Sayfalama
        start = (page - 1) * page_size
        end = start + page_size
        
        # Sonuçları hazırla
        results = []
        for part in queryset[start:end]:
            results.append({
                'id': part.id,
                'text': f"{part.serial_number} ({part.produced_by.user.username})",
            })

        return Response({
            'results': results,
            'pagination': {
                'more': total > (page * page_size)
            }
        })

    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        try:
            uav = self.get_object()
            parts = {
                'wing': PartSerializer(uav.wing).data,
                'body': PartSerializer(uav.body).data,
                'tail': PartSerializer(uav.tail).data,
                'avionics': PartSerializer(uav.avionics).data
            }
            return Response(parts)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
