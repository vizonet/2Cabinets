SITE_NAME = '2Cabinets'

SCORE_RANGE = range(1, 6)                                   # оценки заказа

OFFER_ITEMS = 'offers'
ORDER_ITEMS = 'orders'

RUB = '₽'                                                   # знак валюты

# Общий контекст сайта (статический)
CTX_STATIC = {
    'title': SITE_NAME,                                     # название страницы
    'titleBrand': SITE_NAME,                                # ссылка на главную страницу
    'titleFooter': SITE_NAME,                               # заголовок в футере
    'currency': RUB,                                        # обозначение местной валюты
}
