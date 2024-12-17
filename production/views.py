from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Part, UAV
from accounts.models import TeamMember
from .forms import PartForm, UAVForm

@login_required
def home(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    context = {
        'team_member': team_member,
    }
    
    if team_member.team.name == 'assembly':
        context['uavs'] = UAV.objects.all()
        context['available_parts'] = {
            'wings': Part.objects.filter(type='wing', is_used=False),
            'bodies': Part.objects.filter(type='body', is_used=False),
            'tails': Part.objects.filter(type='tail', is_used=False),
            'avionics': Part.objects.filter(type='avionics', is_used=False),
        }
    else:
        context['parts'] = Part.objects.filter(
            type=team_member.team.name,
            produced_by=team_member
        )
    
    return render(request, 'production/home.html', context)

@login_required
def part_list(request):
    team_member = get_object_or_404(TeamMember, user=request.user)
    parts = Part.objects.filter(type=team_member.team.name)
    return render(request, 'production/part_list.html', {'parts': parts})

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
    
    uavs = UAV.objects.all()
    return render(request, 'production/uav_list.html', {'uavs': uavs})
