from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib import messages
from django.urls import reverse
from .models import Part, UAV
from accounts.models import TeamMember
from .forms import PartForm, UAVForm
from .utils import check_inventory_status

@login_required
def home(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    team = team_member.team.name if team_member else None
    
    # Envanter durumunu kontrol et
    inventory_status = check_inventory_status(current_team=team)
    
    context = {
        'team_member': team_member,
        'inventory_status': inventory_status
    }
    
    if team_member.team.name == 'assembly':
        # Her UAV tipi için parça sayılarını hesapla
        context['part_counts'] = {}
        for uav_type, _ in UAV.UAV_TYPES:
            context['part_counts'][uav_type] = {
                'wing': Part.objects.filter(type='wing', uav_type=uav_type, is_used=False).count(),
                'body': Part.objects.filter(type='body', uav_type=uav_type, is_used=False).count(),
                'tail': Part.objects.filter(type='tail', uav_type=uav_type, is_used=False).count(),
                'avionics': Part.objects.filter(type='avionics', uav_type=uav_type, is_used=False).count(),
            }
    
    return render(request, 'production/home.html', context)

@login_required
def dashboard(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    team = team_member.team.name if team_member else None
    
    # Envanter durumunu kontrol et
    inventory_status = check_inventory_status(current_team=team)
    
    context = {
        'team_member': team_member,
        'inventory_status': inventory_status
    }
    return render(request, 'production/dashboard.html', context)

@login_required
def part_list(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    return render(request, 'production/part_list.html', {'team_member': team_member})

@login_required
def part_create(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            # Kullanıcının kendi takımının parçası dışında parça oluşturmasını engelle
            if form.cleaned_data['type'] != team_member.team.name:
                return HttpResponseForbidden("Bu parçayı oluşturma yetkiniz yok.")
            
            part = form.save(commit=False)
            part.produced_by = team_member
            part.save()
            messages.success(request, 'Part created successfully.')
            return redirect('part_list')
    else:
        form = PartForm()
    
    return render(request, 'production/part_form.html', {'form': form})

@login_required
def part_delete(request, pk):
    team_member = get_object_or_404(TeamMember, user=request.user)
    part = get_object_or_404(Part, pk=pk, type=team_member.team.name)
    
    if request.method == 'POST':
        part.delete()
        messages.success(request, 'Parça başarıyla geri dönüşüme gonderildi.')
        return redirect('part_list')
    
    return render(request, 'production/part_confirm_delete.html', {'part': part})

@login_required
def uav_create(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if team_member.team.name != 'assembly':
        messages.error(request, 'Sadece montaj ekip üyeleri İHA oluşturabilir.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UAVForm(request.POST)
        if form.is_valid():
            uav = form.save(commit=False)
            uav.assembled_by = team_member
            
            # Parçaları kullanılmış olarak işaretle
            form.cleaned_data['wing'].is_used = True
            form.cleaned_data['wing'].save()
            form.cleaned_data['body'].is_used = True
            form.cleaned_data['body'].save()
            if 'tail' in form.cleaned_data:
                form.cleaned_data['tail'].is_used = True
                form.cleaned_data['tail'].save()
            if 'avionics' in form.cleaned_data:
                form.cleaned_data['avionics'].is_used = True
                form.cleaned_data['avionics'].save()
            
            uav.save()
            messages.success(request, 'İHA basarıyla montajlandı.')
            return redirect('home')
    else:
        form = UAVForm()
    
    return render(request, 'production/uav_form.html', {'form': form})

@login_required
def uav_list(request):
    # Kullanıcının ekibini al
    team = request.user.teammember.team.name if hasattr(request.user, 'teammember') else None
    
    # Envanter durumunu kontrol et
    inventory_status = check_inventory_status(current_team=team)
    
    context = {
        'inventory_status': inventory_status
    }
    return render(request, 'production/uav_list.html', context)
