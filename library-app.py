from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from getpass import getpass
import sys, os, bcrypt
from tabulate import tabulate
import keyboard

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
    name = Column(String, default='')
    surname = Column(String, default='')
    activated = Column(Boolean, default=True)  # Pole activated
    blocked = Column(Boolean, default=False)   # Pole blocked

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


#FUNKCJE DOT. UZYTKOWNIKÓW
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


def display_all_users():
    users = session.query(User).all()
    if users:
        user_data = []
        for user in users:
            user_data.append([user.id, user.username, user.name, user.surname, 'Tak' if user.is_admin else 'Nie', 'Tak' if user.activated else 'Nie', 'Tak' if user.blocked else 'Nie'])
        headers = ["ID", "Nazwa użytkownika", "Imię", "Nazwisko", "Administrator", "Aktywowany", "Zablokowany"]
        print(tabulate(user_data, headers=headers, tablefmt="grid"))
    else:
        print("Brak użytkowników w bazie danych.")


def delete_user(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
        print(f"Użytkownik {username} został pomyślnie usunięty.")
    else:
        print("Nie ma użytkownika o podanej nazwie.")

def change_password_by_admin(user_id, new_password):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = password_hash
        session.commit()
        print(f"Hasło dla użytkownika o ID {user_id} zostało pomyślnie zmienione.")
    else:
        print("Nie ma użytkownika o podanym ID.")

# Funkcja do zmiany pola activated przez administratora
def change_activated_status(user_id, activated):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.activated = activated
        session.commit()
        print(f"Status aktywacji dla użytkownika o ID {user_id} został zmieniony.")
    else:
        print("Nie ma użytkownika o podanym ID.")

# Funkcja do zmiany pola blocked przez administratora
def change_blocked_status(user_id, blocked):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user.blocked = blocked
        session.commit()
        print(f"Status blokady dla użytkownika o ID {user_id} został zmieniony.")
    else:
        print("Nie ma użytkownika o podanym ID.")


def edit_user_data(user, name=None, surname=None, is_admin=None, username=None):
    if name is not None:
        user.name = name
    if surname is not None:
        user.surname = surname
    if is_admin is not None:
        user.is_admin = is_admin
    if username is not None:
        user.username = username
    session.commit()
    print("Dane użytkownika zostały pomyślnie zaktualizowane.")


def search_user(search_term):
    search = f"%{search_term}%"
    users = session.query(User).filter(
        (User.id.like(search)) |
        (User.username.like(search)) |
        (User.name.like(search)) |
        (User.surname.like(search))
    ).all()
    if users:
        user_data = []
        for user in users:
            user_data.append([user.id, user.username, user.name, user.surname, 'Tak' if user.is_admin else 'Nie', 'Tak' if user.activated else 'Nie', 'Tak' if user.blocked else 'Nie'])
        headers = ["ID", "Nazwa użytkownika", "Imię", "Nazwisko", "Administrator", "Aktywowany", "Zablokowany"]
        print(tabulate(user_data, headers=headers, tablefmt="grid"))
    else:
        print("Nie znaleziono użytkownika pasującego do podanej frazy.")

def search_book(search_term):
    search = f"%{search_term}%"
    books = session.query(Book).filter(
        (Book.id.like(search)) |
        (Book.title.like(search)) |
        (Book.year.like(search)) |
        (Book.author.like(search))
    ).all()
    if books:
        book_data = []
        for book in books:
            book_data.append([book.id, book.title, book.author, book.year])
        headers = ["ID", "Tytuł", "Autor", "Rok"]
        print(tabulate(book_data, headers=headers, tablefmt="grid"))
    else:
        print("Nie znaleziono książki pasującej do podanej frazy.")

def display_user_books(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        user_books = user.books
        if user_books:
            book_data = []
            for book in user_books:
                book_data.append([book.id, book.title, book.author, book.year])
            headers = ["ID", "Tytuł", "Autor", "Rok"]
            print(tabulate(book_data, headers=headers, tablefmt="grid"))
        else:
            print("Nie masz wypożyczonych książek.")
    else:
        print("Nie ma użytkownika o podanym ID.")

def change_password(user_id, new_password):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = password_hash
        session.commit()
        print("Hasło zostało pomyślnie zmienione.")
    else:
        print("Nie ma użytkownika o podanym ID.")


def count_user_borrowed_books(user_id):
    return session.query(func.count(Transaction.id)).filter_by(user_id=user_id, returned_at=None).scalar()




# FUNKCJE DOT. KSIĄŻEK
def borrow_book(user, book_id):
    if user.blocked == True:
        print("Twoje konto jest zablokowane, nie możesz korzystać w pełni z biblioteki.")
    else:
        try:
            book_id = int(book_id)
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
        except ValueError:
            print("Podano nieprawidłowe ID książki.")

# Funkcja do oddawania książki
def return_book(user, book_id):
    if user.blocked == True:
        print("Twoje konto jest zablokowane, nie możesz korzystać w pełni z biblioteki.")
    else:
        try:
            book_id = int(book_id)
            book = session.query(Book).filter_by(id=book_id, user_id=user.id).first()
            if book:
                book.user_id = None
                session.query(Transaction).filter_by(book_id=book_id, user_id=user.id, returned_at=None).update({"returned_at": func.now()})
                session.commit()
                print("Oddano książkę.")
            else:
                print("Nie możesz zwrócić tej książki.")
        except ValueError:
            print("Podano nieprawidłowe ID książki.")

# Funkcja do wyświetlania wszystkich dostępnych książek
def display_available_books():
    if user.blocked == True:
        print("Twoje konto jest zablokowane, nie możesz korzystać w pełni z biblioteki.")
    else:
        books = session.query(Book).filter_by(user_id=None).all()
        if books:
            book_data = []
            for book in books:
                book_data.append([book.id, book.title, book.author, book.year])
            headers = ["ID", "Tytuł", "Autor", "Rok"]
            print(tabulate(book_data, headers=headers, tablefmt="grid"))
        else:
            print("Nie masz dostępnych książek.")

def display_all_books():
    books = session.query(Book).all()
    if books:
        book_data = []
        for book in books:
            book_data.append([book.id, book.title, book.author, book.year, book.user_id])
        headers = ["ID", "Tytuł", "Autor", "Rok", "ID Użytkownika"]
        print(tabulate(book_data, headers=headers, tablefmt="grid"))
    else:
        print("Nie ma książek w bazie danych.")

def delete_book(book_id):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        session.delete(book)
        session.commit()
        print("Książka została pomyślnie usunięta.")
    else:
        print("Nie ma książki o podanym ID.")

def edit_book(book_id, title=None, author=None, year=None, user_id=None):
    book = session.query(Book).filter_by(id=book_id).first()
    if book:
        if title is not None:
            book.title = title
        if author is not None:
            book.author = author
        if year is not None:
            book.year = year
        if user_id is not None:
            book.user_id = user_id
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
                clear_terminal()
                print("--- ZALOGUJ SIĘ --- 'esc' - exit ")
                username = input("Podaj nazwę użytkownika: ")
                if username.lower() == "esc":
                    print("Anulowano.")
                else:
                    password = getpass("Podaj hasło: ")
                    user = login_user(username, password)
                    if user:
                        print("Zalogowano.")
                        break
                    else:
                        print("Nieprawidłowe dane logowania.")
                input("Naciśnij Enter, aby kontynuować...")
            elif choice == "2":
                clear_terminal()
                print("--- ZAREJESTRUJ SIĘ --- 'esc' - exit ")
                username = input("Podaj nazwę użytkownika: ")
                if username.lower() == "esc":
                    print("Anulowano.")
                else:
                    password = getpass("Podaj hasło: ")
                    register_user(username, password)
                    print("Zarejestrowano. Teraz możesz się zalogować.")
                input("Naciśnij Enter, aby kontynuować...")
            elif choice == "3":
                print("Do zobaczenia!")
                sys.exit()  # Zamykanie aplikacji
            else:
                print("Nieprawidłowy wybór.")
                input("Naciśnij Enter, aby kontynuować...")

        # Menu admina po zalogowaniu
        while True:
            if (user.activated == False):
                clear_terminal()
                input("Twoje konto zostało dezaktywowane, skontaktuj się z administratorem.")
                break  # Wylogowanie użytkownika w przypadku zablokowania konta

            if user.is_admin == True:  # Sprawdzamy, czy zalogowany użytkownik to admin
                clear_terminal()
                print(f"Witaj {user.name}!")
                action = input(
                    "\nCo chcesz zrobić?\n1. Zarządzanie użytkownikami\n2. Zarządzanie książkami\n3. Zmień hasło\n4. Wyloguj\n5. (To-Do)Przeglądaj Transakcje\nWybierz opcję: ")
                if action == "1":
                    while True:
                        clear_terminal()
                        print("--- ZARZĄDZANIE UŻYTKOWNIKAMI --- 'esc' - exit ")
                        user_action = input(
                            "\nCo chcesz zrobić?\n1. Wyświetl listę użytkowników\n2. Dodaj nowego użytkownika\n3. Edytuj użytkownika\n4. Szukaj użytkownika\n5. Usuń użytkownika\n6. Aktywuj/Deaktywuj użytkownika\n7. Zablokuj/Odblokuj użytkownika\n8. Powrót\nWybierz opcję: ")
                        if user_action == "1":
                            clear_terminal()
                            print("--- WYŚWIETL WSZYSTKICH UŻYTKOWNIKÓW ---")
                            display_all_users()
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "2":
                            clear_terminal()
                            print("--- DODAJ NOWEGO UŻYTKOWNIKA --- 'esc' - exit ")
                            username = input("Podaj nazwę użytkownika: ")
                            if username.lower() == "esc":
                                print("Anulowano.")
                            else:
                                password = getpass("Podaj hasło: ")
                                while True:
                                    is_admin_input = input(
                                        "Czy użytkownik ma być administratorem? (T/N): ").strip().lower()
                                    if is_admin_input in ["t", "n"]:
                                        is_admin = is_admin_input == "t"
                                        break
                                    else:
                                        print("Nieprawidłowa wartość. Podaj T/N.")
                                register_user(username, password, is_admin)
                                print("Dodano użytkownika.")
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "3":
                            clear_terminal()
                            print("--- EDYTUJ UŻYTKOWNIKA --- 'esc' - exit ")
                            user_id = input("Podaj ID użytkownika, którego dane chcesz edytować: ")
                            if user_id.lower() == "esc":
                                print("Anulowano.")
                            else:

                                try:
                                    user_id = int(user_id)
                                    user_to_edit = session.query(User).filter_by(id=user_id).first()


                                    # Dane użytkownika w formie listy
                                    user_data = [
                                        [user_to_edit.id, user_to_edit.username, user_to_edit.name,
                                         user_to_edit.surname,
                                         "Tak" if user_to_edit.is_admin else "Nie",
                                         "Tak" if user_to_edit.activated else "Nie",
                                         "Tak" if user_to_edit.blocked else "Nie"]
                                    ]

                                    # Nagłówki kolumn
                                    headers = ["ID", "Nazwa użytkownika", "Imię", "Nazwisko", "Administrator",
                                               "Aktywowany", "Zablokowany"]

                                    # Wyświetlenie tabeli
                                    print(tabulate(user_data, headers=headers, tablefmt="grid"))


                                    if user_to_edit:
                                        print("Dostępne opcje edycji:")
                                        print("1. Zmiana nazwy użytkownika")
                                        print("2. Zmiana hasła")
                                        print("3. Zmiana imienia")
                                        print("4. Zmiana nazwiska")
                                        print("5. Zmiana statusu administratora")

                                        option = input("Wybierz opcję: ")
                                        if option == "1":
                                            new_username = input("Nowa nazwa użytkownika: ")
                                            edit_user_data(user_to_edit, username=new_username)
                                        elif option == "2":
                                            new_password = getpass("Nowe hasło: ")
                                            password_hash = bcrypt.hashpw(new_password.encode('utf-8'),
                                                                         bcrypt.gensalt())
                                            user_to_edit.password_hash = password_hash
                                            session.commit()
                                            print("Hasło zostało pomyślnie zmienione.")
                                        elif option == "3":
                                            new_name = input("Nowe imię: ")
                                            edit_user_data(user_to_edit, name=new_name)
                                        elif option == "4":
                                            new_surname = input("Nowe nazwisko: ")
                                            edit_user_data(user_to_edit, surname=new_surname)
                                        elif option == "5":
                                            while True:
                                                new_admin_status = input(
                                                    "Czy użytkownik ma być administratorem? (T/N): ").strip().lower()
                                                if new_admin_status in ["t", "n"]:
                                                    is_admin = new_admin_status == "t"
                                                    edit_user_data(user_to_edit, is_admin=is_admin)
                                                    break
                                                else:
                                                    print("Nieprawidłowa wartość. Podaj T/N.")
                                        else:
                                            print("Nieprawidłowa opcja.")
                                    else:
                                        print("Nie ma użytkownika o podanym ID.")
                                except ValueError:
                                    print("ID użytkownika nieprawidłowe.")
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "4":
                            clear_terminal()
                            print("--- SZUKAJ UŻYTKOWNIKA ---")
                            search_term = input("Wpisz frazę do wyszukania: ")
                            search_user(search_term)
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "5":
                            clear_terminal()
                            print("--- USUŃ UŻYTKOWNIKA --- 'esc' - exit ")
                            username = input("Podaj nazwę użytkownika do usunięcia: ")
                            if username.lower() == "esc":
                                print("Anulowano.")
                            else:
                                delete_user(username)
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "6":
                            clear_terminal()
                            print("--- AKTYWUJ/DEAKTYWUJ UŻYTKOWNIKA --- 'esc' - exit ")
                            changed_user_id = input("Podaj ID użytkownika do aktywacji/deaktywacji: ")
                            if changed_user_id.lower() == "esc":
                                print("Anulowano.")
                            else:
                                changed_user_id = int(changed_user_id)
                                changed_user = session.query(User).filter_by(id=changed_user_id).first()
                                if changed_user:
                                    activated = True if changed_user.activated == False else False
                                    change_activated_status(changed_user_id, activated)
                                else:
                                    print("Nie ma użytkownika o podanym ID.")
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "7":
                            clear_terminal()
                            print("--- ZABLOKUJ/ODBLOKUJ UŻYTKOWNIKA --- 'esc' - exit ")
                            changed_user_id = input("Podaj ID użytkownika do zablokowania/odblokowania: ")
                            if changed_user_id.lower() == "esc":
                                print("Anulowano.")
                            else:
                                changed_user_id = int(changed_user_id)
                                changed_user = session.query(User).filter_by(id=changed_user_id).first()
                                if changed_user:
                                    blocked = True if changed_user.blocked == False else False
                                    change_blocked_status(changed_user_id, blocked)
                                else:
                                    print("Nie ma użytkownika o podanym ID.")
                            input("Naciśnij Enter, aby kontynuować...")
                        elif user_action == "8":
                            break
                        elif user_action.lower() == "esc":
                            break
                        else:
                            print("Nieprawidłowy wybór.")
                            input("Naciśnij Enter, aby kontynuować...")
                elif action == "2":
                    while True:
                        clear_terminal()
                        print("--- ZARZĄDZANIE KSIĄŻKAMI --- 'esc' - exit ")
                        book_action = input(
                            "\nCo chcesz zrobić?\n1. Wyświetl listę książek\n2. Dodaj książkę\n3. Edytuj książkę\n4. Szukaj książki\n5. Powrót\nWybierz opcję: ")
                        if book_action == "1":
                            clear_terminal()
                            print("--- WYŚWIETL LISTĘ KSIĄŻEK ---")
                            display_all_books()
                            input("Naciśnij Enter, aby kontynuować...")
                        elif book_action == "2":
                            clear_terminal()
                            print("--- DODAJ KSIĄŻKĘ ---")
                            title = input("Podaj tytuł książki: ")
                            if title.lower() == "esc":
                                print("Anulowano.")
                            else:
                                author = input("Podaj autora książki: ")
                                year = None
                                while True:
                                    year_input = input("Podaj rok wydania książki: ")
                                    try:
                                        year = int(year_input)
                                        break  # Jeśli udało się przekonwertować na int, wychodzimy z pętli
                                    except ValueError:
                                        print("Podany rok jest nieprawidłowy. Wprowadź liczbę.")
                                book = Book(title=title, author=author, year=year)
                                session.add(book)
                                session.commit()
                                print("Dodano książkę.")
                            input("Naciśnij Enter, aby kontynuować...")
                        elif book_action == "3":
                            clear_terminal()
                            print("--- EDYTUJ KSIĄŻKĘ ---")
                            book_id = input("Podaj ID książki do edycji: ")
                            if book_id.lower() == "esc":
                                print("Anulowano.")
                            else:
                                book_id = int(book_id)
                                clear_terminal()
                                print("--- WYBIERZ CO CHCESZ ZMODYFIKOWAĆ ---")
                                print("1. Tytuł")
                                print("2. Autor")
                                print("3. Rok")
                                print("4. ID wypożyczającego")
                                edit_option = input("Wybierz opcję: ")
                                if edit_option == "1":
                                    new_title = input("Podaj nowy tytuł: ")
                                    edit_book(book_id, new_title)
                                elif edit_option == "2":
                                    new_author = input("Podaj nowego autora: ")
                                    edit_book(book_id, None, new_author)
                                elif edit_option == "3":
                                    new_year = input("Podaj nowy rok: ")
                                    edit_book(book_id, None, None, new_year)
                                elif edit_option == "4":
                                    while True:
                                        new_user_id_input = input(
                                            "Podaj nowe ID użytkownika (0 - brak przypisanego użytkownika): ")
                                        if new_user_id_input.lower() == "esc":
                                            print("Anulowano.")
                                            break
                                        try:
                                            new_user_id = int(new_user_id_input)
                                            if new_user_id < 0:
                                                print("Podane ID użytkownika jest nieprawidłowe.")
                                            else:
                                                edit_book(book_id, None, None, None, new_user_id)
                                                break
                                        except ValueError:
                                            print("Podane ID użytkownika jest nieprawidłowe.")
                                else:
                                    print("Nieprawidłowy wybór.")
                                input("Naciśnij Enter, aby kontynuować...")
                        elif book_action == "4":
                            clear_terminal()
                            print("--- SZUKAJ KSIĄŻKI ---")
                            search_term = input("Wprowadź frazę do wyszukania: ")
                            search_book(search_term)
                            input("Naciśnij Enter, aby kontynuować...")
                        elif book_action == "5":
                            break
                        elif book_action == "esc":
                            break
                        else:
                            print("Nieprawidłowy wybór.")
                            input("Naciśnij Enter, aby kontynuować...")
                elif action == "3":
                    clear_terminal()
                    print("--- ZMIEŃ HASŁO ---")
                    new_password = getpass("Nowe hasło: ")
                    confirm_password = getpass("Potwierdź nowe hasło: ")
                    if new_password == confirm_password:
                        change_password(user.id, new_password)
                    else:
                        print("Podane hasła nie zgadzają się.")
                    input("Naciśnij Enter, aby kontynuować...")
                elif action == "4":
                    break
                else:
                    print("Nieprawidłowy wybór.")
                    input("Naciśnij Enter, aby kontynuować...")
# Menu użytkownika po zalogowaniu
            else:
                clear_terminal()
                if (user.activated == False):
                    clear_terminal()
                    input("Twoje konto zostało dezaktywowane, skontaktuj się z administratorem.")
                    break  # Wylogowanie użytkownika w przypadku zablokowania konta
                print(f"Witaj {user.name}!")

                if not user.name or not user.surname:
                    print("Aby kontynuować, podaj swoje imię i nazwisko:")
                    name = input("Imię: ")
                    surname = input("Nazwisko: ")
                    edit_user_data(user, name=name, surname=surname)
                clear_terminal()

                print(f"Witaj {user.name}!")
                if (user.blocked == False):
                    print("Twoje konto jest aktywne!")
                else:
                    print("Twoje konto zostało zablokowane! Skontaktuj się z administratorem")

                borrowed_books_count = count_user_borrowed_books(user.id)  # Liczba wypożyczonych książek

                action = input(
                    f"\nCo chcesz zrobić?\n1. Wypożycz książkę\n2. Oddaj książkę\n3. Pokaż dostępne książki\n4. Pokaż moje wypożyczone książki ({borrowed_books_count})\n5. Edytuj swoje dane\n6. Zmień hasło\n7. Deaktywuj moje konto\n8. Wyloguj\nWybierz opcję: ")
                if action == "1":
                    clear_terminal()
                    print("--- WYPOŻYCZ KSIĄŻKĘ --- 'esc' - exit ")
                    display_available_books()
                    book_id = input("Podaj ID książki, którą chcesz wypożyczyć: ")
                    if book_id.lower() == "esc":
                        print("Anulowano.")
                    else:
                        borrow_book(user, book_id)
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "2":
                    clear_terminal()
                    print("--- ODDAJ KSIĄŻKĘ --- 'esc' - exit ")
                    display_user_books(user.id)
                    book_id = input("Podaj ID książki, którą chcesz zwrócić: ")
                    if book_id.lower() == "esc":
                        print("Anulowano.")
                    else:
                        return_book(user, book_id)
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "3":
                    clear_terminal()
                    print("--- DOSTĘPNE KSIĄŻKI ---")
                    display_available_books()
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "4":
                    clear_terminal()
                    print("--- MOJE WYPOŻYCZONE KSIĄŻKI ---")
                    display_user_books(user.id)
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "5":
                    clear_terminal()
                    print("--- EDYTUJ SWOJE DANE --- 'esc' - exit ")
                    new_name = input("Nowe imię (jeśli bez zmian, zostaw puste): ")
                    new_surname = input("Nowe nazwisko (jeśli bez zmian, zostaw puste): ")
                    if new_name.lower() == "esc" or new_surname.lower() == "esc":
                        input("Anulowano.")
                        clear_terminal()
                    elif new_name.lower() == "" and new_surname.lower() != "":
                        edit_user_data(user, surname=new_surname)
                        input("Zmieniono nazwisko.")
                    elif new_surname.lower() == "" and new_name.lower() != "":
                        edit_user_data(user, name=new_name)
                        input("Zmieniono imie.")
                    elif new_name.lower() != "" and new_surname.lower() != "":
                        edit_user_data(user, name=new_name, surname=new_surname)
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "6":
                    clear_terminal()
                    print("--- ZMIEŃ HASŁO ---")
                    new_password = getpass("Nowe hasło: ")
                    confirm_password = getpass("Potwierdź nowe hasło: ")
                    if new_password == confirm_password:
                        change_password(user.id, new_password)
                    else:
                        print("Podane hasła nie zgadzają się.")
                    input("Naciśnij Enter, aby kontynuować...")
                    clear_terminal()
                elif action == "7":
                    clear_terminal()
                    print("--- DEAKTYWUJ MOJE KONTO ---")
                    confirmation = input("Czy na pewno chcesz deaktywować swoje konto? (TAK/NIE): ")
                    if confirmation.upper() == "TAK":
                        change_activated_status(user.id, False)
                        print("Twoje konto zostało deaktywowane.")
                        break  # Wylogowanie użytkownika po deaktywacji konta
                    elif confirmation.upper() == "NIE":
                        print("Anulowano.")
                    else:
                        print("Nieprawidłowa odpowiedź.")
                    input("Naciśnij Enter, aby kontynuować...")
                elif action == "8":
                    break
                elif action.lower() == "esc":
                    break
                else:
                    print("Nieprawidłowy wybór.")
                    input("Naciśnij Enter, aby kontynuować...")

