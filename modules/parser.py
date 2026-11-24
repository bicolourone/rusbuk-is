"""
Модуль 1: Парсер сайта Rusbuk.ru
Букинистический магазин — https://rusbuk.ru
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import time
import re


BASE_URL = "https://rusbuk.ru"

# Популярные разделы каталога для парсинга
CATALOG_URLS = [
    "https://rusbuk.ru/catalog/detskaa_literatura_s1620s",          # Детская литература
    "https://rusbuk.ru/catalog/biografii_memuary_s1268s",            # Биографии
    "https://rusbuk.ru/catalog/istoriias",                           # История
    "https://rusbuk.ru/catalog/hudozhestvennaa_literatura_s3248s",   # Художественная
]


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    }


def parse_page(url: str) -> List[Dict]:
    """Пытается спарсить одну страницу каталога Rusbuk"""
    books = []
    try:
        response = requests.get(url, headers=get_headers(), timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or "utf-8"
    except requests.RequestException as e:
        print(f"Ошибка запроса {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "lxml")

    # Пробуем разные возможные селекторы карточек товаров
    # (структура сайта может меняться — селекторы легко поправить)
    candidates = (
        soup.select("div.product") or
        soup.select("div.item") or
        soup.select("div.goods-item") or
        soup.select("div.catalog-item") or
        soup.select("article") or
        soup.select("div[class*='product']") or
        soup.select("div[class*='item']") or
        soup.select("li.product") or
        []
    )

    for block in candidates:
        title_el = (
            block.select_one("a.product-title") or
            block.select_one(".title a") or
            block.select_one("h3 a") or
            block.select_one("h2 a") or
            block.select_one("a[href*='/product']") or
            block.select_one("a")
        )
        price_el = (
            block.select_one(".price") or
            block.select_one(".product-price") or
            block.select_one("[class*='price']")
        )
        author_el = (
            block.select_one(".author") or
            block.select_one("[class*='author']")
        )

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        if not title or len(title) < 3:
            continue

        href = title_el.get("href", "")
        if href and not href.startswith("http"):
            href = BASE_URL + href

        price = price_el.get_text(strip=True) if price_el else ""
        # Очищаем цену от лишних символов
        price = re.sub(r"\s+", " ", price)

        author = author_el.get_text(strip=True) if author_el else ""

        books.append({
            "title": title,
            "author": author,
            "price": price,
            "category": "",
            "url": href,
            "source": "rusbuk.ru"
        })

    return books


def get_demo_books() -> List[Dict]:
    """
    Демонстрационные данные на случай, если сайт недоступен
    или структура HTML изменилась.
    Нужны, чтобы система работала на защите.
    """
    return [
        {"title": "Мастер и Маргарита", "author": "М.А. Булгаков", "price": "850 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Война и мир (том 1)", "author": "Л.Н. Толстой", "price": "1200 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Преступление и наказание", "author": "Ф.М. Достоевский", "price": "650 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Анна Каренина", "author": "Л.Н. Толстой", "price": "980 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Идиот", "author": "Ф.М. Достоевский", "price": "720 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Тихий Дон (книга 1)", "author": "М.А. Шолохов", "price": "1100 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Евгений Онегин", "author": "А.С. Пушкин", "price": "450 ₽", "category": "Поэзия", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Герой нашего времени", "author": "М.Ю. Лермонтов", "price": "380 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Мёртвые души", "author": "Н.В. Гоголь", "price": "520 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Отцы и дети", "author": "И.С. Тургенев", "price": "410 ₽", "category": "Художественная литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Жизнь замечательных людей: Пушкин", "author": "Разные авторы", "price": "1500 ₽", "category": "Биографии. Мемуары", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "История России с древнейших времён", "author": "С.М. Соловьёв", "price": "2300 ₽", "category": "История", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Детские сказки", "author": "А.С. Пушкин", "price": "290 ₽", "category": "Детская литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Конек-Горбунок", "author": "П.П. Ершов", "price": "320 ₽", "category": "Детская литература", "url": "https://rusbuk.ru/", "source": "demo"},
        {"title": "Воспоминания", "author": "А.И. Герцен", "price": "780 ₽", "category": "Биографии. Мемуары", "url": "https://rusbuk.ru/", "source": "demo"},
    ]


def run_parser(max_pages: int = 2, use_demo_if_fail: bool = True) -> Dict:
    """
    Главная функция парсера.
    Пытается спарсить реальный сайт. Если не получается — использует демо-данные.
    """
    from modules.database import init_db, save_books

    init_db()
    all_books = []

    print("Пытаемся парсить Rusbuk.ru...")
    for i, url in enumerate(CATALOG_URLS[:max_pages]):
        print(f"  Страница {i+1}: {url}")
        books = parse_page(url)
        all_books.extend(books)
        time.sleep(1)  # вежливая задержка

    if not all_books and use_demo_if_fail:
        print("Реальный парсинг не дал результатов. Загружаем демо-данные.")
        all_books = get_demo_books()

    saved = save_books(all_books)

    return {
        "found": len(all_books),
        "saved": saved,
        "message": f"Найдено {len(all_books)} книг, сохранено новых: {saved}",
        "is_demo": all_books and all_books[0].get("source") == "demo"
    }


if __name__ == "__main__":
    result = run_parser(max_pages=2)
    print(result["message"])
    if result.get("is_demo"):
        print("(использованы демонстрационные данные)")
