from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance
from geopy.exc import GeopyError

from foodcartapp.models import Order, Product, Restaurant
from geocoderapp.models import GeoPoint


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability
                for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id]
                                for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.with_costs().active()
    restaurants_with_distance = []
    for order in orders:
        if order.provider:
            restaurants_with_distance.append([])
            continue

        suitable_restaurants = Restaurant.objects.suitable_for_order(order)
        distances = ['нет данных'] * len(suitable_restaurants)

        order_point, _ = GeoPoint.objects.get_or_create(
            address=order.address)
        try:
            if not order_point.calculated:
                order_point.fill_coordinates()
        except (GeopyError, TypeError):
            restaurants_with_distance.append(
                list(zip(suitable_restaurants, distances)),
            )
            continue
        order_coords = (order_point.latitude, order_point.longitude)

        for index, restaurant in enumerate(suitable_restaurants):
            restaurant_point, _ = GeoPoint.objects.get_or_create(
                address=restaurant.address
            )
            try:
                if not restaurant_point.calculated:
                    restaurant_point.fill_coordinates()
            except (GeopyError, TypeError):
                continue

            restaurant_coords = (
                restaurant_point.latitude,
                restaurant_point.longitude
            )
            restaurant_distance = distance.distance(
                order_coords,
                restaurant_coords
            ).km
            distances[index] = f'{restaurant_distance:.2f} км.'

        restaurants_with_distance.append(
            sorted(
                tuple(zip(suitable_restaurants, distances)),
                key=lambda item: item[1],
            )
        )
    orders_with_restaurants = list(zip(orders, restaurants_with_distance))

    return render(request, template_name='order_items.html', context={
        'orders': orders_with_restaurants,
    })
