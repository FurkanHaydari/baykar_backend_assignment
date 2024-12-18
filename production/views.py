from django.shortcuts import render, redirect, get_object_or_404
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
    # Admin/staff kullanıcıları direkt admin paneline yönlendir
    if request.user.is_staff:
        return redirect(reverse('admin:index'))

    # Normal kullanıcılar için mevcut işlemler
    team_member = get_object_or_404(TeamMember, user=request.user)
    context = {
        'team_member': team_member,
        'inventory_warnings': check_inventory_status(),
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
def part_list(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    return render(request, 'production/part_list.html', {'team_member': team_member})

@login_required
def part_create(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.produced_by = team_member
            part.type = team_member.team.name
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
        messages.success(request, 'Part recycled successfully.')
        return redirect('part_list')
    
    return render(request, 'production/part_confirm_delete.html', {'part': part})

@login_required
def uav_create(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if team_member.team.name != 'assembly':
        messages.error(request, 'Only assembly team members can create UAVs.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UAVForm(request.POST)
        if form.is_valid():
            uav = form.save(commit=False)
            uav.assembled_by = team_member
            uav.save()
            messages.success(request, 'UAV assembled successfully.')
            return redirect('home')
    else:
        form = UAVForm()
    
    return render(request, 'production/uav_form.html', {'form': form})

@login_required
def uav_list(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    
    if team_member.team.name != 'assembly':
        messages.error(request, 'Only assembly team members can view UAVs.')
        return redirect('home')
    
    return render(request, 'production/uav_list.html')
