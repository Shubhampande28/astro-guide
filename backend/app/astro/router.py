"""The /chart endpoint: computes a full Kundli from birth details."""

from fastapi import APIRouter

from app.astro.chart import compute_chart
from app.astro.schemas import ChartRequest, ChartResponse

router = APIRouter(prefix="/chart", tags=["chart"])


@router.post("", response_model=ChartResponse)
def post_chart(request: ChartRequest) -> ChartResponse:
    chart = compute_chart(
        birth_date=request.birth_date,
        birth_time=request.birth_time,
        tz_name=request.timezone,
        latitude_deg=request.latitude,
        longitude_east_deg=request.longitude,
        as_of=request.as_of,
    )
    return ChartResponse.from_chart(chart)
