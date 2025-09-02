# analyze_agent/analyze_agent.py (utdrag—visa ändringar)
from __future__ import annotations

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from bd.bd_metadata import get_global_instruments_info
from bd.bd_models import CompanyInterpretation

# from analyze_agent.resolve_ticker_tool import resolve_ticker_tool

# from bd.bd_client import BorsdataClient
# from bd.bd_models import (  # AnalyzeRequest är nu utökad!
#     AnalyzeRequest,
# )

# _SYSTEM_PROMPT = """
#                     Du hjälper användaren att tolka vilket bolag som syftas på genom att avläsa user prompt.

#                     Du ska leta i hjälper investeraren att analysera ETT börsbolag.

#                     Du har ETT tool: `resolve_ticker_tool` som tar användarens text och returnerar tickern till det bolag användaren syftar på från Börsdata-universumet.

#                     REGLER:
#                     - Du MÅSTE anropa `resolve_ticker_tool` exakt en gång med användarens text för att mappa till rätt ticker.
#                     - Svara ENDAST med JSON enligt output-modellen (AnalyzeRequest).
#                     - Fält att fylla av dig:
#                     - company: <<tickern från tool-svaret, t.ex. "SWED A">>
#                     - rationale: kort motivering (1–2 meningar) varför denna ticker matchar prompten.
#                     - Fält som du INTE ska fylla (de fylls av systemet efter körning): tools_used, deps_used, tool_calls.
#                     Exempel: {"company":"SWED A","rationale":"Användaren sa 'svenska handelsbanken'; tool mappade detta till SHB A."}
#                     """.strip()


# @dataclass
# class Deps:
#     bd: BorsdataClient
#     instruments: List[Dict[str, str]]


# _company_agent = Agent(
#     model=OpenAIModel("gpt-4o"),
#     output_type=AnalyzeRequest,  # {"company": "<TICKER>", "rationale": "...", ...}
#     system_prompt=_SYSTEM_PROMPT,  # se ovan
#     tools=[resolve_ticker_tool],  # finns i separat fil
#     deps_type=Deps,  # använder instruments list nedan
# )


# def build_instrument_index(raw) -> List[Dict[str, str]]:
#     index = []
#     for it in raw or []:
#         ticker = getattr(it, "ticker", None) or it.get("ticker")
#         name = getattr(it, "name", None) or it.get("name")
#         if ticker and name:
#             index.append({"ticker": ticker, "name": name})
#     return index


# def _lookup_name_from_ticker(ticker: str, instruments: list[dict[str, str]]) -> str:
#     t = ticker.upper().strip()
#     print(instruments)
#     for ins in instruments:
#         if str(ins.get("ticker", "")).upper() == t:
#             return ins.get("name") or ins.get("companyName") or ticker
#     return ticker  # fallback till ticker om inget hittas


