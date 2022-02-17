from django.db import models

from . import constants


class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField(default=constants.SYSTEM_USER)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(default=constants.SYSTEM_USER)
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'users'


class UserData(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='%(class)s_user_id')
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField()
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'user_data'

class Data(models.Model):
    id = models.AutoField(primary_key=True)
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name='%(class)s_user_data_id')
    data_user_id = models.IntegerField()
    data_id = models.IntegerField()
    data_title = models.TextField()
    data_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField()
    deleted_at = models.DateTimeField(null=True)
    deleted_by = models.IntegerField(null=True)

    class Meta:
        managed = True
        db_table = 'data'