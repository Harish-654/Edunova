import httpx

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; EduNovaBot/1.0; +https://github.com/Harish-654/Edunova)"
}


async def fetch_page(url: str, timeout: float = 12.0) -> str:
    async with httpx.AsyncClient(
        timeout=timeout, follow_redirects=True, headers=REQUEST_HEADERS
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
