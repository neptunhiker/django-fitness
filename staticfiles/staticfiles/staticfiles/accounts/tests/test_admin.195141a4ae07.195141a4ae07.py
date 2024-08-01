import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_admin_change_user(admin_client):
    user = User.objects.create_user(email='user@example.com', password='password123')
    url = reverse('admin:accounts_customuser_change', args=[user.id])
    response = admin_client.get(url)
    assert response.status_code == 200

    new_email = 'updated@example.com'
    response = admin_client.post(url, {
        'email': new_email,
        'is_active': True,
        'is_staff': False,
        'is_superuser': False
    })
    assert response.status_code == 302  # Redirect after successful update
    user.refresh_from_db()
    assert user.email == new_email
