from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, employee_id, password=None, role=None):
        if not employee_id:
            raise ValueError('Users must have an employee ID')
        user = self.model(employee_id=employee_id, role=role)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, password=None, role=None):
        user = self.create_user(employee_id, password=password, role=role)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    employee_id = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = []

class Machine(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    acceleration = models.FloatField()
    velocity = models.FloatField()

    def __str__(self):
        return self.name

class DynamicData(models.Model):
    id = models.AutoField(primary_key=True)
    machine_id = models.ForeignKey(Machine, related_name='dynamic_data', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    actual_position = models.JSONField(default=dict)  # JSONField to store actual positions
    distance_to_go = models.JSONField(default=dict)   # JSONField to store distance to go
    homed = models.JSONField(default=dict)            # JSONField to store homed status
    tool_offset = models.JSONField(default=dict)      # JSONField to store tool offsets
    
    created_by = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data for {self.machine_id.name} by {self.created_by}"
