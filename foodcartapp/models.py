from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Count, F, Q, Sum
from django.db.models.query import QuerySet
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class RestaurantQuerySet(models.QuerySet):
    def suitable_for_order(self, order):
        order_products = OrderItem.objects.filter(order=order)
        return self.annotate(
            prod_count=Count(
                'menu_items__product',
                filter=Q(menu_items__product__in=order_products.values(
                    'product')) & Q(menu_items__availability=True)
            )
        ).filter(prod_count=order_products.count())


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    objects = RestaurantQuerySet.as_manager()

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderQuerySet(QuerySet):
    def with_costs(self):
        return self.annotate(
            cost=Sum(F('items__quantity') * F('items__price'))
        )

    def active(self):
        return self.filter(status__in=[0, 1, 2])


class Order(models.Model):
    firstname = models.CharField(
        'имя',
        max_length=50,
        db_index=True,
    )
    lastname = models.CharField(
        'фамилия',
        max_length=50,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        'телефон',
        db_index=True
    )
    address = models.CharField(
        'адрес',
        max_length=150,
        db_index=True,
    )
    status = models.PositiveSmallIntegerField(
        'статус',
        choices=[
            (0, 'Новый'),
            (1, 'Собирается'),
            (2, 'Доставляется'),
            (3, 'Выполнен'),
        ],
        default=0,
        db_index=True,
    )
    comment = models.TextField(
        'комментарий',
        blank=True,
    )
    registered_at = models.DateTimeField(
        'дата создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'дата звонка',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'дата доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    payment = models.PositiveSmallIntegerField(
        'способ оплаты',
        choices=[
            (0, 'Наличные'),
            (1, 'Электронно'),
        ],
        db_index=True,
    )
    provider = models.ForeignKey(
        Restaurant,
        related_name='orders',
        verbose_name='ресторан-поставщик',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        verbose_name='заказ',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        verbose_name='продукт',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveSmallIntegerField(
        'количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'продукт в заказе'
        verbose_name_plural = 'продукты в заказе'

    def __str__(self):
        return f'{self.product} {self.order}'
