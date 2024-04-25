from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from utils.utils import *
from utils.context import *
from app.models import *
from app.forms import *
from django.contrib.auth.decorators import login_required


def ctx_dynamic(request):
    """Возвращает словарь общего контекста (контекст динамический)."""
    user = request.user if request.user.is_authenticated else None
    categories = Category.objects.all()
    counts = {cat.name: cat.get_items_cnt() for cat in categories}

    ctx = {
        'year': datetime.now().year,                            # текущий год
        'categories': categories,                               # список категорий
        'counts': counts,                                       # число объектов в категории
    }
    if user:
        ctx.update({
            'inworkCnt': Offer.get_work_cnt(user)               # число проектов в работе у пользователя
        })
    return ctx


def get_ctx_common(request):
    """Возвращает общий контекст сайта."""
    ctx = ctx_add(CTX_STATIC)
    ctx.update(ctx_dynamic(request))
    return ctx


def get_number(model):
    """Возвращает номер для соответствующего атрибута модели."""
    if not isinstance(model, models.base.ModelBase):
        return HttpResponse(
            f'<h1 class="text-danger">ERROR: ({get_number.__name__}) параметр не является моделью!</h1>'
        )
    qs = model.objects.all()
    cnt = qs.count() + 1
    lst = list(qs)

    find = False
    while not find:
        for i in lst:
            if i.number == cnt:
                cnt += 1
                break
            if i == lst[-1]:
                find = True
    return cnt


def updates(request):
    """Проверки состояний заказов, проектов."""
    # TODO: Установить атрибут рейтинга пользователей


def search(request):
    """Поиск в проектах, заказах. """
    # TODO: Поиск


def index(request):
    """(view) Главная страница."""
    template = 'app/index.html'
    context = get_ctx_common(request)

    kwargs = {'isDeleted': False}
    offersQuery = get_query(Offer, **kwargs).order_by('cost')         # список всех предлагаемых услуг
    offersCnt = offersQuery.count()

    # список профилей исполнителей
    workers = Profile.objects.filter(specializations__isnull=False).distinct().order_by('user__username')

    context.update({
        # общие параметры странице
        'style': {
            'widthRight': '100',  # %
            'bar': {'bg': 'bg-warning', 'text': 'text-black-50'},
        },

        # боковой блок
        'sidebar': {
            'title': f'Исполнители ({workers.count()})',
        },

        'query': offersQuery,
        'users': workers,

        # все проекты
        'current': {
            'count': offersCnt,
            'item_template': 'app/card-offer.html',
            'titleBar': 'Действующих проектов нет!',
            'titleList': f'Все проекты ({offersCnt}):',
            'query': offersQuery,
            'style': {
                'bar': {'bg': 'bg-primary', 'text': None},
                'visibility': '',
                'elem_id': 'current',
            },
        },
    })
    return render(request, template, context)


def category(request, pk):
    """(view) Возвращает выборку объектов по категориям."""
    template = 'app/category.html'
    context = get_ctx_common(request)

    categoryObj = Category.objects.filter(pk=pk).first()

    # проекты пользователей: не закрытые
    kwargs = {'isDeleted': False}

    if categoryObj:
        query = Offer.objects.filter(category=categoryObj, **kwargs)
    else:
        query = Offer.objects.filter(**kwargs)

    titleBar = f'Проекты категории "{categoryObj.name}" ({query.count()}):'

    context.update({
        'sidebar': False,
        'titleBar': titleBar,
        'item_template': 'app/card-offer.html',
        'query': query,
    })
    return render(request, template, context)


