"""Indodax MCP Server
This server exposes Indodax private REST API methods as MCP tools so that
agents can call them easily.

All methods listed in the official documentation for the `method` parameter are
implemented:
    - getInfo
    - transHistory
    - trade
    - tradeHistory
    - openOrders
    - orderHistory
    - getOrder
    - getOrderByClientOrderId
    - cancelOrder
    - cancelByClientOrderId
    - withdrawFee
    - withdrawCoin
    - listDownline
    - checkDownline
    - createVoucher

Environment Variables (see .env):
    INDODAX_API_KEY    Your API key
    INDODAX_API_SECRET Your API secret (HMAC-SHA512 signing key)

Note:  The Indodax private API is available ONLY via HTTPS POST to the single
endpoint https://indodax.com/tapi.  Authentication is performed by sending
headers:
    Key  -> API key
    Sign -> HMAC-SHA512 signature of the request body using the secret key.

The FastMCP server makes each private request asynchronously using httpx.
"""
from __future__ import annotations

import hmac
import hashlib
import os
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Environment & global initialisation
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY: str | None = os.getenv("INDODAX_API_KEY")
# Allow legacy variable name INDODAX_SECRET_KEY as fallback
API_SECRET: str | None = os.getenv("INDODAX_API_SECRET") or os.getenv("INDODAX_SECRET_KEY")

if not API_KEY or not API_SECRET:
    raise RuntimeError(
        "Please set INDODAX_API_KEY and INDODAX_API_SECRET (or INDODAX_SECRET_KEY) in environment or .env file"
    )

INDODAX_API_URL = "https://indodax.com/tapi"

mcp = FastMCP("indodax")

# ---------------------------------------------------------------------------
# HTTP utility
# ---------------------------------------------------------------------------

