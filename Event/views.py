from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Event,Category,Like,ChatRoom,Comment,Report,EventRegistration
from django.urls import reverse_lazy 
from django.views import View
from django.contrib import messages
from .forms import CategoryForm 
from django.utils import timezone

from user.models import Notification
from django.urls import reverse

import random
from collections import defaultdict
from django.db.models import (
    Q,
    Count,
    Case,
    When,
    Value,
    OuterRef,
    Exists,
    F,
    IntegerField ,
    CharField,
    
)


from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from .utils import with_likes, generate_qr_code, search_events,check_and_block_event_owner
from .selectors import get_event_participants

# Event Views
class CreateEvent(CreateView):
    model=Event
    fields=['title','description','category','location','date','start_time','end_time','image']
    template_name='Event/event_form.html'
    success_url=reverse_lazy('event_list')

    def form_valid(self,form):
        form.instance.organizer=self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class JoinEvent(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        user = request.user

        if user == event.organizer:
            return JsonResponse({"error": "Organizer cannot join"}, status=403)

        registration = EventRegistration.objects.filter(
            event=event,
            user=user
        ).first()

        if registration:
            registration.delete()
            joined = False
        else:
            EventRegistration.objects.create(
                event=event,
                user=user
            )
            joined = True

        participants_count = EventRegistration.objects.filter(event=event).count()

        return JsonResponse({
            "joined": joined,
            "participants_count": participants_count
        })

@method_decorator(ensure_csrf_cookie, name='dispatch')
class EventDetails(DetailView):
    model = Event
    template_name = 'Event/event_detail.html'
    context_object_name = 'event'

    def get_queryset(self):
        qs = super().get_queryset()
        return with_likes(qs, self.request.user)


class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    fields = ['title','description','category','date','location','start_time','end_time','image']
    template_name='Event/event_form.html'
    success_url = reverse_lazy('event_list')

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class EventDelete(LoginRequiredMixin,DeleteView):
    model=Event
    template_name='Event/event_delete.html'
    success_url=reverse_lazy('event_list')

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


# Event Filter Views


class EventList(ListView):
    model=Event
    template_name='Event/event_list.html'
    context_object_name='events'

    def get_queryset(self):
        qs = Event.objects.all().order_by('-start_time')

        category_filter = self.request.GET.get('category')
        if category_filter:
            qs = qs.filter(category__id=category_filter)

        return with_likes(qs, self.request.user)


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
                When(date__date=now.date(), then=Value('ongoing')),
                When(date__lt=now, then=Value('completed')),
                When(date__gt=now, then=Value('upcoming')),
                default=Value('ongoing'),
                output_field=CharField()
            )
        )

        status_filter = self.request.GET.get('status', 'all').lower()
        if status_filter in ['completed', 'ongoing', 'upcoming']:
            qs = qs.filter(status__iexact=status_filter)

        # 🔴 REQUIRED FOR HEART STATE CONSISTENCY
        return with_likes(qs, self.request.user)

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


class joinedEvents(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'Event/joined_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        qs = Event.objects.filter(registrations__user=user).annotate(
            status=Case(
                When(date__lt=now, then=Value('completed')),
                When(date__gt=now, then=Value('upcoming')),
                default=Value('ongoing'),
                output_field=CharField()
            ),
            is_registered=Exists(
                EventRegistration.objects.filter(event=OuterRef('pk'), user=user)
            )
        )

        status_filter = self.request.GET.get('status', 'all').lower()
        if status_filter in ['completed', 'ongoing', 'upcoming']:
            qs = qs.filter(status=status_filter)

        return with_likes(qs.order_by('-start_time'), user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        joined_events = Event.objects.filter(registrations__user=self.request.user)

        context['current_status'] = self.request.GET.get('status', 'all')
        context['total_events'] = joined_events.count()
        context['completed_events_count'] = joined_events.filter(date__lt=now).count()
        context['ongoing_events_count'] = joined_events.filter(date__date=now.date()).count()
        context['upcoming_events_count'] = joined_events.filter(date__gt=now).count()
        return context


class LikedEvents(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'Event/liked_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        qs = (
            Event.objects
            .filter(like__user=self.request.user)
            .order_by('-like__created_at')
            .distinct()
        )
        return with_likes(qs, self.request.user)


# Category Views
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

#Like view 
class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        like, created = Like.objects.get_or_create(
            user=request.user,
            event=event
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True
            if event.organizer != request.user:
                Notification.objects.create(
                    sender=request.user,
                    receiver=event.organizer,
                    event=event,
                    message=f"{request.user.username} liked your event {event.title}",
                    action_url=reverse("event_detail", kwargs={"pk": event.pk}),
                    type="Like"
                )

        likes_count = Like.objects.filter(event=event).count()

        # ✅ RETURN JSON ONLY FOR AJAX
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "liked": liked,
                "likes_count": likes_count
            })

        # ✅ NORMAL POST → REDIRECT BACK
        return redirect(request.META.get("HTTP_REFERER", "events"))

