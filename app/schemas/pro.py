from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class RecommendationsQuery(BaseModel):
    limit: int = Field(default=20, ge=1, le=100)
    min_prob: float = Field(default=0.35, ge=0, le=1)
    min_nmck: int = Field(default=1_000_000, ge=0)
    period: Literal[30, 90, 365] = 365
    okpd: str | None = None
    region: str | None = None


class PeriodQuery(BaseModel):
    period: Literal[30, 90, 365] = 365


class TopCustomersQuery(BaseModel):
    limit: int = Field(default=15, ge=1, le=50)
    period: int = Field(default=180, ge=30, le=730)


class MarketPricesQuery(BaseModel):
    okpd: str
    period: int = Field(default=365, ge=30, le=730)


class ReportGenerateRequest(BaseModel):
    type: Literal["best_customers", "losses_analysis", "price_forecast"]
    period: int = Field(ge=1)
    format: Literal["pdf", "xlsx"] = "pdf"


class Recommendation(BaseModel):
    id: str
    tenderNumber: str
    title: str
    customerName: str
    region: str
    okpd2: str
    nmck: int
    expectedMargin: int
    winProbability: float
    publishedAt: datetime
    reasoning: str


class RecommendationsResponse(BaseModel):
    items: list[Recommendation]
    total: int
    hasMore: bool


class KpiData(BaseModel):
    potentialMargin30d: int
    avgWinProbability: float
    wins: dict[str, int]
    deltaWins: dict[str, float]
    avgPriceReduction: float
    competitorActivityDelta: float
    proRoi: dict[str, int]


class Customer(BaseModel):
    id: str
    name: str
    proceduresCount: int
    ownWinPercent: float
    avgReduction: float
    cancellationRate: float
    delayRate: float


class CompanyStats(BaseModel):
    pieOkpd2: dict[str, int]
    pieRegions: dict[str, int]
    lineWinsMargin: list[dict[str, Any]]
    topCustomers: list[Customer]
    missedOpportunities: list[Recommendation]


class TopCustomersResponse(BaseModel):
    items: list[Customer]


class Competitor(BaseModel):
    id: str
    name: str
    encounters: int
    avgReduction: float
    threatLevel: Literal["low", "medium", "high"]


class CompetitorsMapResponse(BaseModel):
    topCompetitors: list[Competitor]
    intersectionMatrix: dict[str, dict[str, int]] | None = None


class MarketData(BaseModel):
    priceHistory: list[dict[str, Any]]
    boxPlot: dict[str, float]
    seasonalityHeatmap: list[dict[str, Any]]


class ReportGenerateResponse(BaseModel):
    reportUrl: str
    expiresAt: datetime
