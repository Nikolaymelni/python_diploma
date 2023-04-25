from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator


STATE_CHOICES = (
    ('basket', 'Basket'),
    ('new', 'New'),
    ('confirmed', 'Confirmed'),
    ('assembled', 'Assembled'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('canceled', 'Canceled'),
)

USER_TYPE_CHOICES = (
    ('shop', 'Shop'),
    ('buyer', 'Buyer'),
)

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Компания', max_length=40, blank=True)
    position = models.CharField(verbose_name='Должность', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')
    url = models.URLField(verbose_name='Link', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='User',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    state = models.BooleanField(verbose_name='Order status', default=True)


    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = "Shops"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, verbose_name='Shops', related_name='categories',)
    name = models.CharField(max_length=100, verbose_name='Name')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name='Category', related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name='Name')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products List'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField(max_length=80, verbose_name='Model', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='External ID')
    product = models.ForeignKey(Product, related_name='product_infos', verbose_name='Category', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Shop', related_name='product_infos', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Amount')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price')
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Recommend retail price')

    class Meta:
        verbose_name = 'Product Info'
        verbose_name_plural = "Product Info List"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Name')

    class Meta:
        verbose_name = 'Parameter Name'
        verbose_name_plural = "Parameters List"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name='Product info', related_name='product_parameters', blank = True, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Parameter', related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField(max_length=100, verbose_name='Value')

    class Meta:
        verbose_name = 'Parameter'
        verbose_name_plural = "Parameters List"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]


class Contact(models.Model):
    user = models.ForeignKey(User, verbose_name='User',
                             related_name='contacts', blank=True,
                             on_delete=models.CASCADE)

    city = models.CharField(max_length=50, verbose_name='City')
    street = models.CharField(max_length=100, verbose_name='Street')
    house = models.CharField(max_length=15, verbose_name='House', blank=True)
    apartment = models.CharField(max_length=15, verbose_name='Apartment', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Phone Number')

    class Meta:
        verbose_name = 'Contacts'
        verbose_name_plural = "Contacts List"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE, verbose_name='User', blank=True,)
    state = models.CharField(verbose_name='Status', choices=STATE_CHOICES, max_length=20)
    dt = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey(Contact, verbose_name='Contact', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = "Orders List"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Order',
                              related_name='ordered_items', blank=True, on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Product Info', related_name='ordered_items',
                                     blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Amount')

    class Meta:
        verbose_name = 'Ordered item'
        verbose_name_plural = 'Ordered items list'
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Email confirmation token'
        verbose_name_plural = 'Email confirmation tokens'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    user = models.ForeignKey(User, related_name='confirm_email_tokens', on_delete=models.CASCADE,
                             verbose_name=_("The User which is associated to this password reset token"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("When was this token generated"))
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)