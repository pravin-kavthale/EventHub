from django.shortcuts import render,redirect, get_object_or_404,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Event,Category,Like,ChatRoom,EventAttendance,Comment,Report
from django.urls import reverse_lazy 
from django.db.models import Count
from django.views import View
from django.contrib import messages
from .forms import CategoryForm 
from django.utils import timezone
from django.db.models import Case, When, Value, CharField
from user.models import Notification

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
            Notification.objects    .create(
                sender=request.user,
                receiver=event.organizer,
                message=f"{request.user} has joined your event {event}",
                type='Join',
            )
        return redirect('event_detail', pk=pk)

    def test_func(self):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return self.request.user != event.organizer

class EventList(ListView):
    model=Event
    template_name='Event/event_list.html'
    context_object_name='events'

    def get_queryset(self):
        qs=Event.objects.all().order_by('-start_time')
        category_filter = self.request.GET.get('category')  
        if category_filter:
            qs = qs.filter(category__id=category_filter)
        user = self.request.user
        for event in qs:
            event.is_liked = event.is_likeby(user)
        return qs

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['categories']=Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class MyEvents(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'Event/MyEvents.html'
    context_object_name = 'events'

    def get_queryset(self):
        now = timezone.now()

        qs = Event.objects.filter(organizer=self.request.user)

        qs = qs.annotate(
        status=Case(
                    When(
                                date__date=now.date(),
                                start_time__lte=now.time(),
                                end_time__gte=now.time(),
                                then=Value('ongoing')
                        ),
                    When(date__lt=now, then=Value('completed')),
                    When(date__gt=now, then=Value('upcoming')),
                    default=Value('ongoing'),
                    output_field=CharField()
                )
        )
        status_filter = self.request.GET.get('status', 'all').lower()
        if status_filter in ['completed', 'ongoing', 'upcoming']:
            qs = qs.filter(status__iexact=status_filter)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user_events = Event.objects.filter(organizer=self.request.user)

        context['current_status'] = self.request.GET.get('status', 'all').lower()
        context['total_events'] = user_events.count()
        context['completed_events_count'] = user_events.filter(date__lt=now).count()
        context['ongoing_events_count'] = user_events.filter(date=now.date()).count()
        context['upcoming_events_count'] = user_events.filter(date__gt=now).count()
        
        return context

class joinedEvents(LoginRequiredMixin,ListView):
    model=Event
    template_name='Event/joined_events.html'
    context_object_name='events'

    def get_queryset(self):
        status_filter=self.request.GET.get('status','all').lower()
        qs=Event.objects.filter(participants=self.request.user)

        qs=qs.annotate(status=Case(
            When(date__lt=timezone.now(),then=Value('completed')),
            When(date__gt=timezone.now(),then=Value('upcoming')),
            default=Value('ongoing'),
            output_field=CharField()            
        ))

        if status_filter in ['completed','ongoing','upcoming']:
            qs=qs.filter(status=status_filter)
        return qs.order_by('-start_time')
    
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        now=timezone.now()
        Joined_events=Event.objects.filter(participants=self.request.user)
        context['current_status']=self.request.GET.get('status','all')
        context['total_events']=Joined_events.count()
        context['completed_events_count']=Joined_events.filter(date__lt=now).count()
        context['ongoing_events_count']=Joined_events.filter(date=now.date()).count()
        context['upcoming_events_count']=Joined_events.filter(date__gt=now).count()

        return context

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
        else:
            if event.organizer != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=event.organizer,
                    event=event,
                    message=f"{request.user.username} has liked your event {event.title}",
                    type='Like'
                )
        return redirect(request.META.get('HTTP_REFERER', '/'))

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
class CommentView(LoginRequiredMixin, View):
    template_name = 'Event/event_comments.html'
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        comments = event.comments.filter(parent__isnull=True).order_by('-created_at')
        return render(request, self.template_name, {'event': event, 'comments': comments})
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if not event.comments_enabled:
            return HttpResponse("Comments are disabled for this event.", status=403)
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')  

        if content:
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id, event=event)
                Comment.objects.create(user=request.user, content=content, event=event, parent=parent_comment)
                if parent_comment.user != request.user:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=parent_comment.user,
                        event=event,
                        message=f"{request.user} replied to your comment {parent_comment.content}",
                        type="Comment"
                    )
            else:
                Comment.objects.create(user=request.user, content=content, event=event)
                if event.organizer!=request.user:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=event.organizer,
                        event=event,
                        message=f"{request.user} Commented on your event {event.title}",
                        type="Comment"
                    )
        return redirect('comment_event', pk=pk)

class DeleteComment(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'Event/comment_confirm_delete.html'
    context_object_name = "comment"

    def get_success_url(self):
        return reverse_lazy('comment_event', kwargs={'pk': self.object.event.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.user or self.request.user.is_staff

class UpdateComment(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    fields = ['content']
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse_lazy('comment_event', kwargs={'pk': self.object.event.pk}))

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('comment_event', kwargs={'pk': self.get_object().event.pk}))

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
