from langgraph.graph import StateGraph, END
from langgraph_graph.state_schema import GraphState
from langgraph_graph.nodes import vectorSearch_node, SQLSearch_node, scoreCalc_node, explain_node

# 3) LangGraph 그래프 빌드 함수 정의
def build_langgraph():
    graph = StateGraph(GraphState)
    
    graph.add_node("VectorSearch", vectorSearch_node)
    graph.add_node("SQLSearch", SQLSearch_node)
    graph.add_node("ScoreCalc", scoreCalc_node)
    graph.add_node("Explain", explain_node)

    graph.set_entry_point("VectorSearch")   # 첫 시작 노드
    graph.add_edge("VectorSearch", "SQLSearch")
    graph.add_edge( "SQLSearch", "ScoreCalc")
    graph.add_edge("ScoreCalc", "Explain")
    graph.add_edge("Explain", END)

    return graph.compile()