@login_required
def profile(request):
    """(view) Страница профиля пользователя."""
    template = 'app/profile.html'
    context = get_ctx_common(request)      # общий контекст
    errorsForm = None               # ошибки формы

    # начальные данные в форме
    user = request.user
    userProfile = Profile.objects.filter(user=user).first()     # or None
    initial = {'userName': user.username}

    savedOK = False
    # форма профиля
    profileForm = ProfileForm(request.POST or None, request.FILES or None, instance=userProfile, initial=initial)
    if request.method == 'POST':
        if profileForm.is_valid():
            profileObj = profileForm.save(commit=False)
            profileObj.rate = profileObj.get_rate()
            profileObj.save()
            savedOK = True

            # обработка связанной модели User
            if profileForm.cleaned_data['userName'] != user.username:
                user.username = profileForm.cleaned_data['userName']
                user.save()
        else:
            errorsForm = profileForm.errors

    context.update({
        'profileForm': profileForm,
        'errorsForm': errorsForm,
        'savedOK': savedOK,
        'title': f'Профиль "{ user.username }"',
        'titleBar': f'Профиль пользователя "{ user.username }":',
    })
    return render(request, template, context)


@login_required
def offer(request, pk):
    """(view) Страница просмотра параметров проекта. Заказ проекта заказчиком."""
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({({offer.__name__}) }) Не указан номер проекта!</h1>')

    template = 'app/offer.html'
    context = get_ctx_common(request)

    offerObj = Offer.objects.filter(pk=pk).first()

    title = f'Проект #{offerObj.number}'
    context.update({
        'title': title,
        'titleBar': title + ':',
        'offer': offerObj,
        'process': f'Заказать за {offerObj.cost} {RUB}'
    })
    return render(request, template, context)


@login_required
def offer_edit(request, pk=None):
    """(view) Страница создания/редактирования заказа."""
    template = 'app/offer-form.html'
    context = get_ctx_common(request)
    errorsForm = None

    if pk:
        offerObj = Offer.objects.filter(pk=pk).first()
        titleBar = f'Проект #{offerObj.number}:'
    else:
        offerObj = Offer(
            user=request.user,
            number=get_number(Offer)
        )
        titleBar = 'Новый проект:'

    savedOK = False     # результат сохранения формы
    offerForm = OfferForm(request.POST or None, request.FILES or None, instance=offerObj)   # форма проекта

    if request.method == 'POST':
        if offerForm.is_valid():
            offerForm.save()
            savedOK = True

            # добавить специализацию проекта к профилю пользователя
            profileObj = Profile.objects.filter(user=request.user).first()
            profileObj.specializations.add(offerForm.cleaned_data['category'])

            # TODO: Корректировка набора специализаций профиля согласно действующим проектам
        else:
            errorsForm = offerForm.errors

    context.update({
        'offerForm': offerForm,
        'errorsForm': errorsForm,
        'savedOK': savedOK,
        'title': titleBar,
        'titleBar': titleBar,
    })
    return render(request, template, context)


@login_required
def offer_delete(request, pk, flag=1):
    """Восстановить проект (атрибут isDeleted = False)."""
    # TODO: Проверка на действующий статус перед удалением
    Offer.objects.filter(pk=pk).update(isDeleted=bool(int(flag)))
    return redirect(cab_worker)   # перенаправление в кабинет исполнителя


def offers(request, username=None):
    """(view) Страница проектов пользователя."""
    template = 'app/index.html'
    context = get_ctx_common(request)

    if username:
        user = User.objects.get(username=username)
        kwargs = {'user': user, 'isDeleted': False}
        offersQuery = get_query(Offer, **kwargs)                        # проекты заданного пользователя

        if username == request.user.username:
            titleList = f'Мои проекты'
        else:
            titleList = f'Проекты исполнителя "{user}"'
    else:
        offersQuery = get_query(Offer, isDeleted=False)                  # проекты всех пользователей
        titleList = f'Все проекты'

    # все проекты
    offersQuery = offersQuery.order_by('cost')
    offersCnt = offersQuery.count()
    titleList += f' ({offersCnt}):'

    # все исполнители
    workers = Profile.objects.filter(user__is_active=True, specializations__isnull=False)\
        .distinct().order_by('user__username')

    context.update({
        # общие параметры странице
        'title': SITE_NAME,
        'style': {
            'widthRight': '75',  # %
            # 'bar': {'bg': 'bg-success', 'text': 'text-light'},
        },
        # боковой блок
        'sidebar': {
            'title': f'Исполнители ({workers.count()})',
        },
        'query': offersQuery,
        'users': workers,

        # Действующих проекты
        'current': {
            'count': offersCnt,
            'item_template': 'app/card-offer.html',
            'titleBar': 'Действующих проектов нет!',
            'titleList': titleList,
            'query': offersQuery,
            'style': {
                'bar': {'bg': 'bg-primary', 'text': None},
                'visibility': '',
                'elem_id': 'current',
            },
        },
    })
    return render(request, template, context)


