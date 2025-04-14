import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker
from fitness_app.models import *

fake = Faker()
User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    name = fake.name()
    username = factory.Sequence(lambda n: f'user{n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')

class WorkoutPlanFactory(DjangoModelFactory):
    class Meta:
        model = WorkoutPlan
    
    user = factory.SubFactory(UserFactory)
    name = fake.word()
    difficulty = 'beginner'

# Create similar factories for all models