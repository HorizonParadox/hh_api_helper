import re
from dateutil import parser as dt_parser
from datetime import timezone


def strip_html_tags(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text).strip()


def keep_only_latin_words_and_digits(text: str) -> str:
    # Находим все латинские слова и числа длиной от 3 символов и больше
    words = re.findall(r'[a-zA-Z0-9]{3,}', text)

    # Исключаем слово "strong" (игнорируем регистр) и числа длиной 3 или более цифр
    words = [
        word for word in words
        if word.lower() != 'strong' and word.lower() != 'div' and
           word.lower() != 'quot' and word.lower() != 'title' and
           word.lower != 'span' and not word.isdigit() or len(word) < 3
    ]

    # Возвращаем строку с пробелами между словами
    return ' '.join(words)


def parse_salary(salary_data: dict | None) -> int | None:
    if not salary_data:
        return None

    currency = salary_data.get("currency", "RUR")
    if currency not in ("RUR", "RUB"):
        return None

    def extract_digits(value):
        if isinstance(value, str):
            digits = re.sub(r"[^\d]", "", value)
            return int(digits) if digits else None
        elif isinstance(value, (int, float)):
            return int(value)
        return None

    _from = extract_digits(salary_data.get("from"))
    _to = extract_digits(salary_data.get("to"))

    if _from and _to:
        return (_from + _to) // 2
    elif _from:
        return _from
    elif _to:
        return _to

    return None


def get_datetime_type(published_at):
    dt = dt_parser.isoparse(published_at)
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
