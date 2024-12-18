from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

def login_view(request):
    # Eğer kullanıcı zaten giriş yapmışsa
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect(reverse('admin:index'))
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Admin kullanıcısı ise admin paneline yönlendir
            if user.is_staff:
                return redirect(reverse('admin:index'))
            return redirect('home')
        else:
            messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
    
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    was_staff = request.user.is_staff
    logout(request)
    messages.success(request, 'Başarıyla çıkış yapıldı.')
    # Admin kullanıcısı ise admin login sayfasına yönlendir
    if was_staff:
        return redirect(reverse('admin:login'))
    return redirect('login')
