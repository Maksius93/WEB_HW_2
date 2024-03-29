
import json
import re
from pathlib import Path
from json.decoder import JSONDecodeError
from src_classes import Name, Phone, Record, Birthday, AddressBook
from note_classes import Note, NoteBook, Tag
from sort import sort_files_in_folder
# from rich import print


def read_contacts(file_name):
    try:
        with open(file_name, 'r') as f:
            contacts = json.load(f)
    except (FileNotFoundError, AttributeError, JSONDecodeError):
        contacts = {}
    return contacts


def save_contacts(file_name, contacts):
    with open(file_name, 'w') as f:
        if contacts:
            json.dump(contacts, f)


def Error_func(func):
    def inner(*args, **kwargs):
        contacts = AddressBook(kwargs['contacts'])
        if not args:
            IndexError()

        else:
            name = Name(args[0].strip().lower())

        try:
            return func(*args, **kwargs)
        except IndexError:
            return f'Print name and phone/s number via space', contacts
        except KeyError:
            return f'Contact {name} is absent', contacts
        except TypeError as e:
            return (f'If you try to add new contact, contact {name} is already exists.\n'
                    f'If you try to edit contact, contact {name} doesn`t exist'), contacts
        except AttributeError:
            ...
    return inner


def Error_note(func):
    def inner(*args, **kwargs):
        notebook = NoteBook(kwargs['notebook'])

        if not args:
            IndexError()

        else:
            name = Name(args[0].strip().lower())

        try:
            return func(*args, **kwargs)
        except IndexError as exc:
            return f'{exc}', notebook
        except KeyError:
            return f'Contact {name} is absent', notebook
        except TypeError as e:
            return (f'If you try to add new contact, contact {name} is already exists.\n'
                    f'If you try to edit contact, contact {name} doesn`t exist'), notebook
        except AttributeError:
            ...
    return inner


def hello_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return "How can I help you?", contacts


def help_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return ''' 
            To add contacts type "add" and contact`s name after. You can also add phones (>5 digits each), birthdate (format like '27 August 1987' wo quotes), email, notes after name 
            or leave these fields empty. You can also add phone number using this command after contact was created by it`s name. 
            To change contact`s phone number type "change" and contact`s name after, old phone you want to change and new phone (>5 digits) at the end.
            To get contact`s phone numbers type "phone" and contact`s name after.
            To get contact`s birthday type "bd" and contact`s name after.
            To see all contacts with birthday in next n days from today, type "reminder n" (for example, 'reminder 0' wo quotes). You also`ll get contacts with bithday in next 7 days 
            after the date you want to check.
            To get all contacts in your notebook type "show all/show", to get n records, type "show n" wo quotes.
            To delete contact type "delete" and contact`s name after.
            To add a new note, enter the command 'note' followed by the title.
            To find something in notes, enter the command 'fnote'  with something words
            To display all notes, enter 'display'.
            To delete a note, enter 'rnote' followed by the note's title.
            To display a specific note, enter 'snote' followed by the note's title.
            To edit a note, enter 'cnote' followed by the note's title.
            To exit and save changes type "bye"/"close"/"exit"/"."  
            ''', contacts


@Error_func
def add_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    phones = []
    bday = None
    if args[1:]:
        for arg in args[1:]:
            if len(arg) > 5:
                match_phone = re.findall(
                    r'\b\+?\d{1,3}-?\d{1,3}-?\d{1,4}\b', str(arg))
                if match_phone:
                    phones.extend([Phone(phone.strip().lower())
                                  for phone in match_phone])
            match_bd = re.search(r'\b(\d{1,2})\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{4})\b', ' '.join(
                args[1:]), re.IGNORECASE)
            if match_bd:
                bday = Birthday(
                    f"{match_bd.group(1)} {match_bd.group(2)} {match_bd.group(3)}")
    rec = Record(name, phones, bday)

    if not contacts.get(str(name)):
        contacts.add_record(rec)
        save_contacts(file_name, contacts.to_dict())
        return f"Contact {name} with phone {phones} and birthday '{bday}' successfully added", contacts

    if phones:
        contact = contacts.get(str(name))
        contact.add_phone(*phones)
        save_contacts(file_name, contacts.to_dict())
        return f"Phone {phones} added to contact {name}.", contacts
    elif bday:
        contact = contacts.get(str(name))
        contact.bday = bday
        save_contacts(file_name, contacts.to_dict())
        return f"Birthday {bday} added to contact {name}.", contacts