#Chatroom
class ChatRoomView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs["pk"])
        self.chatroom, _ = ChatRoom.objects.get_or_create(event=self.event)
        return super().dispatch(request, *args, **kwargs)

    def has_access(self):
        user = self.request.user
        return (
            user.is_superuser
            or user == self.event.organizer
            or EventRegistration.objects.filter(event=self.event,user=user).exists()
        )

    def get(self, request, pk):
        can_access = self.has_access()

        return render(request, "Event/chatroom.html", {
            "chatroom": self.chatroom,
            "messages": self.chatroom.messages.all() if can_access else None,
            "event": self.event,
            "can_access": can_access,
        })

    def post(self, request, pk):
        if not self.has_access():
            return redirect("join_event", pk=self.event.pk)

        content = request.POST.get("content")
        if content:
            self.chatroom.messages.create(
                user=request.user,
                content=content
            )

            if request.user != self.event.organizer:
                Notification.objects.create(
                    sender=request.user,
                    receiver=self.event.organizer,
                    event=self.event,
                    message=f"{request.user.username} sent a message in {self.event.title}",
                    action_url=reverse("chat_room", kwargs={"pk": pk}),
                    type="Message",
                )

        return redirect("chat_room", pk=pk)

#comment Views
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
                # Reply to an existing comment
                parent_comment = get_object_or_404(Comment, id=parent_id, event=event)
                new_comment = Comment.objects.create(
                    user=request.user,
                    content=content,
                    event=event,
                    parent=parent_comment
                )
                # Notify the parent comment's author
                if parent_comment.user != request.user:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=parent_comment.user,
                        event=event,
                        message=f"{request.user.username} replied to your comment: {parent_comment.content}",
                        action_url = reverse('comment_event', kwargs={'pk': event.pk}) + f"?highlight={new_comment.id}",
                        type="Comment"
                    )
            else:
                new_comment = Comment.objects.create(
                    user=request.user,
                    content=content,
                    event=event
                )
                if event.organizer != request.user:
                    Notification.objects.create(
                        sender=request.user,
                        receiver=event.organizer,
                        event=event,
                        message=f"{request.user.username} commented on your event {event.title}",
                        action_url = reverse('comment_event', kwargs={'pk': event.pk}) + f"?highlight={new_comment.id}",
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
        self.object = form.save()
        return HttpResponseRedirect(
            reverse_lazy(
                'comment_event',
                kwargs={'pk': self.object.event.pk}
            )
        )

    def test_func(self):
        return self.request.user == self.get_object().user


#Report View 
class ReportView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        reason = request.POST.get("reason")
        
        if Report.objects.filter(user=request.user,event=event).exists():
            return JsonResponse({
                "status": "error",
                "message": "You have already reported this event."
            })

        if event.organizer == request.user:
            return JsonResponse({
                "status": "error",
                "message": "You cannot report your own event."
            })


        if reason:
            Report.objects.create(user=request.user, event=event, reason=reason)
            check_and_block_event_owner(event.organizer)

            return JsonResponse({
                "status": "success",
                "message": "Event reported successfully."
            })

        return JsonResponse({
            "status": "error",
            "message": "Report reason is required."
        }, status=400)

#Search View
class EventSearchView(LoginRequiredMixin, ListView):
    template_name = 'Event/search_event.html'
    context_object_name = "results"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        if not query:
            return Event.objects.none()
        qs = search_events(query, limit=20)
        return with_likes(qs, self.request.user)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


# Personalization View
class PersonalizedEventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "Event/event_list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        user = self.request.user

        preferred_categories = (
            Event.objects.filter(registrations__user=user)
            .values_list("category_id", flat=True)
        )

        qs = (
            Event.objects
            .exclude(registrations__user=user)
            .select_related("category", "organizer")
            .annotate(
                category_match=Case(
                    When(category_id__in=preferred_categories, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                ),
                liked_by_user=Count(
                    "like",
                    filter=Q(like__user=user),
                ),
            )
        )

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category_id=category)

        # 🔴 convert to list ONLY for scoring
        events = list(qs)

        for event in events:
            event.personalization_score = (
                event.category_match * 3 +
                event.liked_by_user * 1
            )

        events.sort(
            key=lambda e: (e.personalization_score, e.created_at),
            reverse=True
        )

        # 🔴 CRITICAL: go back to QuerySet + apply with_likes
        qs = Event.objects.filter(pk__in=[e.pk for e in events])
        qs = qs.annotate(
            personalization_order=Case(
                *[
                    When(pk=e.pk, then=Value(i))
                    for i, e in enumerate(events)
                ],
                output_field=IntegerField()
            )
        ).order_by("personalization_order")

        return with_likes(qs, user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get("category")
        return context

def sidebar_view(request):
    return render(request,'base/sidebar.html')

class RegistrationQRView(LoginRequiredMixin, View):
    def get(self, request, event_id):
        registration = get_object_or_404(
            EventRegistration,
            event_id=event_id,
            user=request.user
        )
        qr_image = generate_qr_code(registration.qr_token)
        return HttpResponse(qr_image, content_type="image/png")

class Participants(LoginRequiredMixin, View):

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk, organizer=request.user)

        participants = get_event_participants(event).values(
            "id", "username", "email"
        )

        return JsonResponse(list(participants), safe=False)