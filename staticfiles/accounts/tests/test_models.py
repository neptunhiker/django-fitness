import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    email = 'user@example.com'
    password = 'password123'
    user = User.objects.create_user(email=email, password=password)
    assert user.email == email
    assert user.check_password(password)
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser():
    email = 'admin@example.com'
    password = 'password123'
    user = User.objects.create_superuser(email=email, password=password)
    assert user.email == email
    assert user.check_password(password)
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser

@pytest.mark.django_db
def test_create_user_without_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email=None, password='password123')
