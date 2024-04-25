from django.contrib import admin
from django.core.paginator import Paginator

from app.models import Category, City, Offer, Order, Portfolio, Profile


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    paginator = Paginator


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    paginator = Paginator


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'user', 'cost', 'category', 'short_desc', 'image', 'created', 'updated', 'slug')
    list_display_links = ('user',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-cost',)
    search_fields = ['title', 'user', 'category']
    readonly_fields = ('created', 'updated')
    list_per_page = 20
    paginator = Paginator


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'offer', 'dateStart', 'dateEndPlan', 'dateEndFact', 'isAccepted', 'dateAccept',
                    'score', 'isDeleted')
    list_display_links = ('client', 'offer')
    ordering = ('-score',)
    search_fields = ['client', 'offer']
    readonly_fields = ('score',)
    list_per_page = 20
    paginator = Paginator


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'dateRelease', 'short_url', 'short_desc')
    list_display_links = ('user', 'name', 'short_desc')
    ordering = ('dateRelease', 'name')
    search_fields = ['dateRelease', 'name', 'user', 'short_desc']
    # readonly_fields = ('', )
    list_per_page = 20
    paginator = Paginator


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'phoneNumber', 'experience')
    list_display_links = ('user',)
    ordering = ('-rate',)
    search_fields = ['city', 'phoneNumber']
    readonly_fields = ('rate', 'get_specializations')
    list_per_page = 20
    paginator = Paginator
