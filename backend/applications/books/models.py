from tortoise import models, fields
from applications.items.models import ItemBase


BOOKS_TYPE = [
    ('academic_book', 'Academic Book'),
    ('ebook', 'E-Book'),
    ('magazine', 'Magazine'),
]

class BrandVid(models.Model):
    vieo_for = fields.CharField(max_length=50, choices=BOOKS_TYPE, default='academic_book')
    VIDEO_TYPE_CHOICES = ["youtube", "cloudinary", "basic"]
    
    type = fields.CharField(
        max_length=20,
        choices=VIDEO_TYPE_CHOICES,
        default="youtube",
        description="Select the type of video source"
    )
    video_id = fields.CharField(max_length=400, description="YouTube video ID or Cloudinary video ID")
    title = fields.TextField(max_length=200, null=True, description="Title of the video")
    description = fields.TextField(max_length=1500, null=True, description="Description of the video")
    autoplay = fields.CharField(
        max_length=20,
        default="false",
        description="Autoplay mode: false, true, on-scroll"
    )
    muted = fields.BooleanField(default=True)
    controls = fields.BooleanField(default=True)
    loop = fields.BooleanField(default=False)
    playlist = fields.BooleanField(default=False)
    endScreen = fields.BooleanField(default=True)
    pip = fields.BooleanField(default=False, description="Picture in Picture Mode")
    poster = fields.CharField(max_length=200, null=True, default=None, description="Poster image path")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "books_brand_vid"
        ordering = ["-created_at"]

    def __str__(self):
        return f"({self.type}) - {self.video_id}"

    async def save(self, *args, **kwargs):
        if not self.pk:
            count = await BrandVid.all().count()
            if count > 0:
                raise ValueError("Only one BrandVid instance is allowed.")
        await super().save(*args, **kwargs)



class Book(ItemBase):
    category = fields.ForeignKeyField(
        "items.Category", related_name="books", on_delete=fields.CASCADE
    )
    subcategory = fields.ForeignKeyField(
        "items.SubCategory", related_name="books", on_delete=fields.SET_NULL, null=True
    )
    book_type = fields.CharField(max_length=50, choices=BOOKS_TYPE, default='academic_book')
    author = fields.CharField(max_length=255)
    publisher = fields.CharField(max_length=255, null=True)
    isbn = fields.CharField(max_length=13, unique=True, null=True)
    edition = fields.CharField(max_length=50, null=True)
    total_pages = fields.IntField(null=True)
    language = fields.CharField(max_length=50, null=True)
    publication_date = fields.DatetimeField(null=True)
    file_sample = fields.CharField(max_length=200, null=True) 
    file_full = fields.CharField(max_length=200, null=True)
    image = fields.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"



