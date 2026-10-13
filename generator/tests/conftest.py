import pytest
from django.core.management import call_command


@pytest.fixture
def seed(db):
    call_command("seed_demo", verbosity=0)


@pytest.fixture
def seed_generado(db):
    call_command("seed_demo", "--generar", verbosity=0)


@pytest.fixture
def cliente(client, django_user_model):
    user = django_user_model.objects.create_user("prueba", password="contraseña-segura-123")
    client.force_login(user)
    return client
