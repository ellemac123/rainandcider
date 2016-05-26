# from celery import Celery, task
#
# from .views import *
#
# app = Celery('tasks')
#
# #app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost')
#
# @app.task(run_every=10, name="update_cache")
# def update_cache():
#     """
#     This will update the cache so that the user
#     'never' has to wait for content to load
#     """
#     print("Called the cache")
#     for city in City.objects.all():
#         update_city(city.country, city.pk)
#         print("updated the cache of : " + str(city.pk))
