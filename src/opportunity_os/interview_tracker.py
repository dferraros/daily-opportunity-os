"""
Customer Interview Tracker — ensure real market validation happens.
15 interviews required across top 3 VE opportunities by 2026-04-08.
This module tracks status and blocks pipeline advancement if interviews are missing.
"""

from __future__ import annotations
import json
import os
from datetime import date, datetime
from typing import Optional


# ─── Constants ────────────────────────────────────────────────────────────────

INTERVIEW_DEADLINE = "2026-04-08"
TOTAL_REQUIRED = 15

VALID_CONTACT_TYPES = frozenset(
    ["smb_owner", "freelancer", "diaspora", "informal_trader", "other"]
)
VALID_STATUSES = frozenset(["scheduled", "completed", "no_show", "declined"])


# ─── Path helpers ─────────────────────────────────────────────────────────────

def _project_root() -> str:
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return str(parent)
    return str(current.parents[4])


def _interviews_file() -> str:
    return os.path.join(_project_root(), "data", "interviews.jsonl")


def _opportunities_file() -> str:
    return os.path.join(_project_root(), "data", "opportunities", "opportunities.jsonl")


# ─── Read helpers ─────────────────────────────────────────────────────────────

def _read_interviews() -> list[dict]:
    """Read all interview records from interviews.jsonl."""
    path = _interviews_file()
    if not os.path.exists(path):
        return []
    results = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return results


def _lookup_opportunity(opp_id: str) -> Optional[dict]:
    """Find an opportunity record by ID in opportunities.jsonl."""
    path = _opportunities_file()
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                rec = json.loads(line)
                if rec.get("id") == opp_id:
                    return rec
            except json.JSONDecodeError:
                continue
    return None


def _days_remaining() -> int:
    """Days until the interview deadline from today."""
    today = date.today()
    deadline = date.fromisoformat(INTERVIEW_DEADLINE)
    return max(0, (deadline - today).days)


# ─── Public API ───────────────────────────────────────────────────────────────

def get_interview_quota_status() -> dict:
    """
    Return current interview quota progress against the 2026-04-08 deadline.

    Returns:
        {
            "total_required": 15,
            "completed": int,
            "scheduled": int,
            "missing": int,
            "deadline": "2026-04-08",
            "days_remaining": int,
            "on_track": bool,
        }
    """
    interviews = _read_interviews()
    completed = sum(1 for i in interviews if i.get("status") == "completed")
    scheduled = sum(1 for i in interviews if i.get("status") == "scheduled")
    missing = max(0, TOTAL_REQUIRED - completed)
    days_left = _days_remaining()

    # On-track logic: need at least 1 completed per day remaining to hit quota,
    # or already done. Allow slack if >7 days out.
    if completed >= TOTAL_REQUIRED:
        on_track = True
    elif days_left == 0:
        on_track = completed >= TOTAL_REQUIRED
    else:
        # Need to complete `missing` interviews in `days_left` days.
        # Flag as off-track if pace requires > 3 interviews/day or < 1/day
        # and we're within the warning window (7 days).
        needed_per_day = missing / days_left if days_left > 0 else missing
        if days_left <= 7:
            on_track = needed_per_day <= 3 and completed > 0
        else:
            on_track = True  # More than a week out, not yet critical

    return {
        "total_required": TOTAL_REQUIRED,
        "completed": completed,
        "scheduled": scheduled,
        "missing": missing,
        "deadline": INTERVIEW_DEADLINE,
        "days_remaining": days_left,
        "on_track": on_track,
    }


