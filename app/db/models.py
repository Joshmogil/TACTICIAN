from tortoise.models import Model
from tortoise import fields

from app import user
from app.workout import WorkoutWeek




class User(Model):
    id = fields.UUIDField(pk=True)
    email = fields.CharField(max_length=200, unique=True)
    info = fields.JSONField(field_type=user.User)


class WorkoutChunk(Model):
    id = fields.UUIDField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    # add a timestamp here for when it was created
    # add a timestamp here for when it was done
    workouts = fields.JSONField(field_type=WorkoutWeek)
    user = fields.ForeignKeyField('models.User', related_name='workout_chunks')

    def __str__(self):
        return f"WorkoutChunk for user {self.user_id}"