from tortoise import models, fields
from applications.items.models import ItemBase


class BrandVid(models.Model):
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
        table = "products_brand_vid"
        ordering = ["-created_at"]

    def __str__(self):
        return f"({self.type}) - {self.video_id}"

    async def save(self, *args, **kwargs):
        if not self.pk:
            count = await BrandVid.all().count()
            if count > 0:
                raise ValueError("Only one BrandVid instance is allowed.")
        await super().save(*args, **kwargs)

    

class Product(ItemBase):
    category = fields.ForeignKeyField("items.Category", related_name="products")
    subcategory = fields.ForeignKeyField("items.SubCategory", related_name="products", null=True)
    brand = fields.CharField(max_length=100, null=True)
    weight = fields.FloatField(null=True)
    sku = fields.CharField(max_length=100, null=True)
    warranty = fields.CharField(max_length=100, null=True)
    tags = fields.JSONField(null=True) 
    vendor = fields.ForeignKeyField("user.User", related_name='Vendor', blank=True, null=True)

    class Meta:
        table = "products"

    def __str__(self):
        return f"{self.title} by {self.vendor.username}"


COLOR_CHOICES = [
    ("#000000", "Black"),
    ("#FFFFFF", "White"),
    ("#FF0000", "Red"),
    ("#00FF00", "Lime"),
    ("#0000FF", "Blue"),
    ("#FFFF00", "Yellow"),
    ("#FFA500", "Orange"),
    ("#800080", "Purple"),
    ("#FFC0CB", "Pink"),
    ("#A52A2A", "Brown"),
    ("#808080", "Gray"),
    ("#00FFFF", "Cyan"),
    ("#008080", "Teal"),
    ("#000080", "Navy"),
    ("#FFD700", "Gold"),
    ("#808000", "Olive"),
    ("#F0E68C", "Khaki"),
    ("#4B0082", "Indigo"),
    ("#E6E6FA", "Lavender"),
    ("#D3D3D3", "Light Gray"),
]

SIZE_CHOICES = [
    ("XS", "Extra Small"),
    ("S", "Small"),
    ("M", "Medium"),
    ("L", "Large"),
    ("XL", "Extra Large"),
    ("XXL", "2X Large"),
    ("3XL", "3X Large"),
    
]


class ProductImage(models.Model):
    pk = fields.IntField(pk=True)
    product = fields.ForeignKeyField("products.Product", related_name="product_image", on_delete=fields.CASCADE)
    image = fields.CharField(max_length=200, null=True)
    color = fields.CharField(max_length=7, choices=COLOR_CHOICES, blank=True, null=True)
    size = fields.CharField(max_length=7, choices=SIZE_CHOICES, blank=True, null=True)
    material = fields.CharField(max_length=100, null=True)
    created_at = fields.DatetimeField(auto_now_add=True, description="Timestamp when created")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title}: color: {self.color} > size: {self.size}"