@login_required
def offers_inwork(request):
    """(view) Возвращает коллекцию проектов пользователя в обработке для заказчиков."""
    template = 'app/offers-work.html'
    context = get_ctx_common(request)

    user = request.user
    inworkQuery, inworkCnt = Offer.get_work(user)

    title = f'Проекты "{user}" в работе ({inworkCnt}):'
    context.update({
        'title': title,
        'titleBar': title,

        # проекты в работе
        'inwork': {
            'count': inworkCnt,
            'item_template': 'app/card-offer.html',
            'titleBar': 'Проектов в работе нет!',
            'titleList': f'Мои проекты в работе ({inworkCnt}):',
            'query': inworkQuery,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-primary', 'text': ''},
                'visibility': '',
                'elem_id': 'inwork',
            },
        },

    })
    return render(request, template, context)


@login_required
def order_new(request, pkOffer):
    """(view) Создание нового заказа и перенаправление на страницу детализации."""
    msg = f'ERROR: ({order_new.__name__}) Невозможно создать заказ!'
    if not pkOffer:
        return HttpResponse(f'<h1 class="text-danger">{msg} Нет номера проекта!</h1>')

    template = 'app/order-form.html'
    context = get_ctx_common(request)
    errorsForm = None
    try:
        print(f'INFO: Попытка создания нового заказа по проекту (id {pkOffer})')
        offerObj = Offer.objects.filter(pk=pkOffer).first()

        if offerObj.user == request.user:
            txt = 'Нельзя заказать свой проект!'
            print(txt)
            return HttpResponse(f'<h1>{txt}</h1>')

        # создать объект заказа
        orderObj = Order(
            offer_id=pkOffer,
            number=get_number(Order),
            client=request.user,
            dateStart=dt.date.today()
        )
        # добавить параметры в заказ
        orderObj.set_date_plan()

        savedOK = False
        # форма заказа
        orderForm = OrderForm(request.POST or None, instance=orderObj)
        if request.method == 'POST':
            if orderForm.is_valid():
                orderForm.save()
                # savedOK = True
                print(f'SUCCESS: Заказ (id {orderForm.instance.id}) по проекту (id {pkOffer}) успешно создан')
                return redirect(order, orderObj.pk)
            else:
                errorsForm = orderForm.errors

    except Exception as err:
        print(msg, err)
        return HttpResponse(f'<h1 class="text-danger">{msg} {err}.</h1>')

    context.update({
        'style': {
            'bar': {'bg': 'bg-warning', 'text': 'text-black'},
        },
        'title': f'Создаётся заказ по проекту #{offerObj.number}',
        'titleBar': f'Заказ #{orderObj.number} - проект #{offerObj.number}',
        'orderForm': orderForm,
        'errorsForm': errorsForm,
        'order': orderForm.instance,
        'savedOK': savedOK,

    })
    return render(request, template, context)


