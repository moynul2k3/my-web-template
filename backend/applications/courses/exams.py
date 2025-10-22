from tortoise import models, fields
from applications.courses.courses import TopicBase

class ExamTopic(TopicBase):
    module = fields.ForeignKeyField('courses.Module', on_delete=fields.CASCADE, related_name='course_exam')
    will_start = fields.DatetimeField(blank=True, null=True)
    duration = fields.TimeField(blank=True, null=True)