from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import CreateView,DetailView,ListView,UpdateView,DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Event
from django.urls import reverse_lazy 

def home(request):
    return render(request,'base/base.html')


class CreateEvent(CreateView):
    model=Event
    fields=['title','description','category','location','date','start_time','end_time','image']
    template_name='Event/event_form.html'
    success_url=reverse_lazy('event_list')

    def form_valid(self,form):
        form.instance.organizer=self.request.user
        return super().form_valid(form)

class EventList(ListView):
    model=Event
    template_name='Event/event_list.html'
    context_object_name='events'
    ordering=['-start_time']
    paginate_by=10

class EventDetails(DetailView):
    mmodel=Event
    templatee_name='Event/event_detail.html'
    context_object_name='event'
class EventUpdate(LoginRequiredMixin, UpdateView):
    model = Event
    fields = ['title','description','category','date','location','start_time','end_time','image']
    template_name = 'Event/event_update.html'
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
