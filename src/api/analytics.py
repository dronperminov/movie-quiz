from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from src import database, questions_database, quiz_tours_database
from src.api import login_redirect, templates
from src.entities.user import User
from src.utils.auth import get_user
from src.utils.common import format_time, get_static_hash
from src.utils.date_utils import parse_dates

router = APIRouter()


@router.get("/analytics")
def get_analytics(username: str = Query(""), period: str = Query(""), user: Optional[User] = Depends(get_user)) -> Response:
    if not user:
        return login_redirect(back_url=f"/analytics?username={username}&period={period}")

    show_user = database.get_user(username=username)
    if username and (username.lower() == user.username.lower() or not show_user):
        return RedirectResponse(url=f"/analytics?period={period}")

    if not show_user:
        show_user = user

    period = parse_dates(period)
    analytics = questions_database.get_analytics(username=show_user.username, period=period)
    rating = quiz_tours_database.get_rating(username=show_user.username, query={})

    template = templates.get_template("user/analytics.html")
    content = template.render(
        user=user,
        version=get_static_hash(),
        analytics=analytics,
        rating=rating[0] if rating else 0,
        show_user=show_user,
        period=period,
        format_time=format_time
    )
    return HTMLResponse(content=content)
