import asyncio
import httpx
import re
from typing import Optional, Tuple

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

async def resolve_and_validate_url(raw_url: str, timeout: float = 6.0) -> Tuple[bool, str]:
    """
    Segue redirects (incluindo vertexaisearch e encurtadores) e valida se a URL final responde 200/300.
    Retorna (is_valid, final_url).
    """
    if not raw_url or not raw_url.startswith("http"):
        return False, raw_url

    headers = {"User-Agent": USER_AGENT}
    
    # 1. Tenta HEAD primeiro
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, verify=False) as client:
            resp = await client.head(raw_url, headers=headers)
            if resp.status_code < 400:
                return True, str(resp.url)
    except Exception:
        pass

    # 2. Se HEAD falhar (alguns servidores bloqueiam HEAD com 403/405), tenta GET leve com stream
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout, verify=False) as client:
            async with client.stream("GET", raw_url, headers=headers) as resp:
                if resp.status_code < 400:
                    return True, str(resp.url)
    except Exception:
        pass

    return False, raw_url

async def validate_sources_dict(sources: list[dict]) -> list[dict]:
    """
    Recebe lista de dicts [{'id': 1, 'title': '...', 'url': '...'}]
    Testa em paralelo e filtra apenas as fontes com links 100% verificados.
    """
    tasks = [resolve_and_validate_url(s.get("url", "")) for s in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    verified = []
    for s, res in zip(sources, results):
        if isinstance(res, tuple):
            is_valid, final_url = res
            if is_valid:
                s_copy = dict(s)
                s_copy["url"] = final_url
                verified.append(s_copy)
            else:
                print(f"⚠️ [LinkValidator Descartou Link Morto]: {s.get('url')} (Status Inválido)")
    return verified
