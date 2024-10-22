from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .forms import LoginForm, SignUpForm, UserUpdateForm, EventCreateForm
from .models import MyUser, Event, Tag
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.messages import get_messages
from datetime import datetime
import json
import pytz
from django.conf import settings


class UserLoginView(LoginView):
    template_name = 'event_hub/login.html'
    authentication_form = LoginForm

    def get_redirect_url(self):
        return reverse_lazy('event_hub:event_list')


class SignUpView(CreateView):
    template_name = 'event_hub/signup.html'
    form_class = SignUpForm

    def get_success_url(self):
        messages.success(self.request, "Account creation successful!")
        return reverse('event_hub:login')


def delete_img_if_new(new_image_name, old_image_name):
    if new_image_name != old_image_name:
        if default_storage.exists(old_image_name):
            default_storage.delete(old_image_name)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = MyUser
    form_class = UserUpdateForm
    template_name = 'event_hub/user_update_page.html'
    login_url = reverse_lazy('event_hub:login')
    success_url = reverse_lazy('event_hub:user_update')

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        if form.cleaned_data.get('avatar'):
            new_image_name = form.cleaned_data['avatar'].name
            old_image_name = self.get_object().avatar.name
            delete_img_if_new(new_image_name, old_image_name)

        return super().form_valid(form)

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return MyUser.objects.get(pk=self.request.user.id)


class UserDisplayView(LoginRequiredMixin, DetailView):
    model = MyUser
    template_name = 'event_hub/user_page.html'
    login_url = reverse_lazy('event_hub:login')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['event_list'] = self.object.organized_events.all()
        return context

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        username = self.kwargs.get('username')
        return get_object_or_404(MyUser, username=username)


class UserLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('event_hub:login')
    login_url = reverse_lazy('event_hub:login')


def handle_event_data(request, form, event_instance=None):
    short_description = form.cleaned_data['short_description']
    naive_datetime = datetime.fromisoformat(
        request.POST.get('datetime'))
    tz_name = request.POST.get('timezone')
    local_tz = pytz.timezone(tz_name)
    utc_datetime = local_tz.localize(naive_datetime).astimezone(pytz.utc)

    new_slug = slugify(
        f'{short_description}-{utc_datetime.strftime("%Y-%m-%dT%H%M")}-utc')

    form.instance.datetime = utc_datetime

    if event_instance is not None and form.cleaned_data.get('cover_image'):
        new_image_name = form.cleaned_data['cover_image'].name
        old_image_name = event_instance.cover_image.name
        delete_img_if_new(new_image_name, old_image_name)

    if event_instance is None or event_instance.slug != new_slug:
        form.instance.slug = new_slug

    if event_instance is None:
        form.instance.organizer = request.user

    if event_instance is None or event_instance.timezone != tz_name:
        form.instance.timezone = tz_name


class EventCreateView(LoginRequiredMixin, CreateView):
    template_name = 'event_hub/event_create_page.html'
    form_class = EventCreateForm

    def get_success_url(self) -> str:
        return reverse('event_hub:event_display', args=[self.object.slug])

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        handle_event_data(self.request, form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tags_list'] = context['form'].fields['tags'].queryset
        context['TIMEZONE_KEY'] = settings.TIMEZONE_KEY
        context['MAPBOX_KEY'] = settings.MAPBOX_KEY
        return context


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'event_hub/event_update_page.html'
    login_url = reverse_lazy('event_hub:login')

    def get_success_url(self) -> str:
        return reverse('event_hub:event_display', args=[self.object.slug])

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        handle_event_data(self.request, form, self.get_object())
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['tags_list'] = context['form'].fields['tags'].queryset
        context['selected_tags'] = list(context['event'].tags.all())
        context['short_description'] = ' '.join(
            context['event'].slug.split('-')[:-4])
        context['TIMEZONE_KEY'] = settings.TIMEZONE_KEY
        context['MAPBOX_KEY'] = settings.MAPBOX_KEY
        return context

    def dispatch(self, request, *args, **kwargs):
        event = get_object_or_404(Event, slug=self.kwargs['slug'])
        if event.organizer != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class EventDisplayView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = 'event_hub/event_page.html'
    login_url = reverse_lazy('event_hub:login')


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'event_hub/event_list_page.html'
    login_url = reverse_lazy('event_hub:login')
    paginate_by = 6

    def get_queryset(self):
        title = self.request.GET.get('title')

        if title:
            return Event.objects.filter(title__icontains=title).order_by('datetime')

        return Event.objects.all().order_by('datetime')


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    login_url = reverse_lazy('event_hub:login')

    def get_success_url(self) -> str:
        return reverse('event_hub:user_display', args=[self.request.user.username])

    def dispatch(self, request, *args, **kwargs):
        event = get_object_or_404(Event, slug=self.kwargs['slug'])
        if event.organizer != request.user:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


@login_required(login_url='event_hub:login')
def tag_create_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        tag_name = data.get('tag_name')

        if not tag_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Tag name is required'
            }, status=400)

        try:
            tag = Tag.objects.create(name=tag_name)
            return JsonResponse({
                'status': 'success',
                'message': 'Tag created successfully',
                'tag': {
                    'id': tag.id,
                    'name': tag.name
                }
            }, status=201)
        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Tag with this name already exists'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': 'An error occurred'
            }, status=500)

    else:
        raise Http404()