@login_required
def order_edit(request, pk):
    """(view) Редактирование заказа."""
    msg = f'ERROR: ({order_edit.__name__}) Невозможно изменить заказ!'
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">{msg} Нет номера заказа!</h1>')

    template = 'app/order-form.html'
    context = get_ctx_common(request)
    errorsForm = None
    try:
        print(f'INFO: Попытка редактирования заказа (id {pk})')
        orderObj = Order.objects.filter(pk=pk).first()

        savedOK = False
        # форма заказа
        orderForm = OrderForm(request.POST or None, instance=orderObj)
        if request.method == 'POST':
            if orderForm.is_valid():
                orderForm.save()
                savedOK = True
                print(f'SUCCESS: Заказ (id {orderForm.instance.id}) '
                      f'по проекту (id {orderObj.offer.number}) успешно создан')
            else:
                errorsForm = orderForm.errors

        context.update({
            'orderForm': orderForm,
            'errorsForm': errorsForm,
            'order': orderForm.instance,
            'savedOK': savedOK,
            'title': 'Редактируется заказ',
            'titleBar': f'Заказ #{orderObj.number} - проект #{orderObj.offer.number}',
        })
        return render(request, template, context)

    except Exception as err:
        print(msg, err)
        return HttpResponse(f'<h1 class="text-danger">{msg} {err}</h1>')


@login_required
def order(request, pk):
    """(view) Страница просмотра заказа."""
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({order.__name__}) Нет номера заказа!</h1>')
    template = 'app/order.html'
    context = get_ctx_common(request)

    orderObj = Order.objects.filter(pk=pk).first()

    if not orderObj:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({order.__name__}) Проблема получения заказа из БД!</h1>')

    title = f'Заказ #{orderObj.number} - проект #{orderObj.offer.number}'

    context.update({
        'style': {
            'bar': {'bg': 'bg-warning', 'text': 'text-black'},
        },
        'title': title,
        'titleBar': title + ':',
        'order': orderObj,
        'scoreRange': SCORE_RANGE,
    })
    return render(request, template, context)


@login_required
def orders(request, username):
    """(view) Страница заказов пользователя."""
    template = 'app/index.html'
    context = get_ctx_common(request)

    user = User.objects.filter(username=username).first()

    # список заказов
    kwargs = {'client': user, 'isDeleted': False, 'isAccepted': False}      # в работе
    ordersQuery = get_query(Order, **kwargs).order_by('offer__cost')
    ordersCnt = ordersQuery.count()

    context.update({
        # общие параметры страницы
        'title': SITE_NAME,
        'style': {
            'widthRight': '100',  # %
        },

        'query': ordersQuery,
        'scoreRange': SCORE_RANGE,

        # действующие заказы
        'current': {
            'count': ordersCnt,
            'item_template': 'app/card-order.html',
            'titleBar': 'Действующих заказов нет!',
            'titleList': f'Мои заказы ({ordersCnt}):',
            'query': ordersQuery,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-warning', 'text': 'text-black'},
                'visibility': '',
                'elem_id': 'current',
            },
        },
    })
    return render(request, template, context)


@login_required
def order_success(request, pk, flag=1):
    """(view) Устанавливает/удаляет дату выполнения заказа. """
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({order_success.__name__}) Нет номера заказа!</h1>')

    orderObj = Order.objects.filter(pk=pk).first()
    if bool(int(flag)):
        orderObj.set_date_end_fact()
    else:
        orderObj.del_date_end_fact()
    orderObj.save()
    return redirect(offer, orderObj.offer.pk)


@login_required
def order_accept(request, pk):
    """(view) Принять готовый заказ."""
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({order_accept.__name__})  Не указан номер заказа!</h1>')
    orderObj = Order.objects.filter(pk=pk).first()
    orderObj.set_accept()
    orderObj.save()
    return redirect(order, pk)


@login_required
def order_score(request, pk, score):
    """(view) Оценка заказа."""
    if not pk:
        return HttpResponse(f'<h1 class="text-danger">ERROR: ({order_score.__name__}) Не указан номер заказа!</h1>')
    orderObj = Order.objects.filter(pk=pk).first()
    orderObj.set_score(score)
    orderObj.save()
    return redirect(order, pk)


