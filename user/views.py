from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm

from django.views.generic import CreateView,UpdateView,DetailView,ListView,DeleteView,View

from django.contrib.auth.decorators import login_required
from django.authn.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Notification

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:  # <-- this belongs outside POST check
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    u_form=UserUpdateForm()
    p_form=ProfileUpdateForm()
    
    if request.method=='POST':
        u_form=UserUpdateForm(request.POST,instance=request.user)
        p_form=ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form=UserUpdateForm(instance=request.user)
        p_form=ProfileUpdateForm(instance=request.user.profile)
            
    context={
        'u_form':u_form,
        'p_form':p_form
    }
    return render(request,'profile.html',context)

class CreateNotification(LoginRequiredMixin,UserPassestestMixin,CreateView):
    def post(self,request,*args,**kwargs):
        event=Event.object.get_object_or_404(id=self.kwargs.get('event_id'))
        Like,creates=Like.object.get_object_or_404(user=request.user,event=event)
        if creates:
            Notification.objects.create(
                sender=request.user,
                receiver=Like.event.organizer,
                evet=Like.event,
                message=f"{request.user.username} Liked your event {Like.event.title}",
            )
        comment,creates=Comment.object.get_object_or_404(user=request.user,event=event)
        if creates:
            Notification.objects.create(
                sender=request.user,
                receiver=Comment.event.organizer,
                evet=Comment.event,
                message=f"{request.user.username} Commented on your event {Comment.event.title}: {comment.content}  ",
            )
        follow,creates=UserConnection.object.get_object_or_404(follower=request.user,following=event.organizer)
        if creates:
            Notification.objects.create(
                sender=request.user,
                receiver=event.organizer,
                message=f"{request.user.username} started following you.",
            )
    def test_func(self):
        event = get_object_or_404(Event, id=self.kwargs.get('event_id'))
        return request.user is not event.organizer

class ListNotification(LoginRequiredMixin,ListView):
    model=Notification
    template_name='user/List_notification.html'
    context_object_name='notifications'
    
    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-timestamp')

class DetailNotification(LoginRequiredMixin,DetailView):
    model=Notification
    template_name='user/Detail_notification.html'
    context_object_name='notification'
    
    def get_object(self,queryset=None):
        notification=super().get_object(queryset)
        if not notification.is_read:   # 👈 optional but avoids extra DB writes
            notification.is_read = True
            notification.save()
        return notification