async def _private_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send a signed POST request to Indodax private endpoint and return JSON.

    The function automatically fills `timestamp` (epoch in ms) when `nonce` is
    not supplied by the caller.
    """
    if "timestamp" not in payload and "nonce" not in payload:
        # millisecond timestamp, compatible with docs default recv window
        from time import time
        payload["timestamp"] = int(time() * 1000)

    body = urlencode(payload)
    sign = hmac.new(API_SECRET.encode(), body.encode(), hashlib.sha512).hexdigest()

    headers = {
        "Key": API_KEY,
        "Sign": sign,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(INDODAX_API_URL, headers=headers, data=body)
        response.raise_for_status()
        return response.json()

# ---------------------------------------------------------------------------
# Public REST API tools (no auth required)
# ---------------------------------------------------------------------------

PUBLIC_API_BASE = "https://indodax.com/api"

async def _public_get(path: str) -> Dict[str, Any]:
    url = f"{PUBLIC_API_BASE}/{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

@mcp.tool()
async def server_time() -> Dict[str, Any]:
    """Get server time (public endpoint)."""
    return await _public_get("server_time")

@mcp.tool()
async def pairs() -> list[Dict[str, Any]]:
    """Get list of available trading pairs."""
    return await _public_get("pairs")

@mcp.tool()
async def price_increments() -> Dict[str, Any]:
    """Get price increments per pair."""
    return await _public_get("price_increments")

@mcp.tool()
async def summaries() -> Dict[str, Any]:
    """Get summaries for all pairs."""
    return await _public_get("summaries")

@mcp.tool()
async def ticker(pair_id: str | None = None) -> Dict[str, Any]:
    """Get ticker for a pair (default btcidr)."""
    path = f"ticker/{pair_id}" if pair_id else "ticker"
    return await _public_get(path)

@mcp.tool()
async def ticker_all() -> Dict[str, Any]:
    """Get ticker for all pairs."""
    return await _public_get("ticker_all")

@mcp.tool()
async def trades(pair_id: str | None = None) -> list[Dict[str, Any]]:
    """Get recent trades for pair (default btcidr)."""
    path = f"trades/{pair_id}" if pair_id else "trades"
    return await _public_get(path)

# ---------------------------------------------------------------------------
# MCP tools – one per documented method parameter
# ---------------------------------------------------------------------------

@mcp.tool()
async def get_info() -> Dict[str, Any]:
    """Get user balances, server time, addresses etc. Equivalent to `getInfo`."""
    return await _private_post({"method": "getInfo"})


@mcp.tool()
async def trans_history(start: Optional[str] = None, end: Optional[str] = None) -> Dict[str, Any]:
    """Fetch transaction history between two dates (YYYY-MM-DD).

    Defaults to the last 7 days when no dates specified (server behaviour).
    """
    payload: Dict[str, Any] = {"method": "transHistory"}
    if start:
        payload["start"] = start
    if end:
        payload["end"] = end
    return await _private_post(payload)


@mcp.tool()
async def trade(pair: str, type: str, price: float, idr: Optional[float] = None, crypto: Optional[float] = None) -> Dict[str, Any]:
    """Create a buy/sell order.

    Args:
        pair: Trading pair, e.g. "btc_idr".
        type: "buy" or "sell".
        price: Price per unit.
        idr: Amount in IDR (for buy orders).
        crypto: Amount in crypto (for sell orders).
    """
    payload: Dict[str, Any] = {
        "method": "trade",
        "pair": pair,
        "type": type,
        "price": price,
    }
    if idr is not None:
        payload["idr"] = idr
    if crypto is not None:
        payload["crypto"] = crypto
    return await _private_post(payload)


@mcp.tool()
async def trade_history(pair: Optional[str] = None, count: int = 100, from_id: Optional[int] = None, end_id: Optional[int] = None, order: str = "desc") -> Dict[str, Any]:
    """Get historical trades.

    Args:
        pair: Optional pair filter.
        count: Max records (default 100).
        from_id: Start ID.
        end_id: End ID.
        order: "asc" or "desc".
    """
    payload: Dict[str, Any] = {
        "method": "tradeHistory",
        "count": count,
        "order": order,
    }
    if pair:
        payload["pair"] = pair
    if from_id is not None:
        payload["from"] = from_id
    if end_id is not None:
        payload["end"] = end_id
    return await _private_post(payload)


@mcp.tool()
async def open_orders(pair: Optional[str] = None) -> Dict[str, Any]:
    """Get open orders. Optionally filter by pair."""
    payload: Dict[str, Any] = {"method": "openOrders"}
    if pair:
        payload["pair"] = pair
    return await _private_post(payload)


@mcp.tool()
async def order_history(pair: Optional[str] = None, count: int = 100, from_id: Optional[int] = None, end_id: Optional[int] = None, order: str = "desc") -> Dict[str, Any]:
    """Fetch order history."""
    payload: Dict[str, Any] = {
        "method": "orderHistory",
        "count": count,
        "order": order,
    }
    if pair:
        payload["pair"] = pair
    if from_id is not None:
        payload["from"] = from_id
    if end_id is not None:
        payload["end"] = end_id
    return await _private_post(payload)


@mcp.tool()
async def get_order(order_id: int) -> Dict[str, Any]:
    """Get order by its numeric ID."""
    return await _private_post({"method": "getOrder", "order_id": order_id})


@mcp.tool()
async def get_order_by_client_order_id(client_order_id: str) -> Dict[str, Any]:
    """Get order by client generated ID."""
    return await _private_post({"method": "getOrderByClientOrderId", "client_order_id": client_order_id})


@mcp.tool()
async def cancel_order(order_id: int) -> Dict[str, Any]:
    """Cancel order by numeric ID."""
    return await _private_post({"method": "cancelOrder", "order_id": order_id})


@mcp.tool()
async def cancel_by_client_order_id(client_order_id: str) -> Dict[str, Any]:
    """Cancel order by client order ID."""
    return await _private_post({"method": "cancelByClientOrderId", "client_order_id": client_order_id})


@mcp.tool()
async def withdraw_fee(currency: str, amount: float, address: str, network: Optional[str] = None) -> Dict[str, Any]:
    """Estimate withdrawal fee.

    Args:
        currency: e.g. "btc".
        amount: Amount of coin.
        address: Destination address.
        network: Optional network code (e.g. "erc20").
    """
    payload: Dict[str, Any] = {
        "method": "withdrawFee",
        "currency": currency,
        "amount": amount,
        "address": address,
    }
    if network:
        payload["network"] = network
    return await _private_post(payload)


@mcp.tool()
async def withdraw_coin(currency: str, amount: float, address: str, network: Optional[str] = None, memo: Optional[str] = None) -> Dict[str, Any]:
    """Perform a crypto withdrawal."""
    payload: Dict[str, Any] = {
        "method": "withdrawCoin",
        "currency": currency,
        "amount": amount,
        "address": address,
    }
    if network:
        payload["network"] = network
    if memo:
        payload["memo"] = memo
    return await _private_post(payload)


@mcp.tool()
async def list_downline() -> Dict[str, Any]:
    """List referral downlines (Partner only)."""
    return await _private_post({"method": "listDownline"})


@mcp.tool()
async def check_downline(username: str) -> Dict[str, Any]:
    """Check whether a username is your downline."""
    return await _private_post({"method": "checkDownline", "username": username})


@mcp.tool()
async def create_voucher(amount: float, description: str | None = None) -> Dict[str, Any]:
    """Create a voucher (Partner only)."""
    payload: Dict[str, Any] = {"method": "createVoucher", "amount": amount}
    if description:
        payload["description"] = description
    return await _private_post(payload)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Run over stdio so that it works nicely with agents expecting MCP transport.
    mcp.run(transport="stdio")
