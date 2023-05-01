from app.internal.context import AppContext
from app.internal.config import AppSettings

from fastapi import FastAPI


class Extra:
    settings: AppSettings
    context: AppContext


class App(FastAPI):
    extra: Extra  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra = Extra()
