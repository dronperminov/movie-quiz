import urllib.parse
from typing import Optional

from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from src.entities.user import User
from src.utils.common import get_static_hash

templates = Environment(loader=FileSystemLoader("web/templates"), cache_size=0)
templates.policies["json.dumps_kwargs"]["ensure_ascii"] = False


def send_error(title: str, text: str, user: Optional[User]) -> HTMLResponse:
    template = templates.get_template("components/error.html")
    content = template.render(user=user, page="error", version=get_static_hash(), error_title=title, error_text=text)
    return HTMLResponse(content=content)


def login_redirect(back_url: str) -> RedirectResponse:
    return RedirectResponse(url=f'/login?back_url={urllib.parse.quote(back_url, safe="")}')
