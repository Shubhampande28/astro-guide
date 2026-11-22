"""Pydantic request/response models for the /chart endpoint."""

from datetime import date, datetime, time

from pydantic import BaseModel, Field

from app.astro.chart import Chart


class ChartRequest(BaseModel):
    birth_date: date
    birth_time: time = Field(description="Local civil time of birth, 24h format")
    timezone: str = Field(description="IANA timezone name, e.g. Asia/Kolkata")
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180, description="East positive")
    as_of: datetime | None = Field(
        default=None, description="Which moment's dasha to report as current; defaults to now"
    )


class GrahaSchema(BaseModel):
    graha: str
    sidereal_longitude_deg: float
    sign: str
    degree_in_sign: float
    nakshatra: str
    pada: int
    house: int
    dignity: str
    retrograde: bool
    navamsa_sign: str


class LagnaSchema(BaseModel):
    sidereal_longitude_deg: float
    sign: str
    degree_in_sign: float
    nakshatra: str
    pada: int


class AntarDashaSchema(BaseModel):
    lord: str
    start: datetime
    end: datetime


class MahaDashaSchema(BaseModel):
    lord: str
    start: datetime
    end: datetime
    antar_dashas: list[AntarDashaSchema]


class ChartResponse(BaseModel):
    birth_utc: datetime
    ayanamsa_deg: float
    lagna: LagnaSchema
    grahas: list[GrahaSchema]
    vimshottari: list[MahaDashaSchema]
    current_maha_dasha: str | None
    current_antar_dasha: str | None

    @classmethod
    def from_chart(cls, chart: Chart) -> "ChartResponse":
        return cls(
            birth_utc=chart.birth_utc,
            ayanamsa_deg=chart.ayanamsa_deg,
            lagna=LagnaSchema(**chart.lagna.__dict__),
            grahas=[GrahaSchema(**g.__dict__) for g in chart.grahas],
            vimshottari=[
                MahaDashaSchema(
                    lord=m.lord,
                    start=m.start,
                    end=m.end,
                    antar_dashas=[AntarDashaSchema(**a.__dict__) for a in m.antar_dashas],
                )
                for m in chart.vimshottari
            ],
            current_maha_dasha=chart.current_maha_dasha,
            current_antar_dasha=chart.current_antar_dasha,
        )
