# ui/cli_app.py
# pyright: reportGeneralTypeIssues=false, reportArgumentType=false
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
from impactify.graph.graph import build_graph
class ImpactifyCliApp:
    def __init__(self, user_id: str = "user_1", pincode: str = "110001"):
        self.graph = build_graph()
        self.state: Dict[str, Any] = {
            "messages": [],
            "cart": [],
            "user_profile": {"user_id": user_id, "pincode": pincode},
            "store": {"id": "store_1"},
            "route": "BOSS",
            "done": False,
        }

    def run(self):
        print("🤖 Impactify Retail Navigator (Type 'exit' to quit)")
        print("Tell me what you want to buy today:")

        while not self.state.get("done", False):
            user_input = input("👤 You: ")
            if user_input.lower().strip() in {"exit", "quit"}:
                print("👋 Ending session. Goodbye!")
                break

            # Record user message
            self.state.setdefault("messages", []).append(
                HumanMessage(content=user_input)
            )
            self.state["last_user_message"] = user_input

            # ---- RUN GRAPH ----
            updated_state = self.graph.invoke(self.state.copy())

            # Normalize (sometimes graph returns tuple)
            if isinstance(updated_state, tuple):
                updated_state = updated_state[0]

            self.state = updated_state

            # Print last bot message
            messages: List = self.state.get("messages", [])
            if messages and isinstance(messages[-1], AIMessage):
                print(f"🤖 Bot: {messages[-1].content}")

            # End the flow
            if self.state.get("done", False):
                print("✅ Order complete. Thank you for shopping with Impactify!")
                break
if __name__ == "__main__":
    app = ImpactifyCliApp()
    app.run()
