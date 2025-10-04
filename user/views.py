from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm,UserUpdateForm,ProfileUpdateForm
from django.views.generic import CreateView,UpdateView,DetailView,ListView,DeleteView,View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Notification,Profile,Batch,UserBatch,UserConnection
from django.urls import reverse_lazy
from Event.models import Event,Like,Comment

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
class CreateNotification(LoginRequiredMixin,UserPassesTestMixin,CreateView):
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

class CreateBatch(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    model=Batch
    fields=['name','description','required_events']
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

class ListUserBatch(LoginRequiredMixin,ListView):
    model=UserBatch
    template_name='user/userbatch_list.html'
    context_object_name='user_batches'
    paginate_by=3

    def get_queryset(self):
        return UserBatch.objects.filter(user=self.request.user).order_by('-earned_at')

class CreateUserConnection(LoginRequiredMixin,View):
    success_url=reverse_lazy('profile')
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
        return redirect(self.success_url)

class ListFollowers(LoginRequiredMixin,ListView):
    model=UserConnection
    template_name='user/followers.html'
    context_object_name= 'followers'

    def get_queryset(self):
        return UserConnection.objects.filter(following=self.request.user)
class ListFollowing(LoginRequiredMixin,ListView):
    model=UserConnection
    template_name='user/followers.html'
    context_object_name= 'followings'

    def get_queryset(self):
        return UserConnection.objects.filter(follower=self.request.user)
