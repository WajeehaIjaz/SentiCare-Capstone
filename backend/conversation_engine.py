# backend/chatbot/conversation_engine.py

from backend.chatbot.router            import route_condition
from backend.chatbot.predictor         import predict
from backend.chatbot.template_selector import select_template

from backend.chatbot.questions.anxiety_questions    import ANXIETY_FEATURE_QUESTIONS
from backend.chatbot.questions.stress_questions     import STRESS_FEATURE_QUESTIONS
from backend.chatbot.questions.depression_questions import DEPRESSION_FEATURE_QUESTIONS


_SCREENING_DOMAIN_MAP: dict[str, str] = {
    "feeling_nervous":      "anxiety",
    "uncontrollable_worry": "anxiety",
    "restlessness":         "anxiety",
    "feeling_down":         "depression",
    "loss_of_interest":     "depression",
    "fatigue":              "depression",
    "overwhelmed":          "stress",
    "irritability":         "stress",
}

_INT_TO_LEVEL: dict[int, str] = {0: "low", 1: "medium", 2: "high"}
_FALLBACK_LEVEL = "medium"


class ConversationEngine:

    def __init__(self):
        pass

    # ── Screening 

    def calculate_screening_scores(self, screening_answers: dict) -> dict:
        scores = {"anxiety": 0, "depression": 0, "stress": 0}
        for q_id, val in screening_answers.items():
            domain = _SCREENING_DOMAIN_MAP.get(q_id)
            if domain:
                try:
                    scores[domain] += int(val)
                except (TypeError, ValueError):
                    pass
        print(f"[ConversationEngine] screening_scores={scores}", flush=True)
        return scores

    def determine_condition(self, scores: dict) -> str:
        return route_condition(scores)

    # ── Feature questions 
    def get_feature_questions(self, condition: str) -> list:
        if condition == "anxiety":    return ANXIETY_FEATURE_QUESTIONS
        if condition == "stress":     return STRESS_FEATURE_QUESTIONS
        if condition == "depression": return DEPRESSION_FEATURE_QUESTIONS
        return []

    # ── Prediction 

    def run_prediction(self, condition: str, feature_answers: dict):
        return predict(condition, feature_answers)

    def map_prediction_to_level(self, prediction) -> str:
        if prediction is None:
            print(
                f"[ConversationEngine] ⚠️  map_prediction_to_level received None "
                f"— defaulting to '{_FALLBACK_LEVEL}'.",
                flush=True,
            )
            return _FALLBACK_LEVEL

        try:
            val = int(float(str(prediction)))
            result = _INT_TO_LEVEL.get(val)
            if result:
                print(
                    f"[ConversationEngine] map_prediction_to_level: "
                    f"{prediction!r} → '{result}'",
                    flush=True,
                )
                return result
        except (TypeError, ValueError):
            pass

        print(
            f"[ConversationEngine] ⚠️  Unrecognised prediction={prediction!r}. "
            f"Defaulting to '{_FALLBACK_LEVEL}'.",
            flush=True,
        )
        return _FALLBACK_LEVEL

    # ── CBT response 

    def generate_cbt_response(
        self,
        condition:      str,
        level:          str,
        lang:           str = "en",
        voice_dominant: str = "neutral",     
    ) -> dict | None:
        if not level:
            print(
                f"[ConversationEngine] ⚠️  generate_cbt_response called with "
                f"level={level!r}. Substituting '{_FALLBACK_LEVEL}'.",
                flush=True,
            )
            level = _FALLBACK_LEVEL

        print(
            f"[ConversationEngine] generate_cbt_response: "
            f"condition='{condition}'  level='{level}'  "
            f"lang='{lang}'  voice_dominant='{voice_dominant}'",
            flush=True,
        )

        template = select_template(
            condition,
            level,
            lang=lang,
            voice_dominant=voice_dominant,     
        )

        if template is None:
            print(
                f"[ConversationEngine] ⚠️  No template matched for "
                f"condition='{condition}' level='{level}' lang='{lang}'. "
                f"Check cbt_templates.json.",
                flush=True,
            )
            return None

        therapy = template["therapy"]
        print(
            f"[ConversationEngine] ✓ Template found. "
            f"steps={len(therapy.get('intervention_steps', []))}  "
            f"steps_alt={'yes' if therapy.get('steps_alt') else 'no'}  "
            f"prefer_alt={template.get('prefer_alt_steps', False)}",
            flush=True,
        )
        return {
            "validation":      therapy["validation"],
            "steps":           therapy["intervention_steps"],
            "steps_alt":       therapy.get("steps_alt"),
            "grounding":       therapy["grounding_statement"],
            "questions":       template["guided_questions"],
            "voice_dominant":  template.get("voice_dominant", voice_dominant),
            "prefer_alt_steps":template.get("prefer_alt_steps", False),
        }