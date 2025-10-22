from fastapi import APIRouter, HTTPException, UploadFile, Form, Depends
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Optional
from applications.books.models import BrandVid
from app.utils.file_manager import save_file, update_file, delete_file
from app.auth import permission_required

router = APIRouter(prefix="/brand_vids", tags=["Brand Videos"])

# Pydantic models
BrandVid_Pydantic = pydantic_model_creator(BrandVid, name="BrandVid")
BrandVidIn_Pydantic = pydantic_model_creator(BrandVid, name="BrandVidIn", exclude_readonly=True)

# Create BrandVid
@router.post("/", response_model=BrandVid_Pydantic, dependencies=[Depends(permission_required("add_brandvid"))])
async def create_brand_vid(
    type: str = Form(...),
    video_id: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    autoplay: str = Form("false"),
    muted: bool = Form(True),
    controls: bool = Form(True),
    loop: bool = Form(False),
    playlist: bool = Form(False),
    endScreen: bool = Form(True),
    pip: bool = Form(False),
    poster: Optional[UploadFile] = None
):
    count = await BrandVid.all().count()
    if count > 0:
        raise HTTPException(status_code=400, detail="Only one BrandVid instance is allowed.")

    poster_path = None
    if poster:
        poster_path = await save_file(poster, upload_to="books_brand_vid_posters")

    brand_vid_obj = await BrandVid.create(
        type=type,
        video_id=video_id,
        title=title,
        description=description,
        autoplay=autoplay,
        muted=muted,
        controls=controls,
        loop=loop,
        playlist=playlist,
        endScreen=endScreen,
        pip=pip,
        poster=poster_path
    )
    return await BrandVid_Pydantic.from_tortoise_orm(brand_vid_obj)


# List all BrandVids
@router.get("/", response_model=List[BrandVid_Pydantic])
async def list_brand_vids():
    return await BrandVid_Pydantic.from_queryset(BrandVid.all())


# Get single BrandVid by ID
@router.get("/{vid_id}", response_model=BrandVid_Pydantic)
async def get_brand_vid(vid_id: int):
    brand_vid = await BrandVid_Pydantic.from_queryset_single(BrandVid.get(id=vid_id))
    return brand_vid


# Update BrandVid
@router.put("/{vid_id}", response_model=BrandVid_Pydantic, dependencies=[Depends(permission_required("update_brandvid"))])
async def update_brand_vid(
    vid_id: int,
    type: Optional[str] = Form(None),
    video_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    autoplay: Optional[str] = Form(None),
    muted: Optional[bool] = Form(None),
    controls: Optional[bool] = Form(None),
    loop: Optional[bool] = Form(None),
    playlist: Optional[bool] = Form(None),
    endScreen: Optional[bool] = Form(None),
    pip: Optional[bool] = Form(None),
    poster: Optional[UploadFile] = None
):
    brand_vid_obj = await BrandVid.get_or_none(id=vid_id)
    if not brand_vid_obj:
        raise HTTPException(status_code=404, detail="BrandVid not found")

    update_data = {k: v for k, v in locals().items() if k not in ["vid_id", "poster"] and v is not None}

    if poster:
        poster_path = await update_file(poster, brand_vid_obj.poster, upload_to="books_brand_vid_posters")
        update_data["poster"] = poster_path

    await BrandVid.filter(id=vid_id).update(**update_data)
    return await BrandVid_Pydantic.from_queryset_single(BrandVid.get(id=vid_id))


# Delete BrandVid
@router.delete("/{vid_id}", response_model=dict, dependencies=[Depends(permission_required("delete_brandvid"))])
async def delete_brand_vid(vid_id: int):
    brand_vid_obj = await BrandVid.get_or_none(id=vid_id)
    if not brand_vid_obj:
        raise HTTPException(status_code=404, detail="BrandVid not found")

    if brand_vid_obj.poster:
        await delete_file(brand_vid_obj.poster)

    deleted_count = await BrandVid.filter(id=vid_id).delete()
    return {"detail": "BrandVid deleted successfully"}
