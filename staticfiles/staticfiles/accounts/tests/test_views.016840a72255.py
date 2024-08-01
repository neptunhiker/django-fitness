import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_login_user(client):
    email = 'user@example.com'
    password = 'password123'
    user = User.objects.create_user(email=email, password=password)
    response = client.post(reverse('login'), {'username': email, 'password': password})
    assert response.status_code == 302  # Redirect to home page or next page

@pytest.mark.django_db
def test_login_user_invalid_credentials(client):
    email = 'user@example.com'
    password = 'password123'
    user = User.objects.create_user(email=email, password=password)
    response = client.post(reverse('login'), {'username': email, 'password': 'wrongpassword'})
    assert response.status_code == 200  # Page reloads with error message


