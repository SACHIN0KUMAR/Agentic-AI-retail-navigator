from typing import Callable, Dict, Any, List, TypedDict, cast
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from impactify.graph.boss_agent import boss_decide
from impactify.graph.recommend_agent import recommendation_agent
from impactify.graph.stock_agent import stock_agent
from impactify.graph.promo_agent import promo_agent
from impactify.graph.pickup_agent import pickup_agent
from impactify.graph.payment_agent import payment_agent


class GraphState(TypedDict, total=False):
    messages: List[Any]
    last_user_message: str
    cart: List[Dict[str, Any]]
    store: Dict[str, Any]
    route: str
    done: bool


def _typed_agent(agent: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Callable[[GraphState], GraphState]:
    def run(state: GraphState) -> GraphState:
        return cast(GraphState, agent(cast(Dict[str, Any], state)))
    return run


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("BOSS", RunnableLambda(_typed_agent(boss_decide)))
    builder.add_node("RECOMMENDATION", RunnableLambda(_typed_agent(recommendation_agent)))
    builder.add_node("STOCK_CHECK", RunnableLambda(_typed_agent(stock_agent)))
    builder.add_node("PROMO", RunnableLambda(_typed_agent(promo_agent)))
    builder.add_node("PICKUP", RunnableLambda(_typed_agent(pickup_agent)))
    builder.add_node("PAYMENT", RunnableLambda(_typed_agent(payment_agent)))

    builder.set_entry_point("BOSS")

    def route_from_boss(state: Dict[str, Any]) -> str:
        return state.get("route", "END")

    builder.add_conditional_edges(
        "BOSS",
        route_from_boss,
        {
            "RECOMMENDATION": "RECOMMENDATION",
            "STOCK_CHECK": "STOCK_CHECK",
            "PROMO": "PROMO",
            "PICKUP": "PICKUP",
            "PAYMENT": "PAYMENT",
            "END": END,
        }
    )

    # ✅ Agents go to END, not back to BOSS
    # cli_app.py's while loop handles the next user turn
    builder.add_edge("RECOMMENDATION", END)
    builder.add_edge("STOCK_CHECK", END)
    builder.add_edge("PROMO", END)
    builder.add_edge("PICKUP", END)
    builder.add_edge("PAYMENT", END)

    return builder.compile()