def add_interview(
    opp_id: str,
    contact_type: str,
    status: str,
    key_finding: str = "",
    wtp_confirmed: bool = False,
) -> None:
    """
    Record a customer interview event.

    Args:
        opp_id:        Opportunity this interview is for.
        contact_type:  Category of interviewee.
        status:        Interview status.
        key_finding:   Main insight from the conversation.
        wtp_confirmed: Whether willingness-to-pay was explicitly confirmed.

    Raises:
        ValueError: If contact_type or status is not a recognised value.
    """
    if contact_type not in VALID_CONTACT_TYPES:
        raise ValueError(
            f"Invalid contact_type '{contact_type}'. Must be one of: {sorted(VALID_CONTACT_TYPES)}"
        )
    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{status}'. Must be one of: {sorted(VALID_STATUSES)}"
        )

    record = {
        "opp_id": opp_id,
        "contact_type": contact_type,
        "status": status,
        "key_finding": key_finding,
        "wtp_confirmed": wtp_confirmed,
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    path = _interviews_file()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write("# interview tracking — populated by add_interview()\n")

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    quota = get_interview_quota_status()
    print(
        f"Interview recorded: {opp_id} / {contact_type} / {status}. "
        f"Progress: {quota['completed']}/{quota['total_required']}"
    )


def check_interview_gate(opp_id: str, min_interviews: int = 5) -> tuple[bool, str]:
    """
    Gate: has this opportunity accumulated enough completed interviews?

    Args:
        opp_id:          Opportunity to check.
        min_interviews:  Minimum completed interviews required (default 5).

    Returns:
        (passed: bool, reason: str)
    """
    interviews = _read_interviews()
    completed = [
        i for i in interviews
        if i.get("opp_id") == opp_id and i.get("status") == "completed"
    ]
    count = len(completed)

    if count >= min_interviews:
        return True, (
            f"Gate passed: {count}/{min_interviews} completed interviews for {opp_id}."
        )
    else:
        scheduled = sum(
            1 for i in interviews
            if i.get("opp_id") == opp_id and i.get("status") == "scheduled"
        )
        return False, (
            f"Gate blocked: only {count}/{min_interviews} completed interviews for {opp_id}. "
            f"{scheduled} scheduled, {min_interviews - count} more needed to proceed to build."
        )


def generate_interview_script(opp_id: str) -> str:
    """
    Generate a 7-question interview script in Spanish for an opportunity.

    Args:
        opp_id: Opportunity ID to generate the script for.

    Returns:
        Formatted string ready to use in WhatsApp or call.
        Falls back to a generic script if the opportunity is not found.
    """
    opp = _lookup_opportunity(opp_id)

    if opp:
        name = opp.get("name", "esta oportunidad")
        problem = opp.get("problem_statement", "el problema identificado")
        target = opp.get("target_customer", "el cliente objetivo")
        first_offer = None
        if opp.get("first_revenue_path"):
            first_offer = opp["first_revenue_path"].get("first_offer")
        price_point = None
        if opp.get("first_revenue_path"):
            price_point = opp["first_revenue_path"].get("first_price_point")
    else:
        name = opp_id
        problem = "el problema que estamos investigando"
        target = "tu perfil de cliente"
        first_offer = None
        price_point = None

    price_line = (
        f"Si ofreciéramos una solución por {price_point}, "
        "¿lo considerarías razonable? ¿Qué precio te parecería justo?"
        if price_point
        else
        "¿Cuánto estarías dispuesto/a a pagar por una solución que resuelva esto completamente? "
        "(Puedes dar un rango mensual en USD o Bs.)"
    )

    offer_line = (
        f"Te cuento brevemente: estamos pensando en ofrecer {first_offer}. "
        "¿Eso encajaría con lo que necesitas, o cambiarías algo?"
        if first_offer
        else
        "¿Qué características mínimas necesitaría tener una solución para que la usaras desde el primer día?"
    )

    script = f"""
GUION DE ENTREVISTA — {name}
Oportunidad: {opp_id}
Generado: {datetime.now().strftime("%Y-%m-%d")}
Duración estimada: 15-20 minutos
======================================================

CONTEXTO PARA EL ENTREVISTADOR:
Hablar con: {target}
Problema central: {problem}
Modo: WhatsApp voice / llamada / presencial

------------------------------------------------------
APERTURA (2 min)
------------------------------------------------------
"Hola, te llamo/escribo porque estoy investigando cómo [personas en tu situación] manejan
[área del problema]. No te voy a vender nada hoy — solo quiero entender cómo te va.
¿Tienes 15 minutos?"

------------------------------------------------------
PREGUNTAS (en orden — no saltes ninguna)
------------------------------------------------------

P1. CONFIRMACIÓN DE DOLOR
"¿Con qué frecuencia te enfrentas a este problema?
¿Cómo afecta tu día a día o tu negocio cuando ocurre?"

P2. SOLUCIÓN ACTUAL
"¿Qué haces hoy para manejarlo? ¿Tienes algún workaround, herramienta, o persona que te ayuda?"

P3. COSTO DEL WORKAROUND
"¿Cuánto tiempo o dinero te cuesta ese workaround cada semana o mes?
(Tiempo en horas, dinero en USD/Bs.)"

P4. DISPOSICIÓN A PAGAR (WTP)
"{price_line}"

P5. SEÑAL DE CONFIANZA
"Si yo te ofreciera esta solución, ¿qué necesitarías ver para confiar en que funciona?
(¿Testimonios? ¿Prueba gratis? ¿Referido de alguien que conoces?)"

P6. PROPUESTA CONCEPTUAL
"{offer_line}"

P7. CIERRE Y REFERIDOS
"¿Conoces a 2 o 3 personas más en situaciones similares que pudieran hablar conmigo?
No para venderles nada — solo para entender si el problema es común."

------------------------------------------------------
CIERRE
------------------------------------------------------
"Muchas gracias. Si avanzamos con algo concreto, ¿puedo contactarte de nuevo?"
→ Registra: nombre, contacto, disposición a ser beta tester (sí/no/quizás)

------------------------------------------------------
POST-ENTREVISTA — COMPLETAR EN < 10 MINUTOS
------------------------------------------------------
[ ] ¿Confirmó el dolor como real y frecuente? (sí/no)
[ ] ¿Mencionó un workaround activo? ¿Cuál?
[ ] WTP expresado: ___________
[ ] ¿Confirmó WTP? (sí/no)
[ ] Señal de confianza clave: ___________
[ ] Reacción a la propuesta: (positiva / neutral / escéptica)
[ ] Referidos obtenidos: ___________
[ ] ¿Vale la pena seguir? (sí / no / más datos necesarios)

Registrar resultado con: add_interview("{opp_id}", contact_type, status, key_finding, wtp_confirmed)
""".strip()

    return script
