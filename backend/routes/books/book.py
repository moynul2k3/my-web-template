from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Optional
from datetime import datetime, timezone
from applications.books.models import Book
from applications.items.models import Category, SubCategory
from app.utils.file_manager import save_file, update_file, delete_file
from app.auth import permission_required

router = APIRouter(prefix="/books", tags=["Books"])

# Pydantic models
Book_Pydantic = pydantic_model_creator(Book, name="Book")
BookIn_Pydantic = pydantic_model_creator(Book, name="BookIn", exclude_readonly=True)

# Helper to include computed properties
async def book_with_properties(book_obj: Book):
    data = await Book_Pydantic.from_tortoise_orm(book_obj)
    data_dict = data.dict()
    data_dict.update({
        "tags_list": book_obj.tags_list,
        "is_in_stock": book_obj.is_in_stock,
        "new_arrival": book_obj.new_arrival,
        "todays_deals": book_obj.todays_deals,
        "discounted_price": book_obj.discounted_price,
        "sell_price": book_obj.sell_price
    })
    return data_dict

# Create Book
@router.post("/", response_model=dict, dependencies=[Depends(permission_required("add_book"))])
async def create_book(
    title: str = Form(...),
    slug: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(0.0),
    discount: float = Form(0.0),
    box_price: float = Form(0.0),
    stock: int = Form(0),
    popular: bool = Form(False),
    free_delivery: bool = Form(False),
    hot_deals: bool = Form(False),
    flash_sale: bool = Form(False),
    tag: Optional[str] = Form("academic_books"),
    book_type: str = Form("academic_book"),
    category_id: int = Form(...),
    subcategory_id: Optional[int] = Form(None),
    author: str = Form(...),
    publisher: Optional[str] = Form(None),
    isbn: Optional[str] = Form(None),
    edition: Optional[str] = Form(None),
    total_pages: Optional[int] = Form(None),
    language: Optional[str] = Form(None),
    publication_date: Optional[datetime] = Form(None),
    file_sample: Optional[UploadFile] = None,
    file_full: Optional[UploadFile] = None,
    image: Optional[UploadFile] = None
):
    category_obj = await Category.get_or_none(id=category_id)
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category not found")

    subcategory_obj = None
    if subcategory_id:
        subcategory_obj = await SubCategory.get_or_none(id=subcategory_id)
        if not subcategory_obj:
            raise HTTPException(status_code=404, detail="SubCategory not found")

    file_sample_path = await save_file(file_sample, "book_files") if file_sample else None
    file_full_path = await save_file(file_full, "book_files") if file_full else None
    image_path = await save_file(image, "book_images") if image else None

    book_obj = await Book.create(
        title=title,
        slug=slug,
        description=description,
        price=price,
        discount=discount,
        box_price=box_price,
        stock=stock,
        popular=popular,
        free_delivery=free_delivery,
        hot_deals=hot_deals,
        flash_sale=flash_sale,
        tag=tag,
        book_type=book_type,
        category=category_obj,
        subcategory=subcategory_obj,
        author=author,
        publisher=publisher,
        isbn=isbn,
        edition=edition,
        total_pages=total_pages,
        language=language,
        publication_date=publication_date,
        file_sample=file_sample_path,
        file_full=file_full_path,
        image=image_path
    )
    return await book_with_properties(book_obj)

# List all Books
@router.get("/", response_model=List[dict])
async def list_books():
    books = await Book.all().prefetch_related("category", "subcategory")
    return [await book_with_properties(b) for b in books]

# Get single Book by ID
@router.get("/{book_id}", response_model=dict)
async def get_book(book_id: int):
    book_obj = await Book.get_or_none(id=book_id).prefetch_related("category", "subcategory")
    if not book_obj:
        raise HTTPException(status_code=404, detail="Book not found")
    return await book_with_properties(book_obj)

