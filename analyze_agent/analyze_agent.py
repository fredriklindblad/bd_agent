from __future__ import annotations
from typing import List
from datetime import datetime
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from analyze_agent.utils import (
    _load_yaml_params,
    to_float,
    _extract_year,
)
from analyze_agent.scorecard import (build_scorecard, build_thesis_and_verdict)
from analyze_agent.match_name_ticker import match_name_to_ticker
from bd.bd_provider import FlexibleBorsdataProvider
from bd.bd_client import BorsdataClient
from bd.bd_models import (
    AnalyzeRequest,
    Metrics,
    ScoreItem,
    AnalyzeResponse,
)


# =========================
# LLM-steget (tolka bolagsnamn/ticker)
# =========================

_SYSTEM_PROMPT = """
                    Tolkar investerarens fråga och returnerar ENDAST JSON:
                    {"company": "<ticker eller bolagsnamn>"}

                    Regler:
                    - Returnera bara ren JSON (ingen text runt).
                    - Om användaren skriver "analyze evo", returnera {"company": "EVO"}.
                    - Vid osäkerhet: välj mest sannolika svenska large/mid-cap.
                    """.strip()

_company_agent = Agent(
    model=OpenAIModel("gpt-4o"),
    output_type=AnalyzeRequest,
    system_prompt=_SYSTEM_PROMPT,
)

# =========================
# Publik entrypoint
# =========================

def run_analyze(user_prompt: str) -> AnalyzeResponse:
    print(f"\n🗨️  Fråga till analyze-agenten: {user_prompt}")

    parsed = _company_agent.run_sync(user_prompt).output
    company_query = parsed.company
    print(f"🎯 Tolkat bolag: {company_query}")

    # 1) Matcha mot Instrument[name] -> få (ticker, name)
    bd = BorsdataClient()
    ticker, resolved_name = match_name_to_ticker(bd, company_query)
    print(f"🔎 Match: {resolved_name} → {ticker}")

    # 2) Hämta params och metrics baserat på TICKER
    params = _load_yaml_params("config/params.yaml")
    provider = FlexibleBorsdataProvider(bd)
    print('BDDDDD')
    print(type(bd))
    print(bd)
    print('provider')
    print(provider)
    print(type(provider))

    kr = provider.key_ratios_by_ticker(ticker) or {}
    q  = provider.quote_by_ticker(ticker) or {}

    ebit_margin = to_float(kr.get("EbitMargin"))
    rev_cagr = to_float(kr.get("RevenueCagr5Y"))  # finns ofta inte i BD-kr -> blir None
    rule_of_40 = (ebit_margin + rev_cagr) if (ebit_margin is not None and rev_cagr is not None) else None

    as_of = str(kr.get("asOf") or "")
    year = kr.get("year") or _extract_year(as_of) or datetime.now().year

    kpi = provider.enrich_metrics_from_kpis(ticker)

    snapshot = Metrics(
        as_of=as_of,
        year=int(year),
        price=to_float(q.get("price")),
        market_cap=to_float(q.get("marketCap")),
        pe=to_float(kr.get("PE")),
        ev_ebit=to_float(kr.get("EV_EBIT")),
        ev_sales=to_float(kr.get("EV_Sales")),
        roic=to_float(kpi.get("ROIC") if kpi.get("ROIC") is not None else kr.get("ROIC")),
        ebit_margin=to_float(kpi.get("EbitMargin") if kpi.get("EbitMargin") is not None else kr.get("EbitMargin")),
        gross_margin=to_float(kpi.get("GrossMargin") if kpi.get("GrossMargin") is not None else kr.get("GrossMargin")),
        revenue_cagr_5y=to_float(kpi.get("RevenueCagr5Y")),
        ebit_cagr_5y=to_float(kpi.get("EbitCagr5Y")),
        net_debt_ebitda=to_float(kpi.get("NetDebtEbitda")),
        interest_coverage=None,           # (saknas i KPI-listan -> låt vara None)
        payout_ratio=None,                # (kräver egen beräkning / annan endpoint)
        dividend_stability_years=None,    # (kräver utdelningshistorik)
        rule_of_40=(
            to_float(kpi.get("RevenueCagr5Y")) + to_float(kpi.get("EbitMargin"))
            if (kpi.get("RevenueCagr5Y") is not None and kpi.get("EbitMargin") is not None)
            else None
        ),
    )

    sc = build_scorecard(snapshot, params)
    thesis, verdict = build_thesis_and_verdict(sc)

    # 3) Utskrift i samma stil som screenern
    print("\n📈 ANALYSRESULTAT")
    print(f"{resolved_name} ({ticker})")
    if snapshot.as_of:
        print(f"As of: {snapshot.as_of}")
    print(f"Verdict: {verdict}")
    print(f"Thesis: {thesis}")

    def _print_group(title: str, items: List[ScoreItem]):
        if not items: return
        print(f"\n{title}:")
        for it in items:
            flag = "✅" if it.passed is True else ("⚠️" if it.passed is False else "•")
            rule = f" ({it.rule})" if it.rule else ""
            print(f"  {flag} {it.metric}: {it.value}{rule}")

    _print_group("Valuation", sc.valuation)
    _print_group("Quality", sc.quality)
    _print_group("Growth", sc.growth)
    _print_group("Health", sc.health)
    _print_group("Dividend", sc.dividend)
    _print_group("Signals", sc.signals)
    print(f"\nOverall pass vs params: {sc.overall_pass}")

    # 4) Returnera strukturerat svar
    return AnalyzeResponse(
        ticker=ticker,
        name=resolved_name,
        market=None,
        sector=None,
        branch=None,
        snapshot=snapshot,
        scorecard=sc,
        verdict=verdict,
        thesis=thesis,
        risks=[],
        catalysts=[],
    )

