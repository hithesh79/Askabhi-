"""Optional OpenAI-compatible phrasing adapter; offline mode remains the fallback."""
from __future__ import annotations
import json, os
from core.copilot.offline import answer as offline_answer
from core.copilot.guard import verify_numbers
from core.models import Answer

def _api_key() -> str | None:
    """Return the new AskAbhi key, with compatibility for the previous project key."""
    return os.environ.get("ASKABHI_LLM_API_KEY") or os.environ.get("KAVACH_LLM_API_KEY")

def available() -> bool:
    return bool(_api_key())

def answer_llm(question: str, session) -> Answer:
    """Use an optional LLM to phrase engine-backed results; send aggregates only.

    Raw transaction descriptions are never sent. The model is not the calculator.
    Any unsupported number causes the adapter to fall back to the offline answer.
    """
    baseline=offline_answer(question,session)
    if not available(): return baseline
    try:
        from openai import OpenAI
        client=OpenAI(api_key=_api_key())
        model=os.environ.get("ASKABHI_LLM_MODEL", os.environ.get("KAVACH_LLM_MODEL", "gpt-4.1-mini"))
        evidence={"verdict":baseline.verdict,"evidence":baseline.evidence,"actions":baseline.actions,"caveat":baseline.caveat}
        tools=[{"type":"function","function":{"name":"present_engine_result","description":"Restate only the supplied engine result without adding any numeric claim.","parameters":{"type":"object","properties":{"verdict":{"type":"string"},"evidence":{"type":"array","items":{"type":"string"}},"actions":{"type":"array","items":{"type":"string"}},"caveat":{"type":"string"}},"required":["verdict","evidence","actions","caveat"],"additionalProperties":False}}}]
        response=client.chat.completions.create(model=model,messages=[{"role":"system","content":"You are AskAbhi's financial copilot. The tested engine computes all numbers. You may only explain the supplied evidence and suggest educational options. Do not invent numbers, returns, financial product endorsements or guarantees. Never claim live bank access unless the supplied evidence says so."},{"role":"user","content":"Question: "+question+"\nAuthoritative calculation results (aggregates only): "+json.dumps(evidence,ensure_ascii=False)}],tools=tools,tool_choice={"type":"function","function":{"name":"present_engine_result"}},temperature=0)
        call=response.choices[0].message.tool_calls[0]
        data=json.loads(call.function.arguments)
        text=" ".join([data["verdict"]]+data["evidence"]+data["actions"]+[data["caveat"]])
        guard=verify_numbers(text,evidence)
        if not guard.valid:
            # One constrained regeneration attempt; if unsupported numbers remain, fall back.
            response=client.chat.completions.create(model=model,messages=[{"role":"system","content":"Regenerate the response using ONLY the supplied text and numbers. Add no numerical values."},{"role":"user","content":json.dumps(evidence,ensure_ascii=False)}],tools=tools,tool_choice={"type":"function","function":{"name":"present_engine_result"}},temperature=0)
            data=json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            text=" ".join([data["verdict"]]+data["evidence"]+data["actions"]+[data["caveat"]]); guard=verify_numbers(text,evidence)
        if not guard.valid: return baseline
        return Answer(data["verdict"],data["evidence"],data["actions"],data["caveat"],baseline.tool_results,True,"OpenAI phrasing; engine-verified numbers")
    except Exception:
        return baseline
