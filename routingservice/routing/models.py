from django.db import models

import uuid

# Create your models here.
class Route(models.Model):
    route_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_route_id(self):
        return self.route_id
    
    def get_numerical_id(self):
        return self.id
    