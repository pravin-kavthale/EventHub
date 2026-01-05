from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm,CustomPasswordChangeForm
from django.views.generic import CreateView,UpdateView,DetailView,ListView,DeleteView,View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Notification,Profile,Batch,UserBatch,UserConnection
from django.urls import reverse_lazy
from Event.models import Event,Like,Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse


from django.http import JsonResponse
from django.db import transaction

User = get_user_model() 

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:  
        form = UserRegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def password_change(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated! 🎉")
            return redirect("profile")
        else:
            print(form.errors)  # <-- Add this line
            target_user = request.user
            u_form = UserUpdateForm(instance=target_user)
            p_form = ProfileUpdateForm(instance=target_user.profile)

            context = {
                'target_user': target_user,
                'u_form': u_form,
                'p_form': p_form,
                'password_form': form,
                'is_current_user': True,
                'followers_count': UserConnection.objects.filter(following=target_user).count(),
                'following_count': UserConnection.objects.filter(follower=target_user).count(),
                'is_following': False,
                'events_count': Event.objects.filter(organizer=target_user).count(),
            }
            return render(request, 'profile.html', context)

    return redirect("profile")

@login_required
def profile(request, username=None):
    if username:
        target_user = get_object_or_404(User, username=username)
        is_current_user = (target_user == request.user)
    else:
        target_user = request.user
        is_current_user = True

    # Followers / following counts, etc.
    followers_count = UserConnection.objects.filter(following=target_user).count()
    following_count = UserConnection.objects.filter(follower=target_user).count()
    is_following = UserConnection.objects.filter(follower=request.user, following=target_user).exists()
    events_count = Event.objects.filter(organizer=target_user).count()

    # User & profile update forms
    u_form = None
    p_form = None
    if is_current_user:
        if request.method == 'POST' and 'update_profile' in request.POST:
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('profile')
        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

    # Password change form (for display only)
    password_form = CustomPasswordChangeForm(user=request.user) if is_current_user else None

    context = {
        'target_user': target_user,
        'u_form': u_form,
        'p_form': p_form,
        'password_form': password_form,
        'is_current_user': is_current_user,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'events_count': events_count,
    }

    return render(request, 'profile.html', context)

class ListNotification(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'user/List_notification.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        qs = Notification.objects.filter(receiver=self.request.user,is_read=False).order_by('-timestamp')
        qs.update(is_read=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        navbar_notifications = Notification.objects.filter(receiver=self.request.user).order_by('-timestamp')[:5]
        navbar_unread_count = navbar_notifications.filter(is_read=False).count()

        context['notifications'] = self.get_queryset()  
        context['navbar_notifications'] = navbar_notifications 
        context['navbar_unread_count'] = navbar_unread_count  
        return context

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({"success": True})

class CreateBatch(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model=Batch
    fields=['name','description','required_events','image']
    template_name='user/batch_form.html'
    success_url=reverse_lazy('list_batch')
    
    def test_func(self):
        return self.request.user.is_superuser

class UpdateBatch(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Batch
    fields=['name','description','required_events','image']
    template_name='user/batch_form.html'
    success_url=reverse_lazy('list_batch')

    def test_func(self):
        return self.request.user.is_superuser

class ListBatch(LoginRequiredMixin,ListView):
    model=Batch
    template_name='user/batch_list.html'
    context_object_name='batches'
    paginate_by=10

    def get_queryset(self):
        return Batch.objects.all().order_by('required_events')

class DetailBatch(LoginRequiredMixin,DetailView):
    model=Batch
    template_name='user/batch_detail.html'
    context_object_name='batch'

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        batch=self.get_object()
        count=Event.objects.filter(participants=self.request.user).count()

        if batch.required_events <= count:
            context['show_description'] = True
        else:
            context['show_description'] = False
            messages.info(
                self.request,
                f"You need {batch.required_events} events to earn this batch "
                f"(Currently: {count})."
            )

        return context
        
class DeleteBatch(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Batch
    template_name='user/batch_confirm_delete.html'
    success_url=reverse_lazy('list_batch')

    def test_func(self):
        return self.request.user.is_superuser

class ListUserBatch(LoginRequiredMixin, ListView):
    model = UserBatch
    template_name = 'user/userbatch_list.html'
    context_object_name = 'user_batches'
    paginate_by = 3

    def get_queryset(self):
        return UserBatch.objects.filter(user=self.request.user).order_by('-earned_at')

class CreateUserConnection(LoginRequiredMixin,View):
    
    def post(self,request,*args,**kwargs):
        following=get_object_or_404(User,id=self.kwargs.get('user_id'))
        connection = UserConnection.objects.filter(
            follower=request.user,
            following=following
        )
        if connection.exists():
            connection.delete()
        else:
            UserConnection.objects.create(following=following,follower=request.user)
            Notification.objects.create(
                sender=request.user,
                receiver=following,
                message=f'{request.user} has followed you ',
                action_url=reverse('user_profile', kwargs={'username': request.user.username}),
                type='Follow'
            )
        return redirect('user_profile', username=following.username)

class ListFollowers(LoginRequiredMixin,ListView):
    model=UserConnection
    template_name='user/followers.html'
    context_object_name= 'connections'
    
    def get_queryset(self):
        target_user_id=self.kwargs.get('user_id')
        target_user=get_object_or_404(User,id=target_user_id)
        return UserConnection.objects.filter(following=target_user).select_related('follower')
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['users'] = [conn.follower for conn in context['connections']]
        return context

class ListFollowing(LoginRequiredMixin,ListView):
    model = UserConnection
    template_name = 'user/following.html' 
    context_object_name = 'connections'

    def get_queryset(self):
        target_user_id = self.kwargs.get('user_id')
        target_user = get_object_or_404(User, id=target_user_id)
        return UserConnection.objects.filter(follower=target_user).select_related('following')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = [conn.following for conn in context['connections']]
        return context


class ProfilePrivacy(LoginRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, user=request.user)

        profile.is_private = not profile.is_private
        profile.save()

        return JsonResponse({
            "success": True,
            "is_private": profile.is_private
        })

