"""
tools.py — Tool Definitions and Execution
==========================================

WHAT THIS FILE DOES:
    Defines the tools available to the Business X-Ray agent:
    1. TOOL_DEFINITIONS — JSON schemas the model uses to understand tools
    2. execute_tool()   — Dispatcher that routes tool calls to Python functions
    3. Tool functions   — The actual implementations (simulated data for now)

WHY SIMULATED DATA:
    Real APIs (QuickBooks, Xero, Stripe) require auth, sandbox setup, etc.
    We simulate realistic data so you can learn the agent loop mechanics first.
    Swap in real APIs incrementally without touching agent.py at all.
    This is the correct architecture — tools are an interface, not the core logic.

HOW TOOL DEFINITIONS WORK:
    The model reads these JSON schemas to know:
    - Tool name (must match execute_tool's routing)
    - Description (helps model decide WHEN to call this tool)
    - Parameters (what to pass, types, which are required)
    Think of it as an API contract between you and the model.

TO ADD A REAL API:
    1. Add the tool definition to TOOL_DEFINITIONS
    2. Add a case in execute_tool()
    3. Write the actual function (replace the simulated return)
    agent.py never changes.
"""

import json
from typing import Any


# =============================================================================
# TOOL DEFINITIONS — The schemas the model reads
# =============================================================================

TOOL_DEFINITIONS = [
    {
        "name": "get_revenue_data",
        "description": (
            "Retrieve monthly revenue data for a business client. "
            "Returns 12 months of revenue history, broken down by revenue type "
            "(recurring, project-based, one-time). Use this to assess growth trends "
            "and revenue concentration risk."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "The name of the business client",
                },
                "months": {
                    "type": "integer",
                    "description": "Number of months of history to retrieve (default: 12)",
                },
            },
            "required": ["client_name"],
        },
    },
    {
        "name": "get_expense_breakdown",
        "description": (
            "Retrieve expense data broken down by category for a business client. "
            "Returns total expenses, fixed vs variable split, and top expense categories. "
            "Use this to identify cost structure and potential red flags."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "The name of the business client",
                },
                "period": {
                    "type": "string",
                    "description": "Time period: 'last_month', 'last_quarter', 'last_year'",
                    "enum": ["last_month", "last_quarter", "last_year"],
                },
            },
            "required": ["client_name", "period"],
        },
    },
    {
        "name": "get_cash_flow_statement",
        "description": (
            "Retrieve the cash flow statement for a business client. "
            "Returns operating, investing, and financing cash flows, plus current "
            "cash balance and calculated runway. Critical for assessing liquidity."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "The name of the business client",
                },
            },
            "required": ["client_name"],
        },
    },
    {
        "name": "get_key_metrics",
        "description": (
            "Retrieve pre-calculated key financial metrics for a business client. "
            "Returns gross margin, net margin, burn rate, AR days, AP days, and "
            "customer concentration (top customer as % of revenue). "
            "Use this to quickly assess overall financial health."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "The name of the business client",
                },
            },
            "required": ["client_name"],
        },
    },
    {
        "name": "get_accounts_receivable",
        "description": (
            "Retrieve accounts receivable aging report for a business client. "
            "Shows outstanding invoices bucketed by age (current, 30, 60, 90+ days). "
            "Use this to identify collection issues and working capital risks."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "client_name": {
                    "type": "string",
                    "description": "The name of the business client",
                },
            },
            "required": ["client_name"],
        },
    },
]


# =============================================================================
# TOOL DISPATCHER — Routes tool calls to their implementations
# =============================================================================

def execute_tool(tool_name: str, tool_input: dict) -> Any:
    """
    Dispatch a tool call to the appropriate function.

    WHY THIS PATTERN:
        The agent loop calls this with whatever tool name and inputs the model requested.
        Centralizing dispatch here means agent.py stays clean and generic.
        New tools = add a case here + a function below. That's it.
    """
    dispatch = {
        "get_revenue_data": _get_revenue_data,
        "get_expense_breakdown": _get_expense_breakdown,
        "get_cash_flow_statement": _get_cash_flow_statement,
        "get_key_metrics": _get_key_metrics,
        "get_accounts_receivable": _get_accounts_receivable,
    }

    if tool_name not in dispatch:
        return {"error": f"Unknown tool: {tool_name}"}

    return dispatch[tool_name](**tool_input)


# =============================================================================
# TOOL IMPLEMENTATIONS — Simulated data (swap in real APIs here)
# =============================================================================

def _get_revenue_data(client_name: str, months: int = 12) -> dict:
    """
    Simulates 12 months of revenue data for Acme Manufacturing Co.
    Real version: query QuickBooks/Xero API for P&L by month.
    """
    # Simulated realistic data for a $3M/year manufacturing business
    monthly_revenue = [
        {"month": "Mar 2024", "recurring": 180000, "project": 45000, "one_time": 12000},
        {"month": "Apr 2024", "recurring": 182000, "project": 38000, "one_time": 5000},
        {"month": "May 2024", "recurring": 185000, "project": 52000, "one_time": 8000},
        {"month": "Jun 2024", "recurring": 188000, "project": 61000, "one_time": 0},
        {"month": "Jul 2024", "recurring": 190000, "project": 44000, "one_time": 15000},
        {"month": "Aug 2024", "recurring": 191000, "project": 39000, "one_time": 0},
        {"month": "Sep 2024", "recurring": 195000, "project": 58000, "one_time": 22000},
        {"month": "Oct 2024", "recurring": 197000, "project": 47000, "one_time": 0},
        {"month": "Nov 2024", "recurring": 198000, "project": 53000, "one_time": 0},
        {"month": "Dec 2024", "recurring": 195000, "project": 31000, "one_time": 35000},
        {"month": "Jan 2025", "recurring": 200000, "project": 42000, "one_time": 0},
        {"month": "Feb 2025", "recurring": 203000, "project": 55000, "one_time": 8000},
    ]

    # Return only as many months as requested
    data = monthly_revenue[-months:]

    # Calculate summary stats
    total = sum(m["recurring"] + m["project"] + m["one_time"] for m in data)
    avg_monthly = total / len(data)
    first_month = data[0]["recurring"] + data[0]["project"] + data[0]["one_time"]
    last_month = data[-1]["recurring"] + data[-1]["project"] + data[-1]["one_time"]
    growth_pct = ((last_month - first_month) / first_month) * 100

    return {
        "client": client_name,
        "months_returned": len(data),
        "monthly_detail": data,
        "summary": {
            "total_revenue_period": total,
            "avg_monthly_revenue": round(avg_monthly, 0),
            "latest_month_revenue": last_month,
            "revenue_growth_pct": round(growth_pct, 1),
            "recurring_pct_of_total": round(
                sum(m["recurring"] for m in data) / total * 100, 1
            ),
        },
    }


def _get_expense_breakdown(client_name: str, period: str = "last_quarter") -> dict:
    """
    Simulates expense data for Acme Manufacturing Co.
    Real version: query QuickBooks expense categories via API.
    """
    expenses = {
        "last_month": {
            "total_expenses": 218000,
            "fixed_expenses": 145000,
            "variable_expenses": 73000,
            "categories": {
                "cost_of_goods_sold": 118000,
                "salaries_benefits": 72000,
                "rent_utilities": 18000,
                "software_subscriptions": 8500,
                "marketing": 6500,
                "insurance": 5200,
                "professional_services": 4800,
                "travel_entertainment": 3200,
                "other": 1800,
            },
        },
        "last_quarter": {
            "total_expenses": 651000,
            "fixed_expenses": 435000,
            "variable_expenses": 216000,
            "categories": {
                "cost_of_goods_sold": 354000,
                "salaries_benefits": 216000,
                "rent_utilities": 54000,
                "software_subscriptions": 25500,
                "marketing": 19500,
                "insurance": 15600,
                "professional_services": 14400,
                "travel_entertainment": 9600,
                "other": 5400,
                # RED FLAG: unusual one-time items
                "equipment_repair_emergency": 14000,
            },
        },
        "last_year": {
            "total_expenses": 2580000,
            "fixed_expenses": 1720000,
            "variable_expenses": 860000,
            "categories": {
                "cost_of_goods_sold": 1404000,
                "salaries_benefits": 864000,
                "rent_utilities": 216000,
                "software_subscriptions": 102000,
                "marketing": 78000,
                "insurance": 62400,
                "professional_services": 57600,
                "travel_entertainment": 38400,
                "other": 21600,
                "equipment_repair_emergency": 14000,
            },
        },
    }

    data = expenses[period]
    return {
        "client": client_name,
        "period": period,
        **data,
        "flags": [
            "Emergency equipment repair ($14K) in last quarter — investigate root cause",
            "Software subscriptions ($8.5K/mo) may warrant audit for unused licenses",
        ],
    }


