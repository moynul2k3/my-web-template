from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Optional
from applications.items.models import Category
from app.utils.file_manager import save_file, update_file, delete_file
from app.auth import permission_required

router = APIRouter(prefix="/categories", tags=["Categories"])

# Pydantic models
Category_Pydantic = pydantic_model_creator(Category, name="Category")
CategoryIn_Pydantic = pydantic_model_creator(Category, name="CategoryIn", exclude_readonly=True)

# Create Category
@router.post("/", response_model=Category_Pydantic, dependencies=[Depends(permission_required("add_category"))])
async def create_category(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = None
):
    if Category.filter(name=name).exists():
        raise HTTPException(status_code=400, detail="Already exist.")

    avatar_path = None
    if avatar:
        avatar_path = await save_file(avatar, upload_to="category_avatars")

    category_obj = await Category.create(
        name=name,
        description=description,
        avatar=avatar_path
    )
    return await Category_Pydantic.from_tortoise_orm(category_obj)


# List all Categories
@router.get("/", response_model=List[Category_Pydantic])
async def list_categories():
    return await Category_Pydantic.from_queryset(Category.all())


# Get single Category by ID
@router.get("/{category_id}", response_model=Category_Pydantic)
async def get_category(category_id: int):
    category = await Category_Pydantic.from_queryset_single(Category.get(id=category_id))
    return category


# Update Category
@router.put("/{category_id}", response_model=Category_Pydantic, dependencies=[Depends(permission_required("update_category"))])
async def update_category(
    category_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = None
):
    category_obj = await Category.get_or_none(id=category_id)
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = {k: v for k, v in locals().items() if k not in ["category_id", "avatar"] and v is not None}

    if avatar:
        avatar_path = await update_file(avatar, category_obj.avatar, upload_to="category_avatars")
        update_data["avatar"] = avatar_path

    await Category.filter(id=category_id).update(**update_data)
    return await Category_Pydantic.from_queryset_single(Category.get(id=category_id))


# Delete Category
@router.delete("/{category_id}", response_model=dict, dependencies=[Depends(permission_required("delete_category"))])
async def delete_category(category_id: int):
    category_obj = await Category.get_or_none(id=category_id)
    if not category_obj:
        raise HTTPException(status_code=404, detail="Category not found")

    if category_obj.avatar:
        await delete_file(category_obj.avatar)

    await Category.filter(id=category_id).delete()
    return {"detail": "Category deleted successfully"}
