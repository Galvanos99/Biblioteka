from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from getpass import getpass
import sys, os, bcrypt

# Tworzymy instancję silnika bazy danych SQLite
engine = create_engine('sqlite:///library.db', echo=False)

# Deklarujemy bazę dla modeli
Base = declarative_base()

# Definiujemy modele dla użytkowników i książek
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    is_admin = Column(Boolean, default=False)  # Zmieniamy typ na Boolean i domyślnie ustawiamy na False

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
def register_user(username, password, is_admin=False):
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user:
        print("Użytkownik o tej nazwie już istnieje.")
        return
    else:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())  # Haszujemy hasło
        user = User(username=username, password_hash=password_hash, is_admin=is_admin)
        session.add(user)
        session.commit()


# Prosta funkcja do logowania użytkownika
def login_user(username, password):
    user = session.query(User).filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        return user
    return None

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
    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")

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
    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")

# Funkcja do wyświetlania wszystkich dostępnych książek
def display_available_books():
    books = session.query(Book).filter_by(user_id=None).all()
    if books:
        print("Twoje wypożyczone książki:")
        for i, book in enumerate(books, start=1):
            print(f"{i}. Tytuł: {book.title}")
            print(f"   Autor: {book.author}")
            print(f"   Rok: {book.year}")
            print()
    else:
        print("Nie masz dostępnych książek.")


# Prosta funkcja do wyświetlania wypożyczonych książek przez użytkownika
def display_borrowed_books(user):
    books = session.query(Book).filter_by(user_id=user.id).all()
    if books:
        print("Twoje wypożyczone książki:")
        for i, book in enumerate(books, start=1):
            print(f"{i}. Tytuł: {book.title}")
            print(f"   Autor: {book.author}")
            print(f"   Rok: {book.year}")
            print()
    else:
        print("Nie masz wypożyczonych książek.")

def delete_user(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
        print(f"Użytkownik {username} został pomyślnie usunięty.")
    else:
        print("Nie ma użytkownika o podanej nazwie.")

def change_password_by_admin(username, new_password):
    user = session.query(User).filter_by(username=username).first()
    if user:
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = password_hash
        session.commit()
        print(f"Hasło dla użytkownika {username} zostało pomyślnie zmienione.")
    else:
        print("Nie ma użytkownika o podanej nazwie.")

def delete_book(book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        session.delete(book)
        session.commit()
        print("Książka została pomyślnie usunięta.")
    else:
        print("Nie ma książki o podanym ID.")

def edit_book(book_id, title=None, author=None, year=None):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if year is not None:
            book.year = year
        session.commit()
        print("Dane książki zostały pomyślnie zaktualizowane.")
    else:
        print("Nie ma książki o podanym ID.")


# Przykładowe użycie
if __name__ == "__main__":
    admin_username = "admin"
    admin_password = "admin123"
    register_user(admin_username, admin_password,True)
    user_name="user1"
    user_password="user123"
    register_user(user_name,user_password,False)

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
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
            elif choice == "2":
                username = input("Podaj nazwę użytkownika: ")
                password = getpass("Podaj hasło: ")
                register_user(username, password)
                print("Zarejestrowano. Teraz możesz się zalogować.")
                input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
            elif choice == "3":
                print("Do zobaczenia!")
                sys.exit()  # Zamykanie aplikacji
            else:
                print("Nieprawidłowy wybór.")

    # Menu admina po zalogowaniu
        while True:
            if user.is_admin == True:  # Sprawdzamy, czy zalogowany użytkownik to admin
                clear_terminal()
                print(f"Witaj {user.username}!")
                action = input(
                    "\nCo chcesz zrobić?\n1. Dodaj użytkownika\n2. Dodaj administratora\n3. Usuń użytkownika\n4. Edytuj hasło użytkownika\n5. Dodaj książkę\n6. Usuń książkę\n7. Edytuj książkę\n8. Wyloguj\nWybierz opcję: ")
                if action == "1":
                    username = input("Podaj nazwę użytkownika: ")
                    password = getpass("Podaj hasło: ")
                    register_user(username, password,False)
                    print("Dodano użytkownika.")
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "2":
                    username = input("Podaj nazwę administratora: ")
                    password = getpass("Podaj hasło: ")
                    register_user(username, password,True)
                    print("Dodano użytkownika.")
                elif action == "3":
                    username = input("Podaj nazwę użytkownika: ")
                    delete_user(username)
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "4":
                    username = input("Podaj nazwę użytkownika: ")
                    new_password = getpass("Podaj nowe hasło: ")
                    change_password_by_admin(username,new_password)
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "5":
                    title = input("Podaj tytuł książki: ")
                    author = input("Podaj autora książki: ")
                    year = int(input("Podaj rok wydania książki: "))
                    book = Book(title=title, author=author, year=year)
                    session.add(book)
                    session.commit()
                    print("Dodano książkę.")
                elif action == "6":
                    book_id = int(input("Podaj ID książki, którą chcesz usunąć: "))
                    delete_book(book_id)
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "7":
                    book_id = int(input("Podaj ID książki, którą chcesz edytować: "))
                    title = input("Podaj tytuł książki: ")
                    author = input("Podaj autora książki: ")
                    year = int(input("Podaj rok wydania książki: "))
                    edit_book(book_id,title,author,year)
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "8":
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
                    clear_terminal()
                    display_available_books()
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "2":
                    book_id = int(input("Podaj ID książki, którą chcesz wypożyczyć: "))
                    borrow_book(user, book_id)
                elif action == "3":
                    book_id = int(input("Podaj ID książki, którą chcesz zwrócić: "))
                    return_book(user, book_id)
                elif action == "4":
                    clear_terminal()
                    display_borrowed_books(user)
                    input("Naciśnij Enter, aby wrócić do poprzedniego menu.")
                elif action == "5":
                    print("Wylogowano.")
                    break
                else:
                    print("Nieprawidłowy wybór.")
