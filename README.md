# RU ASN Prefixes Aggregator

Автоматический сбор и суммаризация префиксов российских (RU) автономных систем.

Скрипт ежедневно скачивает список RU AS из RIPE, опрашивает RIPE Stat API для получения анонсируемых префиксов и объединяет их в минимальные CIDR-списки для IPv4 и IPv6.

## Результаты

Списки префиксов доступны по прямым ссылкам:

- [ipv4_ru.txt](https://raw.githubusercontent.com/mrixs/ru_asn_prefixes/master/ipv4_ru.txt)
- [ipv6_ru.txt](https://raw.githubusercontent.com/mrixs/ru_asn_prefixes/master/ipv6_ru.txt)

## Как это работает

1. **GitHub Actions**: Скрипт запускается автоматически раз в сутки (в 02:00 UTC).
2. **Асинхронность**: Используется `aiohttp` для быстрого параллельного опроса RIPE API.
3. **Суммаризация**: Используется стандартная библиотека `ipaddress` для схлопывания (collapse) подсетей.

## Использование локально

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите скрипт:
   ```bash
   python update_prefixes.py
   ```

## Лицензия

[WTFPL](LICENSE) — делайте что хотите.
