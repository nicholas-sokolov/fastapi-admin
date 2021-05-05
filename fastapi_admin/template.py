import os
import typing
from datetime import date
from typing import Any, List, Tuple
from urllib.parse import urlencode

from jinja2 import contextfilter
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from fastapi_admin import VERSION
from fastapi_admin.constants import BASE_DIR

if typing.TYPE_CHECKING:
    from fastapi_admin.resources import Field

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals["VERSION"] = VERSION
templates.env.globals["NOW_YEAR"] = date.today().year
templates.env.add_extension("jinja2.ext.i18n")
templates.env.add_extension("jinja2.ext.autoescape")
templates.env.add_extension("jinja2.ext.with_")
templates.env.add_extension("jinja2.ext.do")


@contextfilter
def current_page_with_params(context: dict, params: dict):
    request = context.get("request")  # type:Request
    full_path = request.scope["raw_path"].decode()
    query_params = dict(request.query_params)
    for k, v in params.items():
        query_params[k] = v
    return full_path + "?" + urlencode(query_params)


templates.env.filters["current_page_with_params"] = current_page_with_params


def set_global_env(name: str, value: Any):
    templates.env.globals[name] = value


def add_template_folder(*folders: str):
    for folder in folders:
        templates.env.loader.searchpath.insert(0, folder)


async def render_values(
    fields: List["Field"], values: List[Tuple[Any]], display: bool = True
) -> List[List[Any]]:
    """
    render values with template render
    :param fields:
    :param values:
    :param display:
    :return:
    """
    ret = []
    for value in values:
        item = []
        for i, k in enumerate(value):
            if display:
                item.append(await fields[i].display.render(value[k]))
            else:
                item.append(await fields[i].input.render(value[k]))
        ret.append(item)
    return ret
