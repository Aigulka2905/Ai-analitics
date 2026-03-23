from typing import Literal

from fastapi import APIRouter, Depends, Query

from app.core.security import AuthUser, get_current_user
from app.schemas.pro import (
    CompanyStats,
    CompetitorsMapResponse,
    KpiData,
    MarketData,
    MarketPricesQuery,
    PeriodQuery,
    RecommendationsQuery,
    RecommendationsResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    TopCustomersQuery,
    TopCustomersResponse,
)
from app.services.pro_service import ProService

router = APIRouter(prefix="/pro", tags=["pro"])
service = ProService()


@router.get("/recommendations", response_model=RecommendationsResponse)
def get_recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    min_prob: float = Query(default=0.35, ge=0, le=1),
    min_nmck: int = Query(default=1_000_000, ge=0),
    period: Literal[30, 90, 365] = Query(default=365),
    okpd: str | None = None,
    region: str | None = None,
    user: AuthUser = Depends(get_current_user),
) -> RecommendationsResponse:
    query = RecommendationsQuery(
        limit=limit,
        min_prob=min_prob,
        min_nmck=min_nmck,
        period=period,
        okpd=okpd,
        region=region,
    )
    return service.get_recommendations(query, user_id=user.user_id)


@router.get("/kpi", response_model=KpiData)
def get_kpi(
    period: Literal[30, 90, 365] = Query(default=365),
    user: AuthUser = Depends(get_current_user),
) -> KpiData:
    return service.get_kpi(PeriodQuery(period=period), user_id=user.user_id)


@router.get("/my-company/stats", response_model=CompanyStats)
def get_company_stats(
    period: Literal[30, 90, 365] = Query(default=365),
    user: AuthUser = Depends(get_current_user),
) -> CompanyStats:
    return service.get_my_company_stats(PeriodQuery(period=period), user_id=user.user_id)


@router.get("/customers/top", response_model=TopCustomersResponse)
def get_top_customers(
    limit: int = Query(default=15, ge=1, le=50),
    period: int = Query(default=180, ge=30, le=730),
    _user: AuthUser = Depends(get_current_user),
) -> TopCustomersResponse:
    return service.get_top_customers(TopCustomersQuery(limit=limit, period=period))


@router.get("/competitors/map", response_model=CompetitorsMapResponse)
def get_competitors_map(
    period: Literal[30, 90, 365] = Query(default=365),
    _user: AuthUser = Depends(get_current_user),
) -> CompetitorsMapResponse:
    return service.get_competitors_map(PeriodQuery(period=period))


@router.get("/market/prices", response_model=MarketData)
def get_market_prices(
    okpd: str,
    period: int = Query(default=365, ge=30, le=730),
    _user: AuthUser = Depends(get_current_user),
) -> MarketData:
    return service.get_market_prices(MarketPricesQuery(okpd=okpd, period=period))


@router.post("/report/generate", response_model=ReportGenerateResponse)
def generate_report(
    payload: ReportGenerateRequest,
    user: AuthUser = Depends(get_current_user),
) -> ReportGenerateResponse:
    return service.generate_report(payload, user_id=user.user_id)
