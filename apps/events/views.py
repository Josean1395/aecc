from datetime import date

from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import redirect, get_object_or_404
from django.http import Http404

from .models import Event, Hackathon
from .mixins import MonthMixin

from .constants import MONTHS


class IndexView(MonthMixin, ListView):
    model = Event
    paginate_by = 5
    template_name = 'events/index.html'
    context_object_name = 'events_information'


class EventView(DetailView):
    model = Event
    slug_field = 'title_slug'
    slug_url_kwarg = 'title_slug'
    template_name = 'events/event.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventView, self).get_context_data(**kwargs)
        event = Event.objects.get(title_slug=self.kwargs['title_slug'])
        context['is_current_date'] = event.event_date == date.today()
        context[
            'has_checked_in'] = self.request.user in event.checked_in.all()
        return context


class HackathonView(TemplateView):
    model = Hackathon
    template_name = 'events/hackathon.html'
    context_object_name = 'hackathon_sponsors'

    def get_context_data(self, **kwargs):
        context = super(HackathonView, self).get_context_data(**kwargs)
        context['hackathon_sponsors'] = Hackathon.objects.all()
        return context


class EventByMonth(ListView):
    model = Event
    paginate_by = 5
    context_object_name = 'events'
    template_name = 'events/events_by_month.html'

    def get_queryset(self):
        return Event.objects.filter(month=self.kwargs['month'])

    def get_context_data(self, **kwargs):
        if self.kwargs['month'] not in MONTHS:
            raise Http404
        context = super(EventByMonth, self).get_context_data(**kwargs)
        context['month'] = self.kwargs['month']
        return context

# TODO - create a form. This causes a leak
def participating(request, **kwargs):
    event = get_object_or_404(Event, title_slug=kwargs['month'])
    event.checked_in.add(request.user.id)
    event.save()
    return redirect("/events/%s/%s" % (kwargs['title_slug'], kwargs['month'],))
