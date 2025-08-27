# analyze_agent/company_tool.py

from __future__ import annotations

import json
import re
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple
from unicodedata import normalize

from pydantic import BaseModel, ConfigDict
from pydantic_ai import RunContext

from analyze_agent.utils import _clean_name, clean_query
from bd.bd_client import BorsdataClient
from bd.bd_models import ToolCall

# -----------------
# Settings
# -----------------
LLM_RERANK_MODEL = "gpt-4o-mini"  # eller "gpt-4o" om du vill
CONFIDENCE_MIN = 0.60  # kräv lite högre säkerhet
SHORTLIST_K = 50
DEBUG_MATCH = False

# Tokens att ignorera i "måste finnas i namnet"
DEMONYM_TOKENS = {
    "svensk",
    "svenska",
    "svenskt",
    "swedish",
    "norsk",
    "norska",
    "danish",
    "dansk",
    "danska",
    "finsk",
    "finska",
    "skandinavisk",
    "skandinaviska",
    "nordic",
    "norden",
}
GENERIC_TOKENS = {
    "ab",
    "asa",
    "abp",
    "publ",
    "sa",
    "oyj",
    "co",
    "inc",
    "corp",
    "group",
    "aktiebolag",
    "bankaktiebolag",
}
STOPWORDS = DEMONYM_TOKENS | GENERIC_TOKENS

# Branch/Sektor-hints
KEYWORD_BRANCH_HINTS = {"bank": ["bank"]}
KEYWORD_SECTOR_HINTS = {"bank": ["finans", "financial", "financials"]}

# Korta alias (bygg gärna ut)
ALIASES = {
    # Banker (SE)
    "svenska handelsbanken": "SHB A",
    "handelsbanken": "SHB A",
    "shb": "SHB A",
    "seb": "SEB A",
    "skandinaviska enskilda banken": "SEB A",
    "swedbank": "SWED A",
    "nordea": "NDA SE",
    "nordea bank": "NDA SE",
    # NO
    "lea bank": "LEA",
    "lea": "LEA",
}


