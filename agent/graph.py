# agent/graph.py

from langgraph.graph import StateGraph, END

from agent.state import ClaimState
from agent.router import (
route_after_privacy,
route_after_extraction,
route_after_policy,
route_after_clinical,
route_after_tariff,
route_after_calculation,
route_after_fraud,
route_after_adjudication,
)

from agent.nodes.intake import intake_node
from agent.nodes.privacy import privacy_node
from agent.nodes.extraction import extraction_node
from agent.nodes.memory import memory_node
from agent.nodes.policy import policy_node
from agent.nodes.clinical import clinical_node
from agent.nodes.tariff import tariff_node
from agent.nodes.calculation import calculation_node
from agent.nodes.fraud import fraud_node
from agent.nodes.adjudication import adjudication_node
from agent.nodes.finalization import finalization_node

workflow = StateGraph(ClaimState)

# =========================================================

# NODES

# =========================================================

workflow.add_node("intake", intake_node)
workflow.add_node("privacy", privacy_node)
workflow.add_node("extraction", extraction_node)
workflow.add_node("memory", memory_node)
workflow.add_node("policy", policy_node)
workflow.add_node("clinical", clinical_node)
workflow.add_node("tariff", tariff_node)
workflow.add_node("calculation", calculation_node)
workflow.add_node("fraud", fraud_node)
workflow.add_node("adjudication", adjudication_node)
workflow.add_node("finalization", finalization_node)

# =========================================================

# ENTRY POINT

# =========================================================

workflow.set_entry_point("intake")

# =========================================================

# INTAKE -> PRIVACY

# =========================================================

workflow.add_edge(
"intake",
"privacy",
)

# =========================================================

# PRIVACY -> EXTRACTION / ERROR

# =========================================================

workflow.add_conditional_edges(
"privacy",
route_after_privacy,
{
"extraction": "extraction",
"error": END,
},
)

# =========================================================

# EXTRACTION -> MEMORY / POLICY / ERROR

# =========================================================

workflow.add_conditional_edges(
"extraction",
route_after_extraction,
{
"memory": "memory",
"policy": "policy",
"error": END,
},
)

# =========================================================

# MEMORY -> POLICY

# =========================================================

workflow.add_edge(
"memory",
"policy",
)

# =========================================================

# POLICY -> CLINICAL / ERROR

# =========================================================

workflow.add_conditional_edges(
"policy",
route_after_policy,
{
"clinical": "clinical",
"error": END,
},
)

# =========================================================

# CLINICAL -> TARIFF / ADJUDICATION / ERROR

# =========================================================

workflow.add_conditional_edges(
"clinical",
route_after_clinical,
{
"tariff": "tariff",
"adjudication": "adjudication",
"error": END,
},
)

# =========================================================

# TARIFF -> CALCULATION / ERROR

# =========================================================

workflow.add_conditional_edges(
"tariff",
route_after_tariff,
{
"calculation": "calculation",
"error": END,
},
)

# =========================================================

# CALCULATION -> FRAUD / ERROR

# =========================================================

workflow.add_conditional_edges(
"calculation",
route_after_calculation,
{
"fraud": "fraud",
"error": END,
},
)

# =========================================================

# FRAUD -> ADJUDICATION / ERROR

# =========================================================

workflow.add_conditional_edges(
"fraud",
route_after_fraud,
{
"adjudication": "adjudication",
"error": END,
},
)

# =========================================================

# ADJUDICATION -> FINALIZATION / ERROR

# =========================================================

workflow.add_conditional_edges(
"adjudication",
route_after_adjudication,
{
"finalization": "finalization",
"error": END,
},
)

# =========================================================

# FINALIZATION -> END

# =========================================================

workflow.add_edge(
"finalization",
END,
)

# =========================================================

# COMPILE GRAPH

# =========================================================

claim_guard_graph = workflow.compile()
