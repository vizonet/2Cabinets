import datetime as dt
from datetime import timedelta
from django.db.models import Avg

from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from django.urls import reverse

from utils.choices import *
from utils.utils import short_str


class City(models.Model):
    """ Модель города. """
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "city"
        verbose_name_plural = "cities"

    def __str__(self):
        return f'{self.name}'


class Category(models.Model):   # в админке
    """ Модель категорий услуг. """
    name = models.CharField('Название', max_length=50)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def get_items_cnt(self, model=None):
        """Возвращает число объектов, связанных с текущей категорией."""
        if not model:
            model = Offer   # по умолчанию

        if isinstance(model, models.base.ModelBase):
            return model.objects.filter(category=self.pk, isDeleted=False).count()
        else:
            return None

    def get_absolute_url(self):
        return reverse('cat', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.name}'


class Offer(models.Model):
    """ Модель проектов исполнителя. """
    number = models.PositiveBigIntegerField('Номер', null=True)
    user = models.ForeignKey(User, verbose_name='Исполнитель', on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=100)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField('Описание', max_length=500)
    image = models.ImageField('Изображение', upload_to=settings.IMG_ROOT, null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.SET_DEFAULT, default=0)
    cost = models.DecimalField('Стоимость', max_digits=8, decimal_places=0)
    processPeriod = models.IntegerField('Дней на выполнение (min)')
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлён', auto_now=True)
    isDeleted = models.BooleanField('Удалён', default=False)

    def get_orders(self, current=True):
        """Возвращает QuerySet-коллекцию заказов по данному проекту."""
        kwargs = {'offer': self}
        if current:
            kwargs.update({'isDeleted': False, 'isAccepted': False})
        return Order.objects.filter(**kwargs)

    def get_users(self, current=True):
        """Возвращает QuerySet-коллекцию заказчиков данного проекта."""
        kwargs = {'order__offer': self}
        if current:  # выполняемые проекты
            kwargs.update({'order__isDeleted': False, 'order__isAccepted': False})
        return User.objects.filter(**kwargs)

    def get_users_str(self, current=True):
        """Возвращает строку перечисления заказчиков данного проекта."""
        lst = list(self.get_users(current))
        return ', '.join(set([i.username + f' ({lst.count(i)})' for i in lst]))

    @staticmethod
    def get_work(user):
        """Возвращает кортеж QuerySet-коллекции и её размера выполняемых проектов пользователя."""
        qs = Offer.objects.filter(user=user,
                                  isDeleted=False,
                                  order__isAccepted=False
                                  ).prefetch_related('order_set')
        return qs, qs.count()

    @staticmethod
    def get_work_cnt(user):
        """Возвращает число проектов пользователя в работе."""
        return Offer.get_work(user)[1]

    def get_accepted_orders_str(self):
        """Возвращает строку из коллекции выполненных заказов."""
        lst = list(Order.objects.filter(offer=self,
                                        isDeleted=False,
                                        isAccepted=True,
                                        ))
        return ', '.join(set([i.name + f' ({lst.count(i)})' for i in lst]))

    def short_desc(self):
        """Возвращает фрагмент описания проекта."""
        return short_str(self.description)
    short_desc.short_description = description.verbose_name     # для admin-панели

    def get_absolute_url(self):
        return reverse('offer', kwargs={'slug': self.slug})

    def __str__(self):
        return f'{self.title} ({self.user.username}): {self.cost}'


class Order(models.Model):
    """Модель заказов."""
    number = models.PositiveBigIntegerField(verbose_name='Номер', unique=True)
    offer = models.ForeignKey(Offer, verbose_name='Проект', on_delete=models.CASCADE)
    client = models.ForeignKey(User, verbose_name='Заказчик', on_delete=models.CASCADE)
    description = models.TextField('Описание', max_length=500, default='')
    # с момента создания заказа (либо с момента акцепта исполнителем)
    dateStart = models.DateTimeField('Дата начала обработки', auto_now_add=True)
    dateEndPlan = models.DateTimeField('Дата выполнения (план)', null=True, default=None)
    dateEndFact = models.DateTimeField('Дата выполнения (факт)', null=True, default=None)
    isAccepted = models.BooleanField('Принято заказчиком?', blank=True, default=False)
    dateAccept = models.DateTimeField('Дата принятия', null=True, default=None)
    score = models.SmallIntegerField('Оценка', null=True, default=0)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлён', auto_now=True)
    isDeleted = models.BooleanField('Удалён', default=False)            # архивация

    def set_date_plan(self):
        """Установить дату выполнения в соответствующий атрибут."""
        if not self.isDeleted and self.dateStart and self.offer.processPeriod:
            self.dateEndPlan = self.dateStart + timedelta(days=self.offer.processPeriod)

    def set_date_end_fact(self):
        """Установить фактическую дату выполнения заказа."""
        if not self.isDeleted and not self.isAccepted:
            self.dateEndFact = dt.date.today()

    def del_date_end_fact(self):
        """Удалить фактическую дату выполнения заказа."""
        if not self.isDeleted and not self.isAccepted:
            self.dateEndFact = None

    def set_accept(self, flag=True):
        """Установить атрибут приёмки заказа и дату приёмки."""
        if not self.isDeleted and self.dateEndFact:
            self.isAccepted = flag
            self.dateAccept = dt.date.today()

    def set_score(self, score):
        """Установить атрибут оценки заказа."""
        if self.isAccepted:
            self.score = score

    def __str__(self):
        return f'{self.offer.title} ({self.offer.user.username}): {self.offer.cost} для {self.client.username}'


class Portfolio(models.Model):
    """Модель ссылок на работы исполнителя."""
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    name = models.CharField('Наименование', max_length=50)
    dateRelease = models.DateField('Дата выпуска')
    url = models.URLField('Ссылка')
    description = models.TextField('Описание', max_length=300, blank=True)

    def short_url(self):
        """Возвращает фрагмент ссылки."""
        return short_str(self.url, 50)
    short_url.short_description = url.verbose_name                  # для admin-панели

    def short_desc(self):
        """Возвращает фрагмент описания."""
        return short_str(self.description)
    short_desc.short_description = description.verbose_name         # для admin-панели

    def __str__(self):
        return f'{self.name} ({self.user.username}) {self.dateRelease}'


class Profile(models.Model):
    """Модель профиля пользователя."""
    # общие атрибуты
    user = models.OneToOneField(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phoneNumber = models.CharField('Телефон', unique=True)
    photo = models.ImageField(verbose_name='Фото', upload_to=settings.IMG_ROOT, null=True, blank=True)
    gender = models.CharField('Пол', choices=GENDER, max_length=1)
    dateReg = models.DateField("Дата регистрации", auto_now_add=True)
    rate = models.FloatField('Рейтинг', null=True, blank=True, default=0)
    city = models.ForeignKey(City, verbose_name='Город', null=True, on_delete=models.SET_NULL)
    specializations = models.ManyToManyField(Category, verbose_name='Специализации', blank=True)

    @property
    def experience(self):
        """Опыт работы на платформе."""
        if self.dateReg is not None:
            return dt.date.today() - self.dateReg
        else:
            return 0

    def get_rate(self):
        """Возвращает рейтинг - среднюю оценку всех выполненных проектов."""
        rateAvg = Order.objects.filter(offer__user=self.user, isAccepted=True)\
            .aggregate(Avg("score", default=0))
        return rateAvg['score__avg']

    def get_specializations(self):
        """Возвращает строковое представление всех специализаций профиля."""
        return ', '.join([c.name for c in self.specializations.all()])
    get_specializations.short_description = specializations.verbose_name        # для admin-панели

    def __str__(self):
        return f'{self.user.username}: {self.phoneNumber}, {self.city}, {self.rate}, {self.get_specializations()}'