@login_required
def cab_client(request):
    """(view) Кабинет клиента."""
    template = 'app/cabinet/cabinet.html'
    context = get_ctx_common(request)
    user = request.user

    # выборки заказов
    ordersQuery = Order.objects.filter(client=user)                         # все мои проекты

    ordersCompleted = ordersQuery.filter(isDeleted=False, isAccepted=True)  # выполненные
    completedCnt = ordersCompleted.count()

    ordersQuery = ordersQuery.filter(isDeleted=False, isAccepted=False)     # в работе
    currentCnt = ordersQuery.count()

    context.update({
        # общие параметры страницы
        'scoreRange': SCORE_RANGE,
        'title': f'Заказчик {user.username}',
        'titleBar': f'Кабинет заказчика "{user.username}":',
        'style': {
            'widthRight': '100',  # %
            'bar': {'bg': 'bg-warning', 'text': 'text-black'},
        },

        # действующие заказы
        'current': {
            'count': currentCnt,
            'item_template': 'app/card-order.html',
            'titleBar': 'Действующих заказов нет!',
            'titleList': f'Действующие заказы ({currentCnt}):',
            'query': ordersQuery,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-warning', 'text': 'text-black-50'},
                'visibility': '',
                'elem_id': 'current',
            },
        },

        # завершённые заказы
        'completed': {
            'count': completedCnt,
            'item_template': 'app/card-order.html',
            'titleList': f'Завершённые заказы ({completedCnt}):',
            'query': ordersCompleted,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-success', 'text': None},
                'visibility': 'visually-hidden',    # bootstrap: visually-hidden / visible
                'elem_id': 'completed',
            },
        },
    })
    return render(request, template, context)


@login_required
def cab_worker(request):
    """(view) Кабинет исполнителя."""
    template = 'app/cabinet/cabinet.html'
    context = get_ctx_common(request)
    user = request.user

    # выборки проектов
    offersQuery = Offer.objects.filter(user=user)                           # все проекты

    offersDeleted = offersQuery.filter(isDeleted=True)                      # удаленные
    deletedCnt = offersDeleted.count()

    offersQuery = offersQuery.filter(isDeleted=False)                       # все действующие (+ в работе)

    inworkQuery, inworkCnt = Offer.get_work(user)                           # в работе

    # offersQuery = offersQuery.difference(inworkQuery)                      # действующие не в работе
    currentCnt = offersQuery.count()

    context.update({
        # общие параметры страницы
        'title': f'Исполнитель {user.username}',
        'titleBar': f'Кабинет исполнителя "{user.username}":',
        'style': {
            'widthRight': '100',  # %
            'bar': {'bg': '', 'text': ''},
        },

        # проекты в работе
        # TODO: вывести в отдельный контекст секцию 'inwork'
        'inwork': {
            'count': inworkCnt,
            'item_template': 'app/card-offer.html',
            'titleList': f'Проекты в работе ({inworkCnt}):',
            'query': inworkQuery,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-primary', 'text': ''},
                'visibility': '',
                'elem_id': 'inwork',
            },
        },

        # действующие проекты не в работе
        # TODO: вывести в отдельный контекст секцию 'current'
        'current': {
            'count': currentCnt,
            'item_template': 'app/card-offer.html',
            'titleBar': 'Действующих проектов нет!',
            'titleList': f'Действующие проекты ({currentCnt}):',
            'query': offersQuery,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-info', 'text': 'text-dark'},
                'visibility': 'visually-hidden',
                'elem_id': 'current',
            },
        },

        # удалённые проекты
        'del': {
            'count': deletedCnt,
            'item_template': 'app/card-offer.html',
            'titleList': f'Удалённые проекты ({deletedCnt}):',
            'query': offersDeleted,
            'style': {
                'cols': 4,  # число колонок списка
                'bar': {'bg': 'bg-secondary', 'text': ''},
                'visibility': 'visually-hidden',    # bootstrap: visually-hidden / visible
                'elem_id': 'del',
            },
        },
    })
    return render(request, template, context)


@login_required
def password_reset(request):
    """(view) Сброс пароля."""
    template = 'login.html'
    context = get_ctx_common(request)

    pass
    return render(request, template, context)
