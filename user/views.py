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

class ListNotification(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'user/List_notification.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        qs = Notification.objects.filter(receiver=self.request.user).order_by('-timestamp')
        qs.update(is_read=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        navbar_notifications = Notification.objects.filter(receiver=self.request.user).order_by('-timestamp')[:5]
        navbar_unread_count = navbar_notifications.filter(is_read=False).count()

        context['notifications'] = self.get_queryset()  # List page notifications
        context['navbar_notifications'] = navbar_notifications  # For navbar dropdown
        context['navbar_unread_count'] = navbar_unread_count  # For bell badge
        return context


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
