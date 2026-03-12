from pprint import pprint
from datetime import datetime, timedelta

from library.models import Base
from library.db import SessionLocal, engine
from library.services import (
    create_author,
    create_book,
    create_student,
    borrow_book,
    return_book,
    get_all_books,
    get_all_students,
    get_overdue_borrows,
)

session = SessionLocal()


def create_tables():
    Base.metadata.create_all(bind=engine)


def drop_tables():
    Base.metadata.drop_all(bind=engine)


def main():

    authors_info = [
        ("J.K. Rowling", "Author of Harry Potter series"),
        ("George Orwell", "Author of 1984 and Animal Farm"),
        ("Fyodor Dostoevsky", "Russian novelist, Crime and Punishment"),
        ("Agatha Christie", "Queen of Crime novels"),
        ("Mark Twain", "Adventures of Huckleberry Finn"),
    ]
    authors = [create_author(name, bio) for name, bio in authors_info]

    books_info = [
        ("Harry Potter and the Sorcerer's Stone", authors[0].id, 1997, "HP1..."),
        ("Harry Potter and the Chamber of Secrets", authors[0].id, 1998, "HP2.."),
        ("1984", authors[1].id, 1949, "1984..."),
        ("Crime and Punishment", authors[2].id, 1866, "CP.."),
        ("Murder on the Orient Express", authors[3].id, 1934, "MOE.."),
        ("Adventures of Huckleberry Finn", authors[4].id, 1884, "HF.."),
    ]
    books = [
        create_book(title, author_id, year, isbn)
        for title, author_id, year, isbn in books_info
    ]

    students_info = [
        ("Alice Smith", "alice1@example.com", "10A"),
        ("Bob Johnson", "bob1@example.com", "11B"),
        ("Charlie Brown", "charlie1@example.com", "12C"),
        ("David Wilson", "david1@example.com", "10A"),
        ("Eva Thompson", "eva1@example.com", "11B"),
        ("Frank Martin", "frank1@example.com", "12C"),
        ("Grace Lee", "grace1@example.com", "10A"),
        ("Henry Clark", "henry1@example.com", "11B"),
        ("Isabella Lewis", "isabella1@example.com", "12C"),
        ("Jack Hall", "jack1@example.com", "10A"),
    ]
    students = [
        create_student(name, email, grade) for name, email, grade in students_info
    ]

    # Overdue borrows
    overdue_borrows = [
        (students[0], books[0], -7),
        (students[2], books[2], -3),
        (students[5], books[3], -10),
        (students[7], books[4], -5),
    ]
    # Normal borrows
    normal_borrows = [
        (students[1], books[1], 5),
        (students[3], books[5], 7),
        (students[4], books[0], 10),
        (students[6], books[2], 3),
    ]

    borrows = []

    for student, book, days_offset in overdue_borrows + normal_borrows:
        borrow = borrow_book(student.id, book.id)
        if borrow:
            borrow.due_date = datetime.now() + timedelta(days=days_offset)
            borrows.append(borrow)

    return {
        "authors": authors,
        "books": books,
        "students": students,
        "borrows": borrows,
    }


def test_overdue_books():
    overdue_list = get_overdue_borrows()

    print("=== Kechikkan kitoblar ===")
    for borrow, student, book, days in overdue_list:
        print(f"{student.full_name} - {book.title} - {days} kun kechikkan")


drop_tables()

if __name__ == "__main__":
    create_tables()
    pprint(main())
    test_overdue_books()
