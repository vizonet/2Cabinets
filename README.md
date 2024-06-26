# Сайт "2Cabinets"

## Тестовый проект оказания услуг между пользователями по различным категориям

Пользователи сайта могут быть как исполнителями, так и заказчиками услуг других пользователей.

Проект разработан с применением фреймворка Django v5 (backend - python) и стека web-технологий + Bootstrap v5.

Сайт имеет стандартно настроенную admin-панель Django с отображением и редактированием заданных моделей данных.

### Текущая реализация проекта предоставляет следующие пользовательские сценарии:
+ авторизация пользователей,
+ без авторизации - только просмотр страниц сайта,
+ для авторизованных пользователей доступно:
    - создание пользователя администратором сайта через админ-панель,
    - просмотр доступных проектов услуг, в том числе с ранжированием по их авторам с возможностью заказать выбранные,
    - создание/редактирование/просмотр профиля пользователя, проекта услуги в выбранной категории,
    - создание заказа на основе выбранного проекта действующей услуги,
    - просмотр своих проектов и заказов, ранжированных по статусам, на соответствующих страницах личного кабинета,
    - удаление/восстановление проектов услуг,
    - автоматическое изменение статуса заказа при его создании, отметки о готовности и принятия работы заказчиком,
    - отображение инструментов управления проектом услуги и заказом в соответствии с их статусами 
      и согласно принадлежности пользователю.

_________

Проект содержит fixtures - файлы в формате json для наполнения базы данных:
two_cabinets/app/fixtures