def run_analyze(user_prompt: str):
    print(f"\n🗨️  Fråga till analyze-agenten: {user_prompt}")
    # 1) TOLKA BOLAG (tolka prompt → bolag)
    model = OpenAIModel("gpt-4o")
    system_prompt = """
                        Du är en namntolkningsagent. Du ska hjälpa till att matcha användarens prompt
                        till en bästa matchning från en lista. Du ska returnera i form av namn och InsId.
                        Du har fått en JSON som Deps i vilken du ska leta bland 'name' och 'ticker' för
                        att tolka vilket bolag användaren menar.
                        Returnera ETT bolag enligt output type där du tar 'InsId', 'name' och 'ticker' från deps för
                        att returnera output.
                    """
    name_agent = Agent(
        model=model,
        output_type=CompanyInterpretation,
        deps_type=get_global_instruments_info(),
        system_prompt=system_prompt,
    )
    result = name_agent.run_sync(user_prompt)
    print(result)

    # deps = Deps(
    #     bd=BorsdataClient(),
    #     instruments=build_instrument_index(get_nordics_instruments()),
    # )
    # result = _company_agent.run_sync(user_prompt, deps=deps)
    # print("result_output: ", result.output)
    # ticker = result.output.company
    # print(result.all_messages)
    # print(result.all_messages_json)

    # # 2) Plocka ut tool-anropen (filtrera så vi inte råkar ta med agentens interna output-tool)
    # tools_used, tool_calls = extract_tools_metadata(result, {resolve_ticker_tool.name})

    # # ❷ Lista över deps du faktiskt nyttjar (utöka vid behov)
    # deps_used = [type(deps.bd).__name__]

    # # ❸ Uppdatera din strukturerade output (AnalyzeRequest) med metadata
    # parsed = result.output.model_copy(
    #     update={
    #         "tools_used": tools_used,
    #         "deps_used": deps_used,
    #         "tool_calls": tool_calls,
    #     }
    # )

    # print(parsed)  # nu ser du tools_used, deps_used, tool_calls i konsolen

    # ticker = parsed.company
    # print(f"🔍 Tolkat bolag/ticker: {ticker} (rationale: {parsed.rationale})")
    # name = _lookup_name_from_ticker(ticker, deps.instruments)

    # # 3) Datahämtning/scorecard (oförändrat)
    # params = _load_yaml_params("config/params.yaml")
    # provider = FlexibleBorsdataProvider(deps)

    # kr = provider.key_ratios_by_ticker(ticker) or {}
    # q = provider.quote_by_ticker(ticker) or {}
    # kpi = provider.enrich_metrics_from_kpis(ticker)

    # as_of = str(kr.get("asOf") or "")
    # year = kr.get("year") or _extract_year(as_of) or datetime.now().year

    # snapshot = Metrics(
    #     as_of=as_of,
    #     year=int(year),
    #     price=to_float(q.get("price")),
    #     market_cap=to_float(q.get("marketCap")),
    #     pe=to_float(kr.get("PE")),
    #     ev_ebit=to_float(kr.get("EV_EBIT")),
    #     ev_sales=to_float(kr.get("EV_Sales")),
    #     roic=to_float(
    #         kpi.get("ROIC") if kpi.get("ROIC") is not None else kr.get("ROIC")
    #     ),
    #     ebit_margin=to_float(
    #         kpi.get("EbitMargin")
    #         if kpi.get("EbitMargin") is not None
    #         else kr.get("EbitMargin")
    #     ),
    #     gross_margin=to_float(
    #         kpi.get("GrossMargin")
    #         if kpi.get("GrossMargin") is not None
    #         else kr.get("GrossMargin")
    #     ),
    #     revenue_cagr_5y=to_float(kpi.get("RevenueCagr5Y")),
    #     ebit_cagr_5y=to_float(kpi.get("EbitCagr5Y")),
    #     net_debt_ebitda=to_float(kpi.get("NetDebtEbitda")),
    #     interest_coverage=None,
    #     payout_ratio=None,
    #     dividend_stability_years=None,
    #     rule_of_40=(
    #         to_float(kpi.get("RevenueCagr5Y")) + to_float(kpi.get("EbitMargin"))
    #         if (
    #             kpi.get("RevenueCagr5Y") is not None
    #             and kpi.get("EbitMargin") is not None
    #         )
    #         else None
    #     ),
    # )

    # sc = build_scorecard(snapshot, params)
    # thesis, verdict = build_thesis_and_verdict(sc)

    # # 5) Utskrift (CLI) – visa även rationale & tools
    # print("\n📈 ANALYSRESULTAT")
    # print(f"{name} ({ticker})")
    # if snapshot.as_of:
    #     print(f"As of: {snapshot.as_of}")
    # if parsed.rationale:
    #     print(f"Rationale: {parsed.rationale}")
    # if parsed.tools_used:
    #     print(f"Tools used: {', '.join(parsed.tools_used)}")
    # if parsed.deps_used:
    #     print(f"Deps used: {', '.join(parsed.deps_used)}")
    # print(f"Verdict: {verdict}")
    # print(f"Thesis: {thesis}")

    # def _print_group(title: str, items: List[ScoreItem]):
    #     if not items:
    #         return
    #     print(f"\n{title}:")
    #     for it in items:
    #         flag = "✅" if it.passed is True else ("⚠️" if it.passed is False else "•")
    #         rule = f" ({it.rule})" if it.rule else ""
    #         print(f"  {flag} {it.metric}: {it.value}{rule}")

    # _print_group("Valuation", sc.valuation)
    # _print_group("Quality", sc.quality)
    # _print_group("Growth", sc.growth)
    # _print_group("Health", sc.health)
    # _print_group("Dividend", sc.dividend)
    # _print_group("Signals", sc.signals)
    # print(f"\nOverall pass vs params: {sc.overall_pass}")

    # # 6) Returnera strukturerat svar (AnalyzeResponse) som tidigare
    # return AnalyzeResponse(
    #     ticker=ticker,
    #     name=name,
    #     market=None,
    #     sector=None,
    #     branch=None,
    #     snapshot=snapshot,
    #     scorecard=sc,
    #     verdict=verdict,
    #     thesis=thesis,
    #     risks=[],
    #     catalysts=[],
    # )