def _get_cash_flow_statement(client_name: str) -> dict:
    """
    Simulates a cash flow statement for Acme Manufacturing Co.
    Real version: pull from accounting software or build from bank feeds.
    """
    return {
        "client": client_name,
        "period": "Last 12 months",
        "operating_cash_flow": {
            "net_income": 280000,
            "depreciation_amortization": 42000,
            "changes_in_working_capital": -118000,  # Negative = working capital consuming cash
            "accounts_receivable_change": -95000,    # AR growing (cash tied up)
            "accounts_payable_change": 22000,
            "inventory_change": -45000,
            "total_operating_cf": 204000,
        },
        "investing_cash_flow": {
            "equipment_purchases": -85000,
            "total_investing_cf": -85000,
        },
        "financing_cash_flow": {
            "loan_repayments": -48000,
            "owner_distributions": -60000,
            "total_financing_cf": -108000,
        },
        "summary": {
            "net_cash_change": 11000,
            "beginning_cash": 187000,
            "ending_cash_balance": 198000,
            "monthly_burn_rate": 54333,        # Based on operating expenses
            "months_of_runway": 3.6,           # 198K / 54.3K — RED FLAG
            "free_cash_flow": 119000,          # Operating CF - Capex
        },
        "flags": [
            "CRITICAL: Only 3.6 months of runway — immediate attention required",
            "AR growth ($95K drag) suggests collection process needs tightening",
            "Owner distributions ($60K) during low-cash period is concerning",
        ],
    }


def _get_key_metrics(client_name: str) -> dict:
    """
    Simulates pre-calculated KPIs for Acme Manufacturing Co.
    Real version: calculate from P&L + Balance Sheet pulled from accounting API.
    """
    return {
        "client": client_name,
        "as_of": "February 2025",
        "profitability": {
            "gross_margin_pct": 41.2,      # Industry avg for manufacturing: 35-45%
            "net_margin_pct": 10.8,         # Decent but watch fixed cost leverage
            "ebitda_margin_pct": 14.3,
        },
        "liquidity": {
            "current_ratio": 1.4,           # Below 2.0 is worth watching
            "quick_ratio": 0.9,             # Below 1.0 = potential liquidity risk
            "cash_balance": 198000,
            "months_of_runway": 3.6,
        },
        "efficiency": {
            "ar_days": 52,                  # Target: <45. Collecting slowly.
            "ap_days": 31,                  # Paying faster than collecting
            "inventory_turns": 6.2,
        },
        "concentration_risk": {
            "top_customer_pct_revenue": 34, # >25% is a risk flag
            "top_3_customers_pct_revenue": 61,
            "top_customer_name": "BuildRight Corp",
        },
        "benchmarks": {
            "industry": "Manufacturing (SMB)",
            "gross_margin_benchmark": "35-45%",
            "ar_days_benchmark": "<45",
            "current_ratio_benchmark": ">2.0",
        },
    }


def _get_accounts_receivable(client_name: str) -> dict:
    """
    Simulates an AR aging report for Acme Manufacturing Co.
    Real version: pull aging report from QuickBooks via API.
    """
    return {
        "client": client_name,
        "as_of": "February 2025",
        "total_ar": 342000,
        "aging_buckets": {
            "current_0_30_days": {"amount": 168000, "pct": 49.1},
            "late_31_60_days":   {"amount": 89000,  "pct": 26.0},
            "late_61_90_days":   {"amount": 54000,  "pct": 15.8},
            "overdue_90_plus":   {"amount": 31000,  "pct": 9.1},
        },
        "top_overdue_accounts": [
            {"customer": "BuildRight Corp",  "amount": 18500, "days_outstanding": 97},
            {"customer": "Harbor Logistics", "amount": 9200,  "days_outstanding": 112},
            {"customer": "Apex Retail Inc",  "amount": 3300,  "days_outstanding": 94},
        ],
        "flags": [
            "$31K (9.1%) is 90+ days overdue — escalate collection immediately",
            "BuildRight Corp: $18.5K overdue despite being top revenue customer — leverage relationship carefully",
            "AR days of 52 vs AP days of 31 = negative cash conversion cycle gap",
        ],
    }
