from django.test import TestCase
from .models import City


class createCityTestCase(TestCase):
    def setUp(self):
        City.objects.create(country='FR', city='Paris', location_id='FRXX0076', id=1)

    def test_create_city(self):
        paris = City.objects.get(city='Paris')
        self.assertEqual(paris.cache_key('item'), 'item_FR_1')
