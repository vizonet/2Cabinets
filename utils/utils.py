from two_cabinets.settings import SHORT_STR


def ctx_add(*args):
    """ Возвращает словарь контекста страниц сайта из списка входящих словарей. """
    context = {}
    for ctx in args:
        if isinstance(ctx, dict):
            context.update(ctx)
        else:
            continue
    return context


def short_str(txt, strMax=SHORT_STR, suffix='...'):
    """ Возвращает короткое представление поля 'description'. """
    if len(txt) > strMax:
        return txt[:strMax] + suffix
    else:
        return txt


def get_query(model, pks=None, **kwargs):
    """ Возвращает объект QuerySet по данным запроса. """
    try:
        if pks:
            query = model.objects.filter(pk__in=pks)
        else:
            query = model.objects.filter(**kwargs)
    except Exception as ex:
        raise ex
    return query
