from datetime import datetime, timedelta

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    Boolean,
    DateTime,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Author(Base, TimestampMixin):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    books: Mapped[list["Book"]] = relationship("Book", back_populates="author")

    def __str__(self):
        return f"Author(id={self.id}, name={self.name}, bio={self.bio})"

    def __repr__(self):
        return f"Author(id={self.id}, name={self.name}, bio={self.bio})"


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id", ondelete="CASCADE"))
    published_year: Mapped[int] = mapped_column(Integer)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)

    author: Mapped["Author"] = relationship("Author", back_populates="books")
    borrows: Mapped[list["Borrow"]] = relationship(
        "Borrow", uselist=True, back_populates="book"
    )

    def __str__(self):
        return f"Book(id={self.id}, title={self.title}, author_id={self.author_id}, published_year={self.published_year}, isbn={self.isbn}, is_available={self.is_available})"

    def __repr__(self):
        return f"Book(id={self.id}, title={self.title}, author_id={self.author_id}, published_year={self.published_year}, isbn={self.isbn}, is_available={self.is_available})"


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    grade: Mapped[str] = mapped_column(String(20), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    borrows: Mapped[list["Borrow"]] = relationship(
        "Borrow", uselist=True, back_populates="student"
    )

    def __str__(self):
        return f"Student(id={self.id}, full_name={self.full_name}, email={self.email}, grade={self.grade}, registered_at={self.registered_at})"

    def __repr__(self):
        return f"Student(id={self.id}, full_name={self.full_name}, email={self.email}, grade={self.grade}, registered_at={self.registered_at})"


class Borrow(Base, TimestampMixin):
    __tablename__ = "borrows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"))
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"))
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    due_date: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.utcnow() + timedelta(days=14)
    )
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    student: Mapped["Student"] = relationship("Student", back_populates="borrows")
    book: Mapped["Book"] = relationship("Book", back_populates="borrows")

    def __str__(self):
        return f"Borrow(id={self.id}, student_id={self.student_id}, book_id={self.book_id}, borrowed_at={self.borrowed_at}, due_date={self.due_date}, returned_at={self.returned_at})"

    def __repr__(self):
        return f"Borrow(id={self.id}, student_id={self.student_id}, book_id={self.book_id}, borrowed_at={self.borrowed_at}, due_date={self.due_date}, returned_at={self.returned_at})"