# -----------------
# Deps för agenten
# -----------------
class Deps(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bd: BorsdataClient
    provenance: List[ToolCall] = []  # <-- NYTT: här samlar vi tool-calls

    def ensure_metadata(self) -> None:
        """Se till att instrument/metadata är laddade innan matchning."""
        try:
            loaded = False
            if hasattr(self.bd, "is_metadata_loaded"):
                loaded = bool(self.bd.is_metadata_loaded())
            else:
                loaded = bool(getattr(self.bd, "instruments", None))
            if not loaded and hasattr(self.bd, "load_metadata"):
                self.bd.load_metadata()
        except Exception:
            # Vid problem kör vi vidare – resolve_ticker_tool har fallback
            pass


# -----------------
# Helpers
# -----------------
def _get_openai_client():
    try:
        from openai import OpenAI

        return OpenAI()
    except Exception:
        return None


def _extract_minimal(it: Any) -> Dict[str, Any]:
    if isinstance(it, dict):
        get = it.get
    else:
        get = lambda k: getattr(it, k, None)
    return {
        "id": get("id") or get("ins_id") or get("InsId") or get("insId"),
        "ticker": (get("ticker") or get("Ticker") or "").strip(),
        "name": (get("name") or get("Name") or "").strip(),
        "country_id": get("country_id") or get("countryId"),
        "sector_id": get("sector_id") or get("sectorId"),
        "branch_id": get("branch_id") or get("branchId"),
        "instrument_type_name": (
            get("instrument_type_name") or get("instrumentTypeName") or ""
        ).strip(),
    }


def _norm_text(s: str) -> str:
    s = clean_query(s)
    s = _clean_name(s)
    s = normalize("NFKD", s)
    s = "".join(ch for ch in s if ord(ch) < 128)
    s = re.sub(
        r"\b(ab|publ|ab publ|s\.a\.|sa|oyj|asa|abp)\b", "", s, flags=re.IGNORECASE
    )
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _ticker_key(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").upper()).strip()


def _tokens(q: str) -> List[str]:
    qn = _norm_text(q).lower()
    toks = [t for t in re.split(r"[\s\-_/]+", qn) if t]
    return toks


def _key_tokens(q_tokens: List[str]) -> List[str]:
    # “måste finnas i namnet”-tokens = alla utom demonym/generic och *bank*
    return [t for t in q_tokens if t not in STOPWORDS and t != "bank" and len(t) >= 2]


def _all_tokens_in_name(tokens: List[str], name: str) -> bool:
    nn = _norm_text(name).lower()
    return all(t in nn for t in tokens)


def _score_base(q: str, row: Dict[str, Any]) -> float:
    name = row["name"] or ""
    ticker = row["ticker"] or ""
    nname = _norm_text(name)
    ntick = _ticker_key(ticker)
    qtick = _ticker_key(q)

    exact_name = 1.0 if nname == q else 0.0
    starts_name = 1.0 if nname.startswith(q) else 0.0
    contains = 1.0 if q in nname else 0.0
    exact_ticker = 1.0 if ntick == qtick else 0.0
    starts_tick = (
        1.0 if ntick.replace(" ", "").startswith(qtick.replace(" ", "")) else 0.0
    )

    tq = {t for t in q.split() if len(t) > 2}
    tn = {t for t in nname.split() if len(t) > 2}
    jacc = len(tq & tn) / max(1, len(tq | tn))
    fuzz = SequenceMatcher(None, nname, q).ratio()

    score = (
        100 * exact_name
        + 90 * exact_ticker
        + 65 * starts_name
        + 50 * starts_tick
        + 40 * fuzz
        + 30 * jacc
        + 15 * contains
    )
    return score


def _domain_bias(
    q_tokens: List[str],
    row: Dict[str, Any],
    bd: BorsdataClient,
    force_nordic: bool,
    bank_mode: bool,
) -> float:
    bonus = 0.0
    # Nordics
    nordic_ids = {
        k
        for k, v in getattr(bd, "COUNTRIES", {}).items()
        if v and v.lower() in {"sverige", "norge", "danmark", "finland", "island"}
    }
    if row.get("country_id") in nordic_ids:
        bonus += 12.0 if force_nordic else 6.0

    # Aktier > ETF/Index
    itype = (row.get("instrument_type_name") or "").lower()
    if "aktie" in itype or itype == "" or "stock" in itype:
        bonus += 5.0
    elif "etf" in itype or "index" in itype:
        bonus -= 3.0

    # Branch/Sektor “bank”
    if bank_mode:
        branch_name = getattr(bd, "BRANCHES", {}).get(row.get("branch_id"), "") or ""
        sector_name = getattr(bd, "SECTORS", {}).get(row.get("sector_id"), "") or ""
        if "bank" in branch_name.lower():
            bonus += 25.0
        for kw in KEYWORD_SECTOR_HINTS["bank"]:
            if kw in sector_name.lower():
                bonus += 12.0
        # straffa uppenbara fel
        bad_words = ["cannabis", "tobacco", "gaming", "oil", "mining"]
        if any(w in (branch_name + " " + sector_name).lower() for w in bad_words):
            bonus -= 20.0

    return bonus


def _score_total(
    q: str,
    q_tokens: List[str],
    row: Dict[str, Any],
    bd: BorsdataClient,
    force_nordic: bool,
    bank_mode: bool,
) -> float:
    return _score_base(q, row) + _domain_bias(
        q_tokens, row, bd, force_nordic, bank_mode
    )


def resolve_ticker_tool(ctx: RunContext[Deps], query: str) -> TickerResolution:
    # Säkerställ metadata
    try:
        ctx.deps.ensure_metadata()
    except Exception:
        pass

    bd = ctx.deps.bd
    raw_items = getattr(bd, "instruments", []) or []
    if not raw_items:
        qq = query.strip().upper()
        res = TickerResolution(ticker=qq, name=query.strip())
        # Logga tool-call för spårbarhet
        try:
            ctx.deps.provenance.append(
                ToolCall(
                    name="resolve_ticker_tool",
                    arguments={"query": query},
                    output_preview=f"{res.ticker} | {res.name}",
                    timestamp_utc=datetime.utcnow().isoformat(timespec="seconds") + "Z",
                )
            )
        except Exception:
            pass
        return res


# -----------------
# Tool-outputmodell
# -----------------
class TickerResolution(BaseModel):
    ticker: str
    name: str


# -----------------
# LLM re-ranking
# -----------------
def _rank_with_llm(
    query: str,
    key_tokens: List[str],
    bank_mode: bool,
    candidates: List[Dict[str, Any]],
    bd: BorsdataClient,
) -> Dict[str, Any]:
    client = _get_openai_client()
    if client is None or not candidates:
        return {}

    def _meta(c: Dict[str, Any]) -> str:
        cid = c.get("country_id")
        sid = c.get("sector_id")
        bid = c.get("branch_id")
        cname = getattr(bd, "COUNTRIES", {}).get(cid, "")
        sname = getattr(bd, "SECTORS", {}).get(sid, "")
        bname = getattr(bd, "BRANCHES", {}).get(bid, "")
        return " | ".join([x for x in [cname, sname, bname] if x])

    lines = [
        f"{i + 1}. {c['ticker']} | {c['name']} | {_meta(c)}"
        for i, c in enumerate(candidates)
    ]
    cand_block = "\n".join(lines)
    key_tok_str = ", ".join(key_tokens) if key_tokens else "(none)"
    bank_rule = (
        " and branch includes 'Bank' or sector is Financials" if bank_mode else ""
    )

    system = (
        "You resolve a user's company query to ONE listed security from Börsdata.\n"
        "RULES:\n"
        "- Pick EXACTLY ONE from the list; never invent.\n"
        "- Strongly prefer candidates whose NAME contains ALL key tokens.\n"
        f"- If query implies a bank, prefer banking candidates{bank_rule}.\n"
        "- Prefer Nordic listings when ambiguous.\n"
        "Return STRICT JSON: ticker, name, confidence (0-1), why."
    )
    user = (
        f"Query: {query}\n"
        f"Key tokens (must appear in name when possible): {key_tok_str}\n\n"
        f"Candidates:\n{cand_block}\n\n"
        "Answer with JSON only using the exact 'ticker' and 'name' from the list."
    )

    try:
        resp = client.chat.completions.create(
            model=LLM_RERANK_MODEL,
            temperature=0.0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = resp.choices[0].message.content or ""
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            return {}
        data = json.loads(m.group(0))
        if not data.get("ticker") or not data.get("name"):
            return {}
        try:
            data["confidence"] = float(data.get("confidence", 0))
        except Exception:
            data["confidence"] = 0.0
        tickers = {c["ticker"].upper(): c for c in candidates}
        if data["ticker"].upper() not in tickers:
            return {}
        return data
    except Exception:
        return {}


# -----------------
# Själva tool:et
# -----------------
def resolve_ticker_tool(ctx: RunContext[Deps], query: str) -> TickerResolution:
    bd = ctx.deps.bd
    raw_items = getattr(bd, "instruments", []) or []
    if not raw_items:
        qq = query.strip().upper()
        return TickerResolution(ticker=qq, name=query.strip())

    # bygga items
    items: List[Dict[str, Any]] = []
    for it in raw_items:
        row = _extract_minimal(it)
        if row["ticker"] or row["name"]:
            items.append(row)

    q_norm = _norm_text(query)
    q_tokens = _tokens(query)
    key_toks = _key_tokens(q_tokens)
    bank_mode = ("bank" in q_tokens) or any(
        t in {"handelsbanken", "swedbank", "nordea", "seb"} for t in q_tokens
    )

    # 0) Alias fast-path
    alias = ALIASES.get(q_norm.lower())
    if alias:
        by_ticker = {_ticker_key(i["ticker"]): i for i in items if i["ticker"]}
        tkey = _ticker_key(alias)
        if tkey in by_ticker:
            hit = by_ticker[tkey]
            return TickerResolution(
                ticker=hit["ticker"].upper(), name=hit["name"] or hit["ticker"].upper()
            )

    # 1) Direkt ticker?
    by_ticker = {_ticker_key(i["ticker"]): i for i in items if i["ticker"]}
    if _ticker_key(q_norm) in by_ticker:
        it = by_ticker[_ticker_key(q_norm)]
        return TickerResolution(
            ticker=it["ticker"].upper(), name=it["name"] or it["ticker"].upper()
        )

    # 2) Force Nordic om språket verkar svenskt/demonymer eller å/ä/ö förekommer
    force_nordic = bool(re.search(r"[åäöÅÄÖ]", query)) or any(
        t in DEMONYM_TOKENS for t in q_tokens
    )
    if force_nordic:
        nordic_ids = {
            k
            for k, v in getattr(bd, "COUNTRIES", {}).items()
            if v and v.lower() in {"sverige", "norge", "danmark", "finland", "island"}
        }
        items = [
            i for i in items if i.get("country_id") in nordic_ids
        ] or items  # fallback om tomt

    # 3) Prefilter: kräver alla key tokens i namnet (om möjligt)
    strict = [i for i in items if key_toks and _all_tokens_in_name(key_toks, i["name"])]
    base_pool = strict if strict else items

    # 4) Scorad shortlist (med domän-bias)
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for it in base_pool:
        s = _score_total(
            q_norm, q_tokens, it, bd, force_nordic=force_nordic, bank_mode=bank_mode
        )
        if s > 0:
            scored.append((s, it))
    if not scored:
        qq = query.strip().upper()
        return TickerResolution(ticker=qq, name=query.strip())

    scored.sort(key=lambda x: x[0], reverse=True)
    shortlist = [it for _, it in scored[:SHORTLIST_K]]

    if DEBUG_MATCH:
        print("\n-- Shortlist (top 10) --")
        for s, it in scored[:10]:
            cid = it.get("country_id")
            sname = getattr(bd, "SECTORS", {}).get(it.get("sector_id"), "")
            bname = getattr(bd, "BRANCHES", {}).get(it.get("branch_id"), "")
            print(
                f"{s:6.1f}  {it['ticker']:<8}  {it['name']}  | {cid} | {sname} | {bname}"
            )

    # 5) LLM re-rank
    llm_pick = _rank_with_llm(query, key_toks, bank_mode, shortlist, bd)

    # 6) Validering – måste uppfylla key tokens (i namn) eller bank-mode-regler
    def _valid_choice(ticker: str) -> bool:
        cand = next(
            (c for c in shortlist if c["ticker"].upper() == ticker.upper()), None
        )
        if not cand:
            return False
        if key_toks and not _all_tokens_in_name(key_toks, cand["name"]):
            # tillåt om bank_mode och branch/sector matchar bank
            if bank_mode:
                bname = getattr(bd, "BRANCHES", {}).get(cand.get("branch_id"), "") or ""
                sname = getattr(bd, "SECTORS", {}).get(cand.get("sector_id"), "") or ""
                if ("bank" in bname.lower()) or any(
                    kw in sname.lower() for kw in KEYWORD_SECTOR_HINTS["bank"]
                ):
                    pass
                else:
                    return False
            else:
                return False
        # uteslut uppenbara mismatchar vid bank_mode
        if bank_mode:
            bname = getattr(bd, "BRANCHES", {}).get(cand.get("branch_id"), "") or ""
            sname = getattr(bd, "SECTORS", {}).get(cand.get("sector_id"), "") or ""
            bad_words = ["cannabis", "tobacco", "gaming", "oil", "mining"]
            if any(w in (bname + " " + sname).lower() for w in bad_words):
                return False
        return True

    if (
        llm_pick
        and llm_pick.get("confidence", 0) >= CONFIDENCE_MIN
        and _valid_choice(llm_pick["ticker"])
    ):
        return TickerResolution(
            ticker=llm_pick["ticker"].upper(),
            name=llm_pick["name"] or llm_pick["ticker"].upper(),
        )

    # 7) Fallback: första heuristiskt giltiga
    for it in shortlist:
        if _valid_choice(it["ticker"]):
            return TickerResolution(
                ticker=it["ticker"].upper(), name=it["name"] or it["ticker"].upper()
            )

    # 8) Sista fallback
    best = shortlist[0]
    res = TickerResolution(
        ticker=best["ticker"].upper(), name=best["name"] or best["ticker"].upper()
    )
    try:
        ctx.deps.provenance.append(
            ToolCall(
                name="resolve_ticker_tool",
                arguments={"query": query},
                output_preview=f"{res.ticker} | {res.name}",
                timestamp_utc=datetime.utcnow().isoformat(timespec="seconds") + "Z",
            )
        )
    except Exception:
        pass
    return res
