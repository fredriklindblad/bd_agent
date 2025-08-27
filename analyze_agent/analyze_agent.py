# analyze_agent/analyze_agent.py (utdrag—visa ändringar)

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from analyze_agent.company_tool import Deps, resolve_ticker_tool
from analyze_agent.scorecard import build_scorecard, build_thesis_and_verdict
from analyze_agent.utils import _extract_year, _load_yaml_params, to_float
from bd.bd_client import BorsdataClient
from bd.bd_models import (  # AnalyzeRequest är nu utökad!
    AnalyzeRequest,
    AnalyzeResponse,
    Metrics,
    ScoreItem,
)
from bd.bd_provider import FlexibleBorsdataProvider

_SYSTEM_PROMPT = """
                    Du hjälper investeraren att analysera ETT svenskt börsbolag.

                    Du har ETT tool: `resolve_ticker_tool(query)` som tar användarens text och returnerar bästa tickern + namn från Börsdata-universumet.

                    REGLER:
                    - Du MÅSTE anropa `resolve_ticker_tool` exakt en gång med användarens text för att mappa till rätt ticker.
                    - Svara ENDAST med JSON enligt output-modellen (AnalyzeRequest).
                    - Fält att fylla av dig: 
                    - company: <<tickern från tool-svaret, t.ex. "SWED A">>
                    - rationale: kort motivering (1–2 meningar) varför denna ticker matchar prompten.
                    - Fält som du INTE ska fylla (de fylls av systemet efter körning): tools_used, deps_used, tool_calls.
                    Exempel: {"company":"SWED A","rationale":"Användaren sa 'svenska handelsbanken'; tool mappade detta till SHB A."}
                    """.strip()

_company_agent = Agent(
    model=OpenAIModel("gpt-4o"),
    output_type=AnalyzeRequest,  # {"company": "<TICKER>", "rationale": "...", ...}
    system_prompt=_SYSTEM_PROMPT,
    tools=[resolve_ticker_tool],
    deps_type=Deps,
)


def run_analyze(user_prompt: str) -> AnalyzeResponse:
    print(f"\n🗨️  Fråga till analyze-agenten: {user_prompt}")

    # 1) Kör agenten med deps (vi återanvänder samma deps-objekt för att komma åt provenance)
    bd = BorsdataClient()
    deps = Deps(bd=bd)  # innehåller provenance-listan
    result = _company_agent.run_sync(user_prompt, deps=deps)
    parsed = result.output  # typ: AnalyzeRequest

    # Robust: säkerställ ticker
    ticker = (parsed.company or "").strip().upper()
    if not ticker:
        raise ValueError("Kunde inte tolka en giltig ticker från frågan.")

    # 2) Fyll i proveniens-fälten (från deps.provenance)
    tools_used = []
    tool_calls = []
    for call in deps.provenance or []:
        tools_used.append(call.name)
        tool_calls.append(call)
    # unika i ordning
    seen = set()
    tools_used = [t for t in tools_used if not (t in seen or seen.add(t))]
    deps_used = [type(deps.bd).__name__]  # t.ex. ["BorsdataClient"]

    parsed = parsed.model_copy(
        update={
            "tools_used": tools_used,
            "deps_used": deps_used,
            "tool_calls": tool_calls,
        }
    )

    # 3) Lookup visningsnamn + hämta data som tidigare
    def _lookup_name_from_ticker(bd: BorsdataClient, ticker: str) -> str:
        t_up = (ticker or "").upper()
        for it in getattr(bd, "instruments", []) or []:
            if isinstance(it, dict):
                if (it.get("ticker", "") or "").upper() == t_up:
                    return it.get("name") or t_up
            else:
                if (getattr(it, "ticker", "") or "").upper() == t_up:
                    return getattr(it, "name", None) or t_up
        return t_up

    resolved_name = _lookup_name_from_ticker(bd, ticker)
    print(f"🎯 Tolkat bolag (ticker): {ticker}")
    print(f"🔎 Match: {resolved_name} → {ticker}")

    # 4) Datahämtning/scorecard (oförändrat)
    params = _load_yaml_params("config/params.yaml")
    provider = FlexibleBorsdataProvider(bd)

    kr = provider.key_ratios_by_ticker(ticker) or {}
    q = provider.quote_by_ticker(ticker) or {}
    kpi = provider.enrich_metrics_from_kpis(ticker)

    as_of = str(kr.get("asOf") or "")
    year = kr.get("year") or _extract_year(as_of) or datetime.now().year

    snapshot = Metrics(
        as_of=as_of,
        year=int(year),
        price=to_float(q.get("price")),
        market_cap=to_float(q.get("marketCap")),
        pe=to_float(kr.get("PE")),
        ev_ebit=to_float(kr.get("EV_EBIT")),
        ev_sales=to_float(kr.get("EV_Sales")),
        roic=to_float(
            kpi.get("ROIC") if kpi.get("ROIC") is not None else kr.get("ROIC")
        ),
        ebit_margin=to_float(
            kpi.get("EbitMargin")
            if kpi.get("EbitMargin") is not None
            else kr.get("EbitMargin")
        ),
        gross_margin=to_float(
            kpi.get("GrossMargin")
            if kpi.get("GrossMargin") is not None
            else kr.get("GrossMargin")
        ),
        revenue_cagr_5y=to_float(kpi.get("RevenueCagr5Y")),
        ebit_cagr_5y=to_float(kpi.get("EbitCagr5Y")),
        net_debt_ebitda=to_float(kpi.get("NetDebtEbitda")),
        interest_coverage=None,
        payout_ratio=None,
        dividend_stability_years=None,
        rule_of_40=(
            to_float(kpi.get("RevenueCagr5Y")) + to_float(kpi.get("EbitMargin"))
            if (
                kpi.get("RevenueCagr5Y") is not None
                and kpi.get("EbitMargin") is not None
            )
            else None
        ),
    )

    sc = build_scorecard(snapshot, params)
    thesis, verdict = build_thesis_and_verdict(sc)

    # 5) Utskrift (CLI) – visa även rationale & tools
    print("\n📈 ANALYSRESULTAT")
    print(f"{resolved_name} ({ticker})")
    if snapshot.as_of:
        print(f"As of: {snapshot.as_of}")
    if parsed.rationale:
        print(f"Rationale: {parsed.rationale}")
    if parsed.tools_used:
        print(f"Tools used: {', '.join(parsed.tools_used)}")
    if parsed.deps_used:
        print(f"Deps used: {', '.join(parsed.deps_used)}")
    print(f"Verdict: {verdict}")
    print(f"Thesis: {thesis}")

    def _print_group(title: str, items: List[ScoreItem]):
        if not items:
            return
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

    # 6) Returnera strukturerat svar (AnalyzeResponse) som tidigare
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
