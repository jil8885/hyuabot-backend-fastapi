import datetime

from pydantic import BaseModel, Field

from app.response.campus import Campus


class Menu(BaseModel):
    date: datetime.date = Field(..., alias="date")
    slot: str = Field(..., alias="slot")
    food: str = Field(..., alias="food")
    price: str = Field(..., alias="price")


class RestaurantLocation(BaseModel):
    latitude: float = Field(..., alias="latitude")
    longitude: float = Field(..., alias="longitude")


class Restaurant(BaseModel):
    id: int = Field(..., alias="id")
    location: RestaurantLocation = Field(..., alias="location")
    menu: list[Menu] = Field(..., alias="menu")


class RestaurantList(Campus):
    restaurants: list[Restaurant] = Field(..., alias="restaurants")
