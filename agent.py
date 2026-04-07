import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from tools import search_flights, search_hotels, calculate_budget
from dotenv import load_dotenv

load_dotenv() 

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
tools_list = [search_flights, search_hotels, calculate_budget]
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in environment variables.")

llm = ChatGoogleGenerativeAI(
    model=gemini_model,
    temperature=float(os.getenv("TEMPERATURE", 0.2)),
    top_p=float(os.getenv("TOP_P", 0.6)),
    google_api_key=gemini_api_key,
)
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node và logging tool calls
def agent_node(state: AgentState):
    messages = state["messages"]
    if not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"Gọi tool: {tc['name']}({tc['args']})")
    else :
        print(f"Trả lời trực tiếp: ")
    return {"messages": [response]}

# 5. Xây dựng Graph 
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))

# TODO: Khai báo edges
builder.add_edge(START, "agent") # Bắt đầu tại agent
builder.add_conditional_edges("agent", tools_condition) # Nếu gọi tool thì sang tools, không thì END
builder.add_edge("tools", "agent") # Sau khi dùng tool, quay lại agent để suy nghĩ tiếp 

graph = builder.compile()

# 6. Chat loop
if __name__ == "__main__":
    # Lưu lịch sử hội thoại trong phiên chạy hiện tại.
    conversation_messages = []
    max_history_messages = 20

    print("=" * 60)
    print("TravelBuddy - Trợ lý Du lịch Thông minh")
    print("Gõ 'quit' để thoát")
    print("=" * 60)
    
    while True:
        user_input = input("\nBạn: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
            
        print("\nTravelBuddy đang suy nghĩ...")
        conversation_messages.append(("human", user_input))

        # Chỉ giữ một phần lịch sử gần nhất để tránh prompt quá dài.
        context_messages = conversation_messages[-max_history_messages:]
        result = graph.invoke({"messages": context_messages})
        conversation_messages = result["messages"]

        final_msg = result["messages"][-1]
        print(f"\nTravelBuddy: {final_msg.content}")