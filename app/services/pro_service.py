from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import md5
from uuid import uuid4

from app.schemas.pro import (
    CompanyStats,
    Competitor,
    CompetitorsMapResponse,
    Customer,
    KpiData,
    MarketData,
    MarketPricesQuery,
    PeriodQuery,
    Recommendation,
    RecommendationsQuery,
    RecommendationsResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    TopCustomersQuery,
    TopCustomersResponse,
)


class ProService:
    def __init__(self) -> None:
        self.recommendation_pool: list[Recommendation] = [
            Recommendation(
                id="rec-101",
                tenderNumber="44-ЭТП-2026-7741",
                title="Поставка систем мониторинга воздуха",
                customerName="ГБУЗ Клиника №52",
                region="Москва",
                okpd2="26.51",
                nmck=5_400_000,
                expectedMargin=620_000,
                winProbability=0.74,
                publishedAt=datetime.fromisoformat("2026-03-21T08:45:00+00:00"),
                reasoning="Высокая историческая конверсия по заказчику + низкое среднее снижение цены.",
            ),
            Recommendation(
                id="rec-102",
                tenderNumber="223-ЭТП-2026-1299",
                title="Поставка контрольно-измерительных шкафов",
                customerName="ПАО Сети Волга",
                region="Самарская область",
                okpd2="26.51",
                nmck=8_300_000,
                expectedMargin=980_000,
                winProbability=0.67,
                publishedAt=datetime.fromisoformat("2026-03-20T11:30:00+00:00"),
                reasoning="OKPD совпадает с сильной компетенцией; конкурентная активность ниже средней.",
            ),
            Recommendation(
                id="rec-103",
                tenderNumber="44-ЭТП-2026-5561",
                title="Поставка серверных модулей",
                customerName="ГКУ Цифровая инфраструктура",
                region="Татарстан",
                okpd2="26.20",
                nmck=12_700_000,
                expectedMargin=1_100_000,
                winProbability=0.59,
                publishedAt=datetime.fromisoformat("2026-03-19T07:15:00+00:00"),
                reasoning="Стабильная маржинальность в сегменте при умеренной конкуренции.",
            ),
            Recommendation(
                id="rec-104",
                tenderNumber="223-ЭТП-2026-1900",
                title="Поставка аналитических сенсоров",
                customerName="АО РегионЛаб",
                region="Санкт-Петербург",
                okpd2="26.51",
                nmck=3_900_000,
                expectedMargin=410_000,
                winProbability=0.48,
                publishedAt=datetime.fromisoformat("2026-03-18T09:05:00+00:00"),
                reasoning="Умеренный потенциал: у заказчика высокий объём, но волатильная цена победителя.",
            ),
            Recommendation(
                id="rec-105",
                tenderNumber="44-ЭТП-2026-9012",
                title="Поставка измерительных комплектов",
                customerName="ФГБУ Научный центр Тест",
                region="Новосибирская область",
                okpd2="26.51",
                nmck=2_600_000,
                expectedMargin=240_000,
                winProbability=0.42,
                publishedAt=datetime.fromisoformat("2026-03-17T10:10:00+00:00"),
                reasoning="Рынок узкий, но есть релевантные победы за последние 180 дней.",
            ),
        ]

        self.customer_pool: list[Customer] = [
            Customer(
                id="cust-01",
                name="ГБУЗ Клиника №52",
                proceduresCount=46,
                ownWinPercent=43,
                avgReduction=6.2,
                cancellationRate=1.5,
                delayRate=8.1,
            ),
            Customer(
                id="cust-02",
                name="ПАО Сети Волга",
                proceduresCount=31,
                ownWinPercent=38,
                avgReduction=7.8,
                cancellationRate=2.4,
                delayRate=11.3,
            ),
            Customer(
                id="cust-03",
                name="ГКУ Цифровая инфраструктура",
                proceduresCount=25,
                ownWinPercent=41,
                avgReduction=5.4,
                cancellationRate=0.8,
                delayRate=7.6,
            ),
        ]

    def get_recommendations(self, query: RecommendationsQuery, user_id: str) -> RecommendationsResponse:
        filtered = [
            self._apply_heuristic(rec, period=query.period, user_id=user_id)
            for rec in self.recommendation_pool
            if rec.nmck >= query.min_nmck
            and rec.winProbability >= query.min_prob
            and (query.okpd is None or rec.okpd2 == query.okpd)
            and (query.region is None or rec.region == query.region)
        ]
        items = filtered[: query.limit]

        return RecommendationsResponse(items=items, total=len(items), hasMore=len(filtered) > len(items))

    def get_kpi(self, query: PeriodQuery, user_id: str) -> KpiData:
        recommendations = self.get_recommendations(
            RecommendationsQuery(limit=100, min_prob=0.3, min_nmck=1_000_000, period=query.period),
            user_id=user_id,
        ).items

        avg_prob = (
            round(sum(item.winProbability for item in recommendations) / max(len(recommendations), 1), 2)
            if recommendations
            else 0.0
        )

        return KpiData(
            potentialMargin30d=round(sum(item.expectedMargin for item in recommendations) * 0.35),
            avgWinProbability=avg_prob,
            wins={"30": 5, "90": 14, "365": 52},
            deltaWins={"30": 1.2, "90": 4.7, "365": 11.9},
            avgPriceReduction=7.1,
            competitorActivityDelta=-2.4,
            proRoi={"earned": 3_840_000, "days": query.period},
        )

    def get_my_company_stats(self, query: PeriodQuery, user_id: str) -> CompanyStats:
        recs = self.get_recommendations(
            RecommendationsQuery(limit=5, min_prob=0.45, min_nmck=1_000_000, period=query.period),
            user_id=user_id,
        ).items

        return CompanyStats(
            pieOkpd2={"26.51": 58, "26.20": 24, "27.90": 18},
            pieRegions={
                "Москва": 36,
                "Санкт-Петербург": 21,
                "Татарстан": 17,
                "Новосибирская область": 11,
                "Прочие": 15,
            },
            lineWinsMargin=[
                {"period": "2025-11", "wins": 3, "margin": 280_000},
                {"period": "2025-12", "wins": 4, "margin": 410_000},
                {"period": "2026-01", "wins": 5, "margin": 520_000},
                {"period": "2026-02", "wins": 4, "margin": 470_000},
                {"period": "2026-03", "wins": 6, "margin": 690_000},
            ],
            topCustomers=self.customer_pool,
            missedOpportunities=recs[:3],
        )

    def get_top_customers(self, query: TopCustomersQuery) -> TopCustomersResponse:
        return TopCustomersResponse(items=self.customer_pool[: query.limit])

    def get_competitors_map(self, _query: PeriodQuery) -> CompetitorsMapResponse:
        competitors = [
            Competitor(
                id="comp-01",
                name="ООО ТехСнаб",
                encounters=34,
                avgReduction=10.3,
                threatLevel="high",
            ),
            Competitor(
                id="comp-02",
                name="АО Индустрия Систем",
                encounters=26,
                avgReduction=7.9,
                threatLevel="medium",
            ),
            Competitor(
                id="comp-03",
                name="ООО ЛабКомплект",
                encounters=19,
                avgReduction=6.1,
                threatLevel="low",
            ),
        ]
        return CompetitorsMapResponse(
            topCompetitors=competitors,
            intersectionMatrix={
                "ООО ТехСнаб": {"АО Индустрия Систем": 14, "ООО ЛабКомплект": 9},
                "АО Индустрия Систем": {"ООО ТехСнаб": 14, "ООО ЛабКомплект": 6},
                "ООО ЛабКомплект": {"ООО ТехСнаб": 9, "АО Индустрия Систем": 6},
            },
        )

    def get_market_prices(self, query: MarketPricesQuery) -> MarketData:
        period_adjustment = round(query.period / 3650, 2)
        return MarketData(
            priceHistory=[
                {"date": "2025-12-01", "avgPrice": 1_120_000, "contracts": 14},
                {"date": "2026-01-01", "avgPrice": 1_185_000, "contracts": 19},
                {"date": "2026-02-01", "avgPrice": 1_144_000, "contracts": 17},
                {"date": "2026-03-01", "avgPrice": 1_213_000, "contracts": 22},
            ],
            boxPlot={"min": 820_000, "q1": 1_030_000, "median": 1_160_000, "q3": 1_280_000, "max": 1_550_000},
            seasonalityHeatmap=[
                {"month": "Jan", "weekday": "Mon", "value": round(0.61 + period_adjustment, 2)},
                {"month": "Jan", "weekday": "Tue", "value": round(0.57 + period_adjustment, 2)},
                {"month": "Feb", "weekday": "Mon", "value": round(0.64 + period_adjustment, 2)},
                {"month": "Mar", "weekday": "Thu", "value": round(0.71 + period_adjustment, 2)},
            ],
        )

    def generate_report(self, payload: ReportGenerateRequest, user_id: str) -> ReportGenerateResponse:
        expires_at = datetime.now(tz=UTC) + timedelta(minutes=30)
        return ReportGenerateResponse(
            reportUrl=f"https://files.etp-pro.local/reports/{user_id}/{payload.type}-{uuid4()}.{payload.format}",
            expiresAt=expires_at,
        )

    @staticmethod
    def _apply_heuristic(rec: Recommendation, period: int, user_id: str) -> Recommendation:
        historical_confidence = min(0.15, period / 3650)

        digest = md5(f"{rec.id}:{user_id}:{period}".encode("utf-8"), usedforsecurity=False).hexdigest()
        deterministic_bias = ((int(digest[:4], 16) / 65535) - 0.5) * 0.08

        win_probability = max(0.05, min(0.98, round(rec.winProbability + historical_confidence + deterministic_bias, 2)))
        expected_margin = round(rec.nmck * (0.08 + win_probability * 0.06))

        return rec.model_copy(update={"winProbability": win_probability, "expectedMargin": expected_margin})
