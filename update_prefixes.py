import asyncio
import aiohttp
import ipaddress
import sys

ASN_URL = "https://ftp.ripe.net/ripe/asnames/asn.txt"
PREFIX_API_URL = "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{}"

async def fetch_ru_asns(session):
    """Скачивает список AS и фильтрует только российские (RU)"""
    async with session.get(ASN_URL) as response:
        text = await response.text()
        asns = []
        for line in text.splitlines():
            line = line.strip()
            if line.endswith(", RU"):
                parts = line.split()
                if parts:
                    asn = parts[0]
                    if asn.isdigit():
                        asns.append(asn)
        return asns

async def fetch_prefixes(session, asn, semaphore, retries=3):
    """Получает анонсируемые префиксы для конкретной AS с повторными попытками (ретраями)"""
    async with semaphore:
        url = PREFIX_API_URL.format(asn)
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        prefixes = []
                        for p in data.get('data', {}).get('prefixes', []):
                            prefixes.append(p['prefix'])
                        return prefixes
                    else:
                        await asyncio.sleep(1)
            except Exception as e:
                if attempt == retries - 1:
                    print(f"Ошибка при получении AS{asn}: {e}", file=sys.stderr)
                else:
                    await asyncio.sleep(1)
        return []

async def main():
    connector = aiohttp.TCPConnector(limit_per_host=30)
    async with aiohttp.ClientSession(connector=connector) as session:
        print("Скачивание списка RU AS...")
        ru_asns = await fetch_ru_asns(session)
        print(f"Найдено автономных систем (RU): {len(ru_asns)}")

        semaphore = asyncio.Semaphore(40)
        tasks = [fetch_prefixes(session, asn, semaphore) for asn in ru_asns]

        print("Запрос префиксов для всех AS (это займет пару минут)...")
        results = await asyncio.gather(*tasks)

        ipv4_nets = []
        ipv6_nets = []

        for prefixes in results:
            for prefix in prefixes:
                try:
                    net = ipaddress.ip_network(prefix, strict=False)
                    if net.version == 4:
                        ipv4_nets.append(net)
                    else:
                        ipv6_nets.append(net)
                except ValueError:
                    pass

        print("Суммаризация (схлопывание) префиксов...")
        collapsed_v4 = list(ipaddress.collapse_addresses(ipv4_nets))
        collapsed_v6 = list(ipaddress.collapse_addresses(ipv6_nets))

        print(f"Итого IPv4 префиксов после суммаризации: {len(collapsed_v4)}")
        print(f"Итого IPv6 префиксов после суммаризации: {len(collapsed_v6)}")

        with open("ipv4_ru.txt", "w") as f:
            for net in collapsed_v4:
                f.write(f"{net}\n")

        with open("ipv6_ru.txt", "w") as f:
            for net in collapsed_v6:
                f.write(f"{net}\n")
                
        print("Готово! Результаты сохранены в ipv4_ru.txt и ipv6_ru.txt")

if __name__ == "__main__":
    asyncio.run(main())
