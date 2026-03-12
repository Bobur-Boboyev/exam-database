from datetime import datetime

from library.models import Author, Book, Student, Borrow
from library.db import SessionLocal

session = SessionLocal()


def create_author(name: str, bio: str = None) -> Author:
    """Yangi muallif yaratish"""
    author = Author(name=name, bio=bio)

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


def get_author_by_id(author_id: int) -> Author | None:
    """ID bo'yicha muallifni olish"""
    return session.query(Author).filter(Author.id == author_id).first()


def get_all_authors() -> list[Author]:
    """Barcha mualliflar ro'yxatini olish"""
    return session.query(Author).all()


def update_author(author_id: int, name: str = None, bio: str = None) -> Author | None:
    """Muallif ma'lumotlarini yangilash"""
    author = get_author_by_id(author_id=author_id)

    if not author:
        return None

    if name is not None:
        author.name = name
    if bio is not None:
        author.bio = bio

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


def delete_author(author_id: int) -> bool:
    """Muallifni o'chirish (faqat kitoblari bo'lmagan holda)"""
    author = get_author_by_id(author_id=author_id)

    if not author:
        return False

    if author.books:
        return False

    session.delete(author)
    session.commit()

    return True


def create_book(
    title: str, author_id: int, published_year: int, isbn: str = None
) -> Book:
    """Yangi kitob yaratish"""
    existing_book = session.query(Book).filter(Book.isbn == isbn).first()

    if existing_book:
        raise ValueError("isbn must be unique.")

    book = Book(
        title=title, author_id=author_id, published_year=published_year, isbn=isbn
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


def get_book_by_id(book_id: int) -> Book | None:
    """ID bo'yicha kitobni olish"""
    return session.query(Book).filter(Book.id == book_id).first()


def get_all_books() -> list[Book]:
    """Barcha kitoblar ro'yxatini olish"""
    return session.query(Book).all()


def search_books_by_title(title: str) -> list[Book]:
    """Kitoblarni sarlavha bo'yicha qidirish (partial match)"""
    title = title.strip()
    return session.query(Book).filter(Book.title.ilike(f"%{title}%")).all()


def delete_book(book_id: int) -> bool:
    """Kitobni o'chirish"""
    book = get_book_by_id(book_id)

    if not book:
        return False

    session.delete(book)
    session.commit()

    return True


def create_book(
    title: str, author_id: int, published_year: int, isbn: str = None
) -> Book:
    if isbn:
        existing_book = session.query(Book).filter(Book.isbn == isbn).first()
        if existing_book:
            raise ValueError("isbn must be unique.")

    book = Book(
        title=title, author_id=author_id, published_year=published_year, isbn=isbn
    )

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


def create_student(full_name: str, email: str, grade: str = None) -> Student:
    """Yangi talaba ro'yxatdan o'tkazish"""
    existing_student = session.query(Student).filter(Student.email == email).first()

    if existing_student:
        raise ValueError("email must be unique.")

    student = Student(full_name=full_name, email=email, grade=grade)

    session.add(student)
    session.commit()
    session.refresh(student)

    return student


def get_student_by_id(student_id: int) -> Student | None:
    """ID bo'yicha talabani olish"""
    return session.query(Student).filter(Student.id == student_id).first()


def get_all_students() -> list[Student]:
    """Barcha talabalar ro'yxatini olish"""
    return session.query(Student).all()


def update_student_grade(student_id: int, grade: str) -> Student | None:
    """Talaba sinfini yangilash"""
    user = get_student_by_id(student_id)

    if not user:
        return None

    user.grade = grade

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def borrow_book(student_id: int, book_id: int) -> Borrow | None:
    """
    Talabaga kitob berish

    Quyidagilarni tekshirish kerak:
    1. Student va Book mavjudligini
    2. Kitobning is_available=True ekanligini
    3. Talabada 3 tadan ortiq qaytarilmagan kitob yo'qligini yani 3 tagacha kitob borrow qila oladi

    Transaction ichida:
    - Borrow yozuvi yaratish
    - Book.is_available = False qilish
    - due_date ni hisoblash (14 kun)

    Returns:
        Borrow object yoki None (xatolik bo'lsa)
    """
    student = get_student_by_id(student_id)
    book = get_book_by_id(book_id)

    if not student or not book:
        return None

    if not book.is_available:
        return None

    borrowed_books = (
        session.query(Borrow)
        .filter(Borrow.student_id == student.id, Borrow.returned_at == None)
        .count()
    )

    if borrowed_books >= 3:
        return None

    # due_date Borrow da avtomatik hisoblanadi
    borrow = Borrow(student_id=student.id, book_id=book.id)

    book.is_available = False

    session.add(borrow)
    session.commit()
    session.refresh(borrow)

    return borrow


def return_book(borrow_id: int) -> bool:
    """
    Kitobni qaytarish

    Transaction ichida:
    - Borrow.returned_at ni to'ldirish
    - Book.is_available = True qilish

    Returns:
        True (muvaffaqiyatli) yoki False (xatolik)
    """
    borrow = session.query(Borrow).filter(Borrow.id == borrow_id).first()

    if not borrow:
        return False

    if borrow.returned_at:
        raise ValueError("Book already returned.")

    borrow.returned_at = datetime.now()
    borrow.book.is_available = True

    session.commit()

    return True


def get_student_borrow_count(student_id: int) -> int:
    """Talabaning jami olgan kitoblari soni"""
    return session.query(Borrow).filter(Borrow.student_id == student_id).count()


def get_currently_borrowed_books() -> list[tuple[Book, Student, datetime]]:
    """Hozirda band bo'lgan kitoblar va ularni olgan talabalar"""
    books = session.query(Borrow).filter(Borrow.returned_at == None).all()

    borrowed_books = list(
        map(lambda borrow: (borrow.book, borrow.student, borrow.borrowed_at), books)
    )
    return borrowed_books


def get_books_by_author(author_id: int) -> list[Book]:
    """Muayyan muallifning barcha kitoblari"""
    author = get_author_by_id(author_id)

    if not author:
        return None

    books = author.books

    return books


def get_overdue_borrows() -> list[tuple[Borrow, Student, Book, int]]:
    """
    Kechikkan kitoblar ro'yxati

    Returns:
        List of tuples: (Borrow, Student, Book, kechikkan_kunlar)
        faqat returned_at=NULL va due_date o'tgan yozuvlar
    """
    borrows = (
        session.query(Borrow)
        .filter(Borrow.returned_at == None, Borrow.due_date < datetime.now())
        .all()
    )

    result = list(
        map(
            lambda borrow: (
                borrow,
                borrow.student,
                borrow.book,
                (datetime.now() - borrow.due_date).days,
            ),
            borrows,
        )
    )
    return result
