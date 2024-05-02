from tortoise import Model, fields


class User(Model):
    host = fields.CharField(pk=True, max_length=64)
    data = fields.JSONField(default={'attempts': 0, 'guesses': [], 'level': 0})
