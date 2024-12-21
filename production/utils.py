from .models import Part

def check_inventory_status(current_team=None):
    """
    Envanter durumunu kontrol eder ve eksik parçaları raporlar.
    Her ekibin üretim durumunu diğer ekiplerle karşılaştırır.
    
    Args:
        current_team: Mevcut ekip (wing, body, tail, avionics, assembly)
        
    Returns:
        dict: Her İHA tipi için parça durumu ve uyarılar
    """
    UAV_TYPES = ['tb2', 'tb3', 'akinci', 'kizilelma']
    PART_TYPES = ['wing', 'body', 'tail', 'avionics']
    PART_NAMES = {
        'wing': 'Kanat',
        'body': 'Gövde',
        'tail': 'Kuyruk',
        'avionics': 'Aviyonik'
    }
    
    inventory_status = {}
    
    # Montaj ekibi tüm eksik parçaları görmeli
    is_assembly = current_team == 'assembly'
    
    for uav_type in UAV_TYPES:
        part_counts = {}
        warnings = []
        
        # Her parça tipinin sayısını hesapla
        for part_type in PART_TYPES:
            count = Part.objects.filter(
                type=part_type,
                uav_type=uav_type,
                **{f"uav_{part_type}__isnull": True}  # Kullanılmamış parçalar
            ).count()
            part_counts[part_type] = count
        
        # Parça dengesizliği kontrolü
        max_count = max(part_counts.values())
        
        # Her parça tipi için kontroller
        for part_type in PART_TYPES:
            count = part_counts[part_type]
            
            # Bu parça tipi mevcut ekibe aitse veya montaj ekibiyse
            if current_team == part_type or is_assembly:
                # Eksik parça uyarısı
                if count == 0:
                    warnings.append({
                        'type': 'danger',
                        'message': f"{uav_type.upper()} için {PART_NAMES[part_type]} parçası eksik!"
                    })
                # Düşük stok uyarısı
                elif count <= 5:
                    warnings.append({
                        'type': 'warning',
                        'message': f"{uav_type.upper()} için {PART_NAMES[part_type]} stoku düşük! (Kalan: {count})"
                    })
                
                # Parça dengesizliği uyarısı
                if count < max_count:
                    other_parts = []
                    for other_type, other_count in part_counts.items():
                        if other_count > count:
                            other_parts.append(f"{PART_NAMES[other_type]} ({other_count})")
                    
                    if other_parts:
                        warnings.append({
                            'type': 'warning',
                            'message': f"{uav_type.upper()} için {PART_NAMES[part_type]} parçanız ({count}) yetersiz. " +
                                     f"Diğer parçalar: {', '.join(other_parts)}"
                        })
        
        # Montaj ekibi için İHA üretim durumu
        if is_assembly and min(part_counts.values()) > 0:
            min_count = min(part_counts.values())
            needed_parts = []
            for part_type, count in part_counts.items():
                if count == min_count:
                    needed_parts.append(PART_NAMES[part_type])
            
            if needed_parts:
                warnings.append({
                    'type': 'info',
                    'message': f"{min_count} adet İHA üretmek için {', '.join(needed_parts)} parçaları hazır."
                })
        
        if warnings:  # Sadece uyarı varsa status'e ekle
            inventory_status[uav_type] = {
                'part_counts': part_counts,
                'warnings': warnings
            }
    
    return inventory_status
