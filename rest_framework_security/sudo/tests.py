from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


class StatusViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('sudo-status')
        self.user = get_user_model().objects.create(
            username='demo',
        )

    def test_is_expired(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('remaning_time'), '0.0')
        self.assertEqual(response.json().get('is_expired'), True)

    def test_not_expired(self):
        self.client.force_authenticate(user=self.user)
        self.user.last_login = timezone.now()
        self.user.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('is_expired'), False)


class UpdateStatusTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('sudo-update_status')
        self.password = 'demo1234'
        self.user = get_user_model().objects.create(
            username='demo',
        )
        self.user.set_password(self.password)
        self.user.save()

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        self.assertIsNone(self.user.last_login)
        response = self.client.post(self.url, {'password': self.password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.user.last_login)


class ExpireNowViewTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('sudo-expire_now')
        self.dt = timezone.now()
        self.user = get_user_model().objects.create(
            username='demo', last_login=self.dt,
        )

    def test_update(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertLess(get_user_model().objects.get(pk=self.user.pk).last_login, self.dt)
