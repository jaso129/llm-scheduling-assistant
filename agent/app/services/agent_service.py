import uuid
from typing import Optional

from app.schemas.agent import AgentRunRequest, AgentRunResponse, EventDraft
from app.llm.planner import make_plan
from app.utils.idempotency import build_idempotency_key
from app.utils.time_guard import missing_time
from app.tools import event_client


def run_agent(req: AgentRunRequest, request_id: Optional[str]) -> AgentRunResponse:
    trace_id = request_id or str(uuid.uuid4())

    plan = make_plan(req.user_text)
    event_id = req.event_id or plan.event_id

    # 合併 client override（第二次補欄位/時間、或 UI 提供 event_id）
    merged_event = None
    if plan.event is not None:
        merged_event = EventDraft(
            title=req.title if req.title is not None else plan.event.title,
            notes=req.notes if req.notes is not None else plan.event.notes,
            startDate=req.startDate if req.startDate is not None else plan.event.startDate,
            endDate=req.endDate if req.endDate is not None else plan.event.endDate,
        )

    # LLM 直接說需要釐清：不執行
    if plan.need_clarification:
        return AgentRunResponse(
            trace_id=trace_id,
            action=plan.action,
            need_clarification=True,
            questions=plan.questions,
            draft=merged_event,
        )

    # confirm=false：只回 plan/draft，不做 side effect
    if not req.confirm:
        # 需要 event_id 的動作
        if plan.action in ("get_event", "update_event", "delete_event", "retry_notion_sync") and not event_id:
            return AgentRunResponse(
                trace_id=trace_id,
                action=plan.action,
                need_clarification=True,
                questions=["Please provide event_id (or select an event) then set confirm=true."],
                draft=merged_event,
            )
        # create/update 缺時間
        if plan.action in ("create_event", "update_event") and merged_event and missing_time(merged_event.startDate, merged_event.endDate):
            return AgentRunResponse(
                trace_id=trace_id,
                action=plan.action,
                need_clarification=True,
                questions=["startDate/endDate is missing. Provide them then set confirm=true."],
                draft=merged_event,
            )

        return AgentRunResponse(
            trace_id=trace_id,
            action=plan.action,
            need_clarification=False,
            draft=merged_event,
        )

    # confirm=true：要執行 tool call
    action = plan.action
    idem = req.idempotency_key or build_idempotency_key(
        user_text=req.user_text,
        action=action,
        event_id=event_id,
        start=merged_event.startDate if merged_event else None,
        end=merged_event.endDate if merged_event else None,
    )

    if action == "create_event":
        if not merged_event:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Missing event payload. Please rephrase your request."])
        if missing_time(merged_event.startDate, merged_event.endDate):
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["startDate/endDate is missing. Provide them then confirm again."],
                                    draft=merged_event)
        code, data = event_client.create_event(merged_event, idem)
        return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=False,
                                draft=merged_event, backend_status_code=code, backend_response=data)

    if action == "get_event":
        if not event_id:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Please provide event_id then confirm again."])
        code, data = event_client.get_event(event_id)
        return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=False,
                                backend_status_code=code, backend_response=data)

    if action == "update_event":
        if not event_id:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Please provide event_id then confirm again."], draft=merged_event)
        if not merged_event:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Missing event payload for update. Please specify what to change."])
        code, data = event_client.update_event(event_id, merged_event, idem)
        return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=False,
                                draft=merged_event, backend_status_code=code, backend_response=data)

    if action == "delete_event":
        if not event_id:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Please provide event_id then confirm again."])
        code, data = event_client.delete_event(event_id, idem)
        return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=False,
                                backend_status_code=code, backend_response=data)

    if action == "retry_notion_sync":
        if not event_id:
            return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=True,
                                    questions=["Please provide event_id then confirm again."])
        code, data = event_client.retry_notion_sync(event_id, idem)
        return AgentRunResponse(trace_id=trace_id, action=action, need_clarification=False,
                                backend_status_code=code, backend_response=data)

    # none
    return AgentRunResponse(
        trace_id=trace_id,
        action="none",
        need_clarification=False,
        backend_response={"message": "No backend action needed."},
    )