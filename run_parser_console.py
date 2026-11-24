"""
Консольный запуск парсера Rusbuk.ru
"""

from modules.parser import run_parser
from modules.database import get_stats, get_all_books

if __name__ == "__main__":
    print("=" * 55)
    print("  Парсер Rusbuk.ru — букинистические книги")
    print("=" * 55)

    result = run_parser(max_pages=2)
    print(result["message"])
    if result.get("is_demo"):
        print("(использованы демонстрационные данные)")

    stats = get_stats()
    print(f"\nВсего книг в базе: {stats['total_books']}")
    print(f"Уникальных авторов: {stats['unique_authors']}")

    print("\nПоследние 5 книг:")
    for b in get_all_books(limit=5):
        print(f"  • {b['author'] or '—'} — {b['title'][:50]}  [{b['price']}]")
