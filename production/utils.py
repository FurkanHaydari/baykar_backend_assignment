from .models import Part

def check_inventory_status():
    """
    Envanter durumunu kontrol eder ve eksik parçaları raporlar.
    """
    UAV_TYPES = ['tb2', 'tb3', 'akinci', 'kizilelma']
    PART_TYPES = ['wing', 'body', 'tail', 'avionics']
    
    inventory_warnings = []
    
    for uav_type in UAV_TYPES:
        for part_type in PART_TYPES:
            available_parts = Part.objects.filter(
                type=part_type,
                uav_type=uav_type,
                is_used=False
            ).count()
            
            if available_parts == 0:
                warning = f"{uav_type.upper()} için {part_type} parçası eksik!"
                inventory_warnings.append(warning)
    
    return inventory_warnings
