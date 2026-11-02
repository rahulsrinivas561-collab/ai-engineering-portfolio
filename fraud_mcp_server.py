from fastmcp import FastMCP
import pandas as pd

# 1. Initialize the FastMCP server instance
mcp = FastMCP(name="Enterprise Fraud & Risk MCP Server")

# Mock database of risky transactions (simulating Snowflake/Swiggy risk logs)
TRANSACTION_DB = {
    "TXN_90412": {"user": 88402, "amount": 14500.0, "risk": "High", "reason": "Account Takeover / Unknown Device"},
    "TXN_90413": {"user": 33112, "amount": 3200.0, "risk": "Medium", "reason": "Unrecognized City Login"},
    "TXN_77102": {"user": 11920, "amount": 450.0, "risk": "Low", "reason": "Late Delivery Refund Request"}
}

# 2. Expose a Tool via MCP (@mcp.tool)
# FastMCP automatically uses docstrings and type hints to build the JSON schema for LLMs!
@mcp.tool()
def lookup_transaction_risk(transaction_id: str) -> dict:
    """
    Looks up a transaction ID in the enterprise risk database and returns risk details.
    """
    tx_id = transaction_id.upper().strip()
    if tx_id in TRANSACTION_DB:
        return {"transaction_id": tx_id, "status": "Found", "data": TRANSACTION_DB[tx_id]}
    else:
        return {"transaction_id": tx_id, "status": "Not Found", "data": {}}

# 3. Expose static or dynamic data as a Resource (@mcp.resource)
@mcp.resource("resource://risk_summary/metrics")
def get_risk_metrics() -> dict:
    """
    Provides high-level aggregate risk analytics for dashboards.
    """
    return {
        "total_audited_today": len(TRANSACTION_DB),
        "high_risk_count": sum(1 for v in TRANSACTION_DB.values() if v["risk"] == "High"),
        "system_status": "Operational"
    }

if __name__ == "__main__":
    # Run the MCP server over standard input/output (stdio) transport
    mcp.run()