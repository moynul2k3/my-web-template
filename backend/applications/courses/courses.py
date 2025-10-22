from tortoise import models, fields
from applications.items.models import ItemBase

class Course(ItemBase):
    category = fields.ForeignKeyField("items.Category", related_name="course")
    subcategory = fields.ForeignKeyField("items.SubCategory", related_name="course", null=True)
    instructor = fields.ForeignKeyField("user.User", related_name='instructor', blank=True, null=True)
    level = fields.CharField(max_length=50, null=True, description="Beginner / Intermediate / Advanced")
    video_id = fields.CharField(max_length=100, null=True)
    banner = fields.CharField(max_length=200, null=True)
    certificate_available = fields.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} by {self.vendor.username}"
    
class Module(models.Model):
    course = fields.ForeignKeyField('courses.Course', on_delete=fields.CASCADE, related_name='course_module')
    name = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} of {self.course.title}"

class TopicBase(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    description = fields.TextField(blank=True, null=True)
    material = fields.CharField(max_length=200, blank=True, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)


