from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView
from django.utils.translation import gettext_lazy as _, ngettext
from django.views.decorators.cache import cache_page

from random import random

from myauth.models import Profile


# class HelloView(View):
#     welcome_message = _('welcome hello world!')
#
#     def get(self, request: HttpRequest) -> HttpResponse:
#         items_str = request.GET.get_object_or_404('items') or 0
#         items = int(items_str)
#         product_line = ngettext(
#             'One product',
#             '{count} products',
#             items
#         )
#         product_line = product_line.format(count=items)
#
#         return HttpResponse(
#             f'<h1>{self.welcome_message}</h1>'
#             f'<h2>{product_line}</h2>'
#         )


class AboutMeView(TemplateView):
    template_name = 'myauth/about-me.html'


    # def get(self, request: HttpRequest, pk: int) -> HttpResponse:
    #     profile = get_object_or_404(Profile, pk=pk)
    #     context = {
    #         'profile': profile
    #     }
    #     return render(request, 'myauth/about-me.html', context=context)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = 'myauth/register.html'
    success_url = reverse_lazy('myauth:about-me')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('/admin/')

    return render(request, 'myauth/login.html', {'error': 'Invalid username or password.'})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse('myauth:login'))


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse('Cookie set')
    response.set_cookie('fizz', 'buzz', max_age=3600)
    return response


@cache_page(60 * 2)
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get('fizz', 'default_value')
    return HttpResponse(f'Cookie value: {value!r} + {random()}')


@permission_required('myauth.view_profile', raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session['foobar'] = 'spameggs'
    return HttpResponse('Session set!')


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get('foobar', 'default_value')
    return HttpResponse(f'Session valu: {value!r}')


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({'foo': 'bar', 'spam': 'eggs'})


# class UpdateAvatarView(UpdateView):
#     queryset = Profile.objects.select_related('user')
#     template_name = 'myauth/update-avatar.html'
#     fields = 'avatar',
#     # success_url = reverse_lazy('myauth:about-me')
#     #
#     # def get_success_url(self):
#     #     return reverse(
#     #         'myauth:update-avatar',
#     #         kwargs={'pk': self.object.pk}
#     #     )
#
#     def get_queryset(self):
#         user = self.request.user
#         print(user)
#         q = Profile.objects.get(user_id=3)
#         print(q)
#         print(q.bio)
#         return q
