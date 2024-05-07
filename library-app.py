from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from getpass import getpass
import sys, os

# Tworzymy instancję silnika bazy danych SQLite
engine = create_engine('sqlite:///library.db', echo=False)

# Deklarujemy bazę dla modeli
Base = declarative_base()

# Definiujemy modele dla użytkowników i książek
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    books = relationship("Book", back_populates="user")  # Dodaj ten wiersz

    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="books")

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', year={self.year})>"

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    borrowed_at = Column(String, default=func.now())
    returned_at = Column(String)

    book = relationship("Book")
    user = relationship("User")

# Tworzymy tabelę w bazie danych
Base.metadata.create_all(engine)

# Tworzymy sesję
Session = sessionmaker(bind=engine)
session = Session()

#Czyszczenie terminala
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Prosta funkcja do rejestracji użytkownika
def register_user(username, password):
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    #print("Zarejestrowano użytkownika.")

# Prosta funkcja do logowania użytkownika
def login_user(username, password):
    user = session.query(User).filter_by(username=username, password=password).first()
    return user

# Funkcja do wypożyczania książki
def borrow_book(user, book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        if book.user_id is None:
            book.user_id = user.id
            session.add(Transaction(book_id=book.id, user_id=user.id))
            session.commit()
            print("Wypożyczono książkę.")
        else:
            print("Książka jest już wypożyczona.")
    else:
        print("Książka o podanym ID nie istnieje.")

# Funkcja do oddawania książki
def return_book(user, book_id):
    book = session.query(Book).filter_by(id=book_id, user_id=user.id).first()
    if book:
        book.user_id = None
        session.query(Transaction).filter_by(book_id=book_id, user_id=user.id, returned_at=None).update({"returned_at": func.now()})
        session.commit()
        print("Oddano książkę.")
    else:
        print("Nie możesz zwrócić tej książki.")

# Funkcja do wyświetlania wszystkich dostępnych książek
def display_available_books():
    books = session.query(Book).filter_by(user_id=None).all()
    for book in books:
        print(book)

# Prosta funkcja do wyświetlania wypożyczonych książek przez użytkownika
def display_borrowed_books(user):
    books = session.query(Book).filter_by(user_id=user.id).all()
    for book in books:
        print(book)

# Przykładowe użycie
if __name__ == "__main__":
    admin_username = "admin"
    admin_password = "admin123"
    register_user(admin_username, admin_password)
    #print("Dodano użytkownika admin.")
    user_name="user1"
    user_password="user123"
    register_user(user_name,user_password)

    # Dodaj kilka książek
    books_data = [
        {"title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "year": 1997},
        {"title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
        {"title": "1984", "author": "George Orwell", "year": 1949}
    ]
    for book_info in books_data:
        book = Book(**book_info)
        session.add(book)
    session.commit()

    # Główna pętla aplikacji
    while True:
    # Logowanie lub rejestracja
        while True:
            clear_terminal()
            choice = input("Witaj w bibliotece!\n1. Zaloguj się\n2. Zarejestruj się\n3. Zamknij aplikację\nWybierz opcję: ")
            if choice == "1":
                username = input("Podaj nazwę użytkownika: ")
                password = getpass("Podaj hasło: ")
                user = login_user(username, password)
                if user:
                    print("Zalogowano.")
                    break
                else:
                    print("Nieprawidłowe dane logowania.")
            elif choice == "2":
                username = input("Podaj nazwę użytkownika: ")
                password = getpass("Podaj hasło: ")
                register_user(username, password)
                print("Zarejestrowano. Teraz możesz się zalogować.")
            elif choice == "3":
                print("Do zobaczenia!")
                sys.exit()  # Zamykanie aplikacji
            else:
                print("Nieprawidłowy wybór.")

    # Menu admina po zalogowaniu
        while True:
            if user.username == "admin":  # Sprawdzamy, czy zalogowany użytkownik to admin
                clear_terminal()
                print(f"Witaj {user.username}!")
                action = input(
                    "\nCo chcesz zrobić?\n1. Dodaj użytkownika\n2. Usuń użytkownika\n3. Edytuj hasło użytkownika\n4. Dodaj książkę\n5. Usuń książkę\n6. Edytuj książkę\n7. Wyloguj\nWybierz opcję: ")
                if action == "1":
                    username = input("Podaj nazwę użytkownika: ")
                    password = getpass("Podaj hasło: ")
                    register_user(username, password)
                    print("Dodano użytkownika.")
                elif action == "2":
                    user_id = int(input("Podaj ID użytkownika, którego chcesz usunąć: "))
                    # Tutaj dodać funkcję usuwania użytkownika
                    pass
                elif action == "3":
                    user_id = int(input("Podaj ID użytkownika, którego hasło chcesz zmienić: "))
                    new_password = getpass("Podaj nowe hasło: ")
                    # Tutaj dodać funkcję zmiany hasła użytkownika
                    pass
                elif action == "4":
                    title = input("Podaj tytuł książki: ")
                    author = input("Podaj autora książki: ")
                    year = int(input("Podaj rok wydania książki: "))
                    book = Book(title=title, author=author, year=year)
                    session.add(book)
                    session.commit()
                    print("Dodano książkę.")
                elif action == "5":
                    book_id = int(input("Podaj ID książki, którą chcesz usunąć: "))
                    # Tutaj dodać funkcję usuwania książki
                    pass
                elif action == "6":
                    book_id = int(input("Podaj ID książki, którą chcesz edytować: "))
                    # Tutaj dodać funkcję edycji książki
                    pass
                elif action == "7":
                    print("Wylogowano.")
                    break
                else:
                    print("Nieprawidłowy wybór.")
            else:
                clear_terminal()
                print(f"Witaj {user.username}!")
                action = input(
                    "\nCo chcesz zrobić?\n1. Wyświetl dostępne książki\n2. Wypożycz książkę\n3. Zwróć książkę\n4. Wyświetl moje książki\n5. Wyloguj\nWybierz opcję: ")
                if action == "1":
                    display_available_books()
                elif action == "2":
                    book_id = int(input("Podaj ID książki, którą chcesz wypożyczyć: "))
                    borrow_book(user, book_id)
                elif action == "3":
                    book_id = int(input("Podaj ID książki, którą chcesz zwrócić: "))
                    return_book(user, book_id)
                elif action == "4":
                    display_borrowed_books(user)
                elif action == "5":
                    print("Wylogowano.")
                    break
                else:
                    print("Nieprawidłowy wybór.")