# Update Book
@router.put("/{book_id}", response_model=dict, dependencies=[Depends(permission_required("update_book"))])
async def update_book(
    book_id: int,
    title: Optional[str] = Form(None),
    slug: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    discount: Optional[float] = Form(None),
    box_price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    popular: Optional[bool] = Form(None),
    free_delivery: Optional[bool] = Form(None),
    hot_deals: Optional[bool] = Form(None),
    flash_sale: Optional[bool] = Form(None),
    tag: Optional[str] = Form(None),
    book_type: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    subcategory_id: Optional[int] = Form(None),
    author: Optional[str] = Form(None),
    publisher: Optional[str] = Form(None),
    isbn: Optional[str] = Form(None),
    edition: Optional[str] = Form(None),
    total_pages: Optional[int] = Form(None),
    language: Optional[str] = Form(None),
    publication_date: Optional[datetime] = Form(None),
    file_sample: Optional[UploadFile] = None,
    file_full: Optional[UploadFile] = None,
    image: Optional[UploadFile] = None
):
    book_obj = await Book.get_or_none(id=book_id)
    if not book_obj:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = {k: v for k, v in locals().items() if k not in ["book_id", "file_sample", "file_full", "image"] and v is not None}

    # Handle category and subcategory
    if "category_id" in update_data:
        category_obj = await Category.get_or_none(id=update_data["category_id"])
        if not category_obj:
            raise HTTPException(status_code=404, detail="Category not found")
        update_data["category"] = category_obj
        update_data.pop("category_id")

    if "subcategory_id" in update_data:
        if update_data["subcategory_id"] is None:
            update_data["subcategory"] = None
        else:
            subcategory_obj = await SubCategory.get_or_none(id=update_data["subcategory_id"])
            if not subcategory_obj:
                raise HTTPException(status_code=404, detail="SubCategory not found")
            update_data["subcategory"] = subcategory_obj
        update_data.pop("subcategory_id")

    # Handle files
    if file_sample:
        update_data["file_sample"] = await update_file(file_sample, book_obj.file_sample, upload_to="book_files")
    if file_full:
        update_data["file_full"] = await update_file(file_full, book_obj.file_full, upload_to="book_files")
    if image:
        update_data["image"] = await update_file(image, book_obj.image, upload_to="book_images")

    await Book.filter(id=book_id).update(**update_data)
    book_obj = await Book.get(id=book_id)
    return await book_with_properties(book_obj)

# Delete Book
@router.delete("/{book_id}", response_model=dict, dependencies=[Depends(permission_required("delete_book"))])
async def delete_book(book_id: int):
    book_obj = await Book.get_or_none(id=book_id)
    if not book_obj:
        raise HTTPException(status_code=404, detail="Book not found")

    # Delete files
    if book_obj.file_sample:
        await delete_file(book_obj.file_sample)
    if book_obj.file_full:
        await delete_file(book_obj.file_full)
    if book_obj.image:
        await delete_file(book_obj.image)

    await Book.filter(id=book_id).delete()
    return {"detail": "Book deleted successfully"}




# {
#   "id": 1,
#   "title": "Introduction to Python",
#   "slug": "introduction-to-python",
#   "description": "A comprehensive guide to Python programming.",
#   "price": 50.0,
#   "discount": 10.0,
#   "box_price": 55.0,
#   "stock": 20,
#   "popular": true,
#   "free_delivery": true,
#   "hot_deals": false,
#   "flash_sale": false,
#   "tag": "academic_books,programming,python",
#   "book_type": "academic_book",
#   "category_id": 2,
#   "subcategory_id": 5,
#   "author": "John Doe",
#   "publisher": "Tech Press",
#   "isbn": "9781234567890",
#   "edition": "3rd",
#   "total_pages": 350,
#   "language": "English",
#   "publication_date": "2025-01-15T00:00:00Z",
#   "file_sample": "uploads/book_files/python_sample.pdf",
#   "file_full": "uploads/book_files/python_full.pdf",
#   "image": "uploads/book_images/python_cover.jpg",
#   "created_at": "2025-10-19T22:30:00Z",
#   "updated_at": "2025-10-19T22:35:00Z",

#   // Computed properties
#   "tags_list": ["academic_books", "programming", "python"],
#   "is_in_stock": true,
#   "new_arrival": true,
#   "todays_deals": false,
#   "discounted_price": 5.0,
#   "sell_price": 45.0
# }
