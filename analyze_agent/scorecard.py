# =========================
# Scorecard & verdict
# =========================

from typing import Any, Dict, List, Tuple
from bd.bd_models import Metrics, ScoreItem, Scorecard
from analyze_agent.utils import to_float, fmt_rule, ratio_pass
from typing import TypeVar
T = TypeVar('T')


def build_scorecard(metrics: Metrics, params: Dict[str, Any]) -> Scorecard:
    val = params.get("valuation_rules") or {}
    qual = params.get("quality_rules") or {}
    grow = params.get("growth_rules") or {}
    hlth = params.get("financial_health") or {}
    divd = params.get("dividend_policy") or {}
    sign = params.get("signals") or {}

    sc = Scorecard()

    sc.valuation += [
        ScoreItem(metric="P/E",        value=metrics.pe,       rule=fmt_rule("<=", to_float(val.get("pe_max"))),            passed=ratio_pass(metrics.pe, "<=", to_float(val.get("pe_max")))),
        ScoreItem(metric="EV/EBIT",    value=metrics.ev_ebit,  rule=fmt_rule("<=", to_float(val.get("ev_ebit_max"))),       passed=ratio_pass(metrics.ev_ebit, "<=", to_float(val.get("ev_ebit_max")))),
        ScoreItem(metric="EV/Sales",   value=metrics.ev_sales, rule=fmt_rule("<=", to_float(val.get("ev_sales_max"))),      passed=ratio_pass(metrics.ev_sales, "<=", to_float(val.get("ev_sales_max")))),
    ]

    sc.quality += [
        ScoreItem(metric="ROIC (%)",         value=metrics.roic,        rule=fmt_rule(">=", to_float(qual.get("roic_min"))),            passed=ratio_pass(metrics.roic, ">=", to_float(qual.get("roic_min")))),
        ScoreItem(metric="EBIT margin (%)",  value=metrics.ebit_margin, rule=fmt_rule(">=", to_float(qual.get("ebit_margin_min"))),     passed=ratio_pass(metrics.ebit_margin, ">=", to_float(qual.get("ebit_margin_min")))),
        ScoreItem(metric="Gross margin (%)", value=metrics.gross_margin,rule=fmt_rule(">=", to_float(qual.get("gross_margin_min"))),    passed=ratio_pass(metrics.gross_margin, ">=", to_float(qual.get("gross_margin_min")))),
    ]

    sc.growth += [
        ScoreItem(metric="Revenue CAGR 5y (%)", value=metrics.revenue_cagr_5y, rule=fmt_rule(">=", to_float(grow.get("revenue_cagr_5y_min"))), passed=ratio_pass(metrics.revenue_cagr_5y, ">=", to_float(grow.get("revenue_cagr_5y_min")))),
        ScoreItem(metric="EBIT CAGR 5y (%)",    value=metrics.ebit_cagr_5y,    rule=fmt_rule(">=", to_float(grow.get("ebit_cagr_5y_min"))),    passed=ratio_pass(metrics.ebit_cagr_5y, ">=", to_float(grow.get("ebit_cagr_5y_min")))),
    ]

    sc.health += [
        ScoreItem(metric="Net debt / EBITDA",    value=metrics.net_debt_ebitda,   rule=fmt_rule("<=", to_float(hlth.get("net_debt_ebitda_max"))), passed=ratio_pass(metrics.net_debt_ebitda, "<=", to_float(hlth.get("net_debt_ebitda_max")))),
        ScoreItem(metric="Interest coverage (x)",value=metrics.interest_coverage, rule=fmt_rule(">=", to_float(hlth.get("interest_coverage_min"))),passed=ratio_pass(metrics.interest_coverage, ">=", to_float(hlth.get("interest_coverage_min")))),
    ]

    sc.dividend += [
        ScoreItem(metric="Payout ratio (%)",         value=metrics.payout_ratio,              rule=fmt_rule("<=", to_float(divd.get("payout_max"))),                 passed=ratio_pass(metrics.payout_ratio, "<=", to_float(divd.get("payout_max")))),
        ScoreItem(metric="Dividend stability (yrs)", value=to_float(metrics.dividend_stability_years), rule=fmt_rule(">=", to_float(divd.get("dividend_stability_min_years"))), passed=ratio_pass(to_float(metrics.dividend_stability_years), ">=", to_float(divd.get("dividend_stability_min_years")))),
    ]

    sc.signals += [
        ScoreItem(metric="Rule of 40", value=metrics.rule_of_40, rule=fmt_rule(">=", to_float(sign.get("rule_of_40_min"))), passed=ratio_pass(metrics.rule_of_40, ">=", to_float(sign.get("rule_of_40_min")))),
    ]

    def group_pass(items: List[ScoreItem]) -> bool:
        checked = [it.passed for it in items if it.rule is not None]
        if not checked:
            return True  # ingen data ⇒ neutral (fäll inte caset)
        return any(p is True for p in checked) and not any(p is False for p in checked)

    sc.overall_pass = all([
        group_pass(sc.valuation),
        group_pass(sc.quality),
        group_pass(sc.growth),
        group_pass(sc.health),
        group_pass(sc.dividend),
        group_pass(sc.signals),
    ])

    return sc


def build_thesis_and_verdict(sc: Scorecard) -> Tuple[str, str]:
    if sc.overall_pass is True:
        return ("Bolaget passerar dina kärntrösklar inom värdering, kvalitet och tillväxt. "
                "Givet parametrarna ser caset attraktivt ut.", "BUY")
    val_fail = any(i.passed is False for i in sc.valuation if i.rule)
    qual_ok = not any(i.passed is False for i in sc.quality if i.rule)
    grow_ok = not any(i.passed is False for i in sc.growth if i.rule)
    if (qual_ok and grow_ok) and val_fail:
        return ("Kvalitet och tillväxt ser goda ut, men värderingen är över dina gränser. "
                "Håll under bevakning och invänta bättre pris.", "HOLD")
    return ("Bolaget uppfyller inte tillräckligt många kriterier eller saknar nyckeldata för bedömning.", "AVOID")