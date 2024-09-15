from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.api import templates
from src.entities.user import User
from src.utils.auth import get_user
from src.utils.common import get_static_hash

router = APIRouter()


@router.get("/")
def index(user: Optional[User] = Depends(get_user)) -> HTMLResponse:
    template = templates.get_template("index.html")
    content = template.render(
        user=user,
        version=get_static_hash()
    )

    return HTMLResponse(content=content)
