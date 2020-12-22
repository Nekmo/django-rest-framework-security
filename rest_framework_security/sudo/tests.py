from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class UserIpTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('sudo-status')
        self.user = get_user_model().objects.create(
            username='demo',
        )

    def test_is_expired(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.json().get('remaning_time'), '0.0')
        self.assertEqual(response.json().get('is_expired'), True)

    def test_not_expired(self):
        self.client.force_authenticate(user=self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.json().get('is_expired'), False)
