from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Event,Category,Like,ChatRoom,EventAttendance,Comment,Report
from django.urls import reverse_lazy 
from django.db.models import Count
from django.shortcuts import get_object_or_404,redirect
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from .forms import CategoryForm 

def home(request):
    return render(request,'base/base.html')

# Event Views
class CreateEvent(CreateView):
    model=Event
    fields=['title','description','category','location','date','start_time','end_time','image']
    template_name='Event/event_form.html'
    success_url=reverse_lazy('event_list')

    def form_valid(self,form):
        form.instance.organizer=self.request.user
        return super().form_valid(form)


class JoinEvent(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if request.user in event.participants.all():
            event.participants.remove(request.user)
            messages.success(request, "You have left the event.")
            EventAttendance.objects.filter(user=request.user, event=event).delete()
        else:
            event.participants.add(request.user)
            messages.success(request, "You have joined the event.")
            EventAttendance.objects.get_or_create(user=request.user, event=event, defaults={'status': 'going'})

        return redirect('event_detail', pk=pk)

    def test_func(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return self.request.user != event.organizer


class EventList(ListView):
    model=Event
    template_name='Event/event_list.html'
    context_object_name='events'
    ordering=['-start_time']
    paginate_by=10

    def get_queryset(self):
        return Event.objects.all()
class EventDetails(DetailView):
    model=Event
    template_name='Event/event_detail.html'
    context_object_name='event'

class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    fields = ['title','description','category','date','location','start_time','end_time','image']
    template_name='Event/event_form.html'
    success_url = reverse_lazy('event_list')

    def get_queryset(self):
        # Only allow the organizer to update their own events
        return Event.objects.filter(organizer=self.request.user)

class EventDelete(LoginRequiredMixin,DeleteView):
    model=Event
    template_name='Event/event_delete.html'
    success_url=reverse_lazy('event_list')

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

class CreateCategory(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'Event/category_form.html'
    success_url = reverse_lazy('category_list')  # change to your category list URL

    def form_valid(self, form):
        # If you want to do anything before saving, you can do it here
        return super().form_valid(form)

class CategoryList(ListView):
    model=Category
    template_name='Event/category_list.html'
    context_object_name='categories'
    
    
    def get_queryset(self):
        return Category.objects.annotate(
            event_count=Count('events')  # renamed from popularity
        ).order_by('-event_count')

class CategoryUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=Category
    fields=['name','description','favicon']
    template_name = 'Event/category_form.html'
    success_url=reverse_lazy('category_list')

    def test_func(self):
        return self.request.user.is_superuser

class CategoryDelete(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=Category
    template_name='Event/category_delete.html'
    success_url=reverse_lazy('category_list') 
    def test_func(self):
        return self.request.user.is_superuser

# Like view
class LikeView(LoginRequiredMixin,View):
    def post(self,request,pk):
        event=get_object_or_404(Event,pk=pk)
        like,created=Like.objects.get_or_create(user=request.user,event=event)
        if not created:
            like.delete()
        return redirect('event_detail',pk=pk)

class EventAttendanceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        status = request.POST.get('status', 'going')  # default to 'going'

        attendance, created = EventAttendance.objects.get_or_create(
            user=request.user,
            event=event,
            defaults={'status': status}  # only used if created
        )
        if not created:
            # If already exists, delete it (toggle off)
            attendance.delete()

        return redirect('event_detail', pk=pk)

class getEventAttendance(LoginRequiredMixin,UserPassesTestMixin,ListView):
    model=EventAttendance
    template_name='Event/event_attendance.html'
    context_object_name='attendances'

    def get_queryset(self):
        self.event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return EventAttendance.objects.filter(event=self.event)
    def test_func(self):
        return self.request.user.is_superuser or self.request.user == self.event.organizer


class ChatRoomView(LoginRequiredMixin,View):
    def get(self,request,pk):
        event=get_object_or_404(Event,pk=pk)
        chatroom,create=ChatRoom.objects.get_or_create(event=event)
        messages=chatroom.messages.all()
        return render(request,'Event/chatroom.html',{'chatroom':chatroom,'messages':messages,'event':event})
    def post(self,request,pk):
        event=get_object_or_404(Event,pk=pk)
        chatroom,create=ChatRoom.objects.get_or_create(event=event)
        content=request.POST.get('content')
        if content:
            messages=chatroom.messages.create(user=request.user,content=content)
            return redirect('chatroom',pk=pk)
        messages=chatroom.messages.all()
        return render(request,'Event/chatroom.html',{'chatroom':chatroom,'messages':messages,'event':event})

# Comment Views 
class CommentView(LoginRequiredMixin,View):
    def get(self,request,pk):
        event=get_object_or_404(Event,pk=pk)
        comments=event.comments.all().order_by('-created_at')
        return render(request,'Event/event_comments.html',{'event':event,'comments':comments})
                
    def post(self,request,pk):
        event=get_object_or_404(Event,pk=pk)
        if not event.comments_enabled:
            return HttpResponse("Comments are disabled for this event.",status=403)
        content=request.POST.get('content')
        if content:
            event.comments.objects.create(User=request.user,content=content)
            return redirect('event_detail',pk=pk)
        return render(request,'Event/event_comments.html',{'event':event,'comments':event.comments.all().order_by('-created_at')})

class ReplyCommentView(LoginRequiredMixin,View):
    def get(self,request,pk):
        parent=get_object_or_404(Comment,pk=pk)
        comments_replies=parent.replies.all()
        return render(request,'Event/event_comments.html',{'parent':parent,'replies':comments_replies})

    def post(self,request,pk):
        parent=get_object_or_404(Comment,pk=pk)
        content=request.POST.get('content')
        if content:
            Comment.objects.create(
                user=request.user,
                event=parent.event,
                parent=parent,
                content=content
            )
            return redirect('event_detail',pk=parent.event.pk)
        comments_replies=parent.replies.all()
        return render(request,'Event/event_comments.html',{'parent':parent,'replies':comments_replies})

class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'Event/comment_confirm_delete.html'
    context_object_name = "comment"

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.event.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user or self.request.user.is_staff

class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, UpdateView):

    model = Comment
    fields = ['content']
    template_name = "Event/comment_update.html"  # use a dedicated template

    def get_success_url(self):
        return reverse_lazy('event_detail', kwargs={'pk': self.object.event.pk})

    def test_func(self):
        return self.request.user == self.get_object().user

#Report View 
class ReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        reason = request.POST.get("reason")

        if reason:
            Report.objects.create(user=request.user, event=event, reason=reason)
            return redirect("event_detail", pk=pk)

        return HttpResponse("Report reason is required.", status=400)

