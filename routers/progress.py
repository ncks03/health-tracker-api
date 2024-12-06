from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, APIRouter, HTTPException
from models.entities import Progress
from schemas.responses import ProgressResponse
from services.functions import get_db

router = APIRouter(
    prefix="/progress",
    tags=["progress"]
)

@router.get("/")
async def get_progress(db = Depends(get_db)):
    try:
        progresses = db.query(Progress).all()
        if not progresses:
            raise HTTPException(status_code=404, detail="no progresses found")

        return [
            ProgressResponse(
                customer_id=progress.customer_id,
                date=progress.date,
                weight=progress.weight
            )for progress in progresses
        ]

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(status_code=500, detail=f"unexpected error!")

@router.get("/{progress_id}")
async def get_progress_by_id(progress_id: int, db = Depends(get_db)):
    try:
        progress = db.query(Progress).filter(Progress.id == progress_id).first()
        if not progress:
            raise HTTPException(status_code=404, detail=f"No progress found with id {progress_id}")

        return ProgressResponse(
            customer_id=progress.customer_id,
            date=progress.date,
            weight=progress.weight
        )

    except HTTPException as e:
        raise e

    except Exception:
        raise HTTPException(status_code=500, detail=f"unexpected error!")