@Error_func
def change_func(*args, **kwargs):
    contacts = kwargs['contacts']

    if args[0]:
        name = Name(args[0].strip().lower())
    else:
        raise IndexError()

    old_phone = Phone(args[1].strip().lower())
    new_phone = Phone(args[2].strip().lower())
    rec = contacts.get(str(name))

    if rec:
        rec.edit_phone(old_phone, new_phone)
        save_contacts(file_name, contacts.to_dict())

        return f"Phone for contact {name} changed successfully.\nOld phone {old_phone}, new phone {new_phone}", contacts
    return f"Contact {name} doesn't exist", contacts


@Error_func
def del_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    contacts.pop(str(name))
    save_contacts(file_name, contacts.to_dict())
    return f"Contact {name} successfully deleted", contacts


@Error_func
def phone_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    return str(contacts.get(str(name))), contacts


def bday_func(*args, **kwargs):
    contacts = kwargs['contacts']
    name = Name(args[0].strip().lower())
    rec = contacts.get(str(name))
    print(type(rec))
    if rec:
        result = rec.days_to_birthday()
        return result, contacts
    return f"Contact {name} doesn't exist", contacts


def show_func(*args, **kwargs):
    contacts = kwargs['contacts']
    if not args:
        return IndexError("Please write integer number or all"), contacts
    else:
        records_num = args[0].strip()
    if contacts:
        if records_num == "all" or not records_num:
            for record in contacts.paginator(records_num=len(contacts)):
                return record, contacts
        if len(args) > 0:
            try:
                records_num = int(args[0].strip())
                for record in contacts.paginator(records_num):
                    return record, contacts
            except ValueError:
                return "The number of contacts for show must be a integer", contacts

    return "No contacts", contacts


def get_birthdays_in_x_days(*args, **kwargs):
    contacts = kwargs['contacts']
    if contacts:
        if len(args) > 0:
            try:
                x = int(args[0].strip())
                return contacts.get_birthdays_in_x_days(x), contacts
            except ValueError:
                pass
            except AttributeError:
                return "You need exit and save contact before using reminder", contacts
        return "Type days number from today", contacts
    return "No contacts found", contacts


def find_func(*args, **kwargs):
    contacts = kwargs["contacts"]
    n = args[0].strip().lower()
    result = []
    for key, value in contacts.items():
        if n in "{} {} {}".format(str(value.name).lower(),
                                  str(value.phones),
                                  str(value.bday)):
            result.append(f"{key} : {value.phones}, {value.bday}")
    return '\n'.join(result) or f"There are no results with {n}", contacts


def unknown_command(*args, **kwargs):
    contacts = kwargs['contacts']
    return "Sorry, unknown command. Try again", contacts


def exit_func(*args, **kwargs):
    contacts = kwargs['contacts']
    return "Bye", contacts


def handler(text):
    for command, func in MODES.items():
        if text.lower().startswith(command):
            return func, text.replace(command, '').strip().split()
    return unknown_command, []


def clean_func(*args, **kwargs):
    contacts = kwargs['contacts']
    main_path = ""
    for item in list(args):
        if "\\" in item:
            main_path = Path(item)
            break
    if main_path != "":
        try:
            sort_files_in_folder(main_path)
            return 'Sorted is ended!', contacts
        except FileNotFoundError:
            return 'The path is not correctly. No such folder exists.', contacts
    else:
        return 'No folder path specified.', contacts


@Error_note
def add_note(*args, **kwargs):
    """
    Додає нотатки:
    поетапно приймає від користувача заголовок, текст нотатки, теги

    """
    notebook: NoteBook = kwargs["notebook"]

    try:
        if args[0]:
            title = ' '.join(args)
    except IndexError:
        raise IndexError('Заголовок не може бути пустим') from None

    text = input("Введіть текст нотатку :")
    str_tags = input("Введіть теги нотатку через кому :")
    tags = [Tag(tag.strip()) for tag in str_tags.split(',')]
    nt = Note(title=title, text=text, tags=tags)
    notebook.add_notes(nt)
    save_contacts(note_file, notebook.to_dict())
    return f"Note '{title}' successfully added", notebook


@Error_note
def display_note(*args, **kwargs):
    """Виводить список заголовків всіх нотатків"""
    notebook: NoteBook = kwargs["notebook"]
    if notebook:
        if len(args) > 0:
            try:
                records_num = int(args[0].strip())
                for note in notebook.paginator(records_num):
                    return note, notebook
            except ValueError:
                pass
        for note in notebook.paginator(notes_num=len(notebook)):
            return note, notebook
    return "No notes", notebook


@Error_note
def find_note(*args, **kwargs):
    """Пошук нотатків """
    notebook: NoteBook = kwargs["notebook"]
    n = args[0].strip().lower()
    result = []
    for key, value in notebook.items():
        if n in "{} {} {}".format(str(value.title).lower(),
                                  str(value.text).lower(),
                                  str(' '.join([str(i) for i in value.tags])).lower()):
            result.append(f"{key} : {value.title}, {value.text}, {value.tags}")
    return '\n'.join(result) or f"There are no results with {n}", notebook


@Error_note
def remove_note(*args, **kwargs):
    """ 
        Видаляє нотатку по заголовку. Треба ввести заголовок повністю
    """
    notebook: NoteBook = kwargs["notebook"]
    try:
        word, notebook = notebook.remove_note(
            ' '.join(args) if len(args) > 1 else args[0])
    except IndexError:
        return 'Note not found', notebook
    save_contacts(note_file, notebook.to_dict())
    return f'{word.capitalize()} successfully remove', notebook


@Error_note
def show_note(*args, **kwargs):
    """ Виводить нотатку потрібно ввести повний заголовок"""
    notebook: NoteBook = kwargs["notebook"]
    n = args[0].strip().lower()
    result = []
    for key, value in notebook.items():
        if n in "{} {} {}".format(str(value.title).lower(),
                                  str(value.text).lower(),
                                  str(' '.join([str(i) for i in value.tags])).lower()):
            result = (f"{key} : {value.title}, {value.text}, {value.tags}")
    return f'{result}' or f"There are no results with {n}", notebook


@Error_note
def note_changes(*args, **kwargs):
    """ Редагує поля нотатку """
    notebook: NoteBook = kwargs["notebook"]
    try:
        if args[0]:
            title = ' '.join(args).lower()
    except IndexError:
        raise IndexError('Введіть корретно заголовок') from None

    note: Note = None

    for k, v in notebook.items():
        if title == k.lower():
            note = v

    if note == None:
        return "Note not found", notebook

    input_text = "Якщо бажаєте змінити заголовк нажтіть '1' якщо текст ноатку нажміть '2' \
а якщо теги тоді '3' "
    choice = input(input_text+'\n >>>')

    match choice:
        case '1':
            old_title = note.title
            new_title = input('Введіь новий заголовок: ')
            if new_title == '':
                raise IndexError("Заголовок не оже бути пустим")
            note.change_title(new_title)
            notebook.pop(old_title)
            notebook[new_title] = note
            save_contacts(note_file, notebook.to_dict())
            return f"Успішно замінили {old_title} на {new_title}", notebook

        case '2':
            old_text = note.text
            new_text = input('Введіь новий текст: ')
            note.change_text(new_text)
            notebook[note.title] = note
            save_contacts(note_file, notebook.to_dict())
            return f"Успішно замінили {old_text} на {new_text}", notebook

        case '3':
            old_tags = note.tags
            new_tags = input('Введіь нові теги через кому: ')
            new_tags = [Tag(tag.strip()) for tag in new_tags.split(',')]
            note.change_tags(new_tags)
            notebook[note.title] = note
            save_contacts(note_file, notebook.to_dict())
            return f"Успішно замінили {old_tags} на {new_tags}", notebook
        case _:
            raise IndexError('Введіть коррекно дані') from None


# список функцій пакеу нотатків]
NOTE_MODES = [add_note, display_note, find_note,
              remove_note, show_note, note_changes]

MODES = {"hello": hello_func,
         "add": add_func,
         "change": change_func,
         "help": help_func,
         "delete": del_func,
         "phone": phone_func,
         "bd": bday_func,
         "reminder": get_birthdays_in_x_days,
         "show": show_func,
         "find": find_func,
         "close": exit_func,
         "exit": exit_func,
         "bye": exit_func,
         "clean": clean_func,
         "note": add_note,
         "fnote": find_note,
         "display": display_note,
         "rnote": remove_note,
         "snote": show_note,
         "cnote": note_changes,
         ".": exit_func}

file_name = 'contacts.json'
note_file = 'note.json'


def main():
    contacts = AddressBook()
    contacts.from_dict(read_contacts(file_name))
    result, contacts = help_func(contacts=contacts)
    notebook = NoteBook()
    notebook.from_dict(read_contacts(note_file))
    print(result)
    while True:
        func, text = handler(input('write command:'))
        if func in NOTE_MODES:
            result, notebook = func(*text, notebook=notebook)
            print(result)
        elif func:
            result, contacts = func(*text, contacts=contacts)
            print(result)
        if func == exit_func:
            save_contacts(file_name, contacts.to_dict())
            break


if __name__ == '__main__':

    main()
