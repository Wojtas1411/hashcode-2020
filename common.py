from typing import List, Tuple, Any
import signal


def get_enumerated_tuple_list(lst: List[Any]) -> List[Tuple[int, Any]]:
    result = []
    for i, value in enumerate(lst):
        result.append((i, value))
    return result


class Instance:

    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            lines = list(map(lambda x: x.strip().split(' '), f.readlines()))
        self.num_books = int(lines[0][0])
        self.num_libraries = int(lines[0][1])
        self.days = int(lines[0][2])
        self.scoring = dict(get_enumerated_tuple_list(list(map(int, lines[1]))))
        self.libraries = []
        for i in range(2, len(lines) - 1, 2):
            self.libraries.append([list(map(int, lines[i])), list(map(int, lines[i + 1]))])
        self.libraries = list(
            map(lambda x: Library(x[0][0], x[0][1], x[0][2], list(map(lambda y: (y, self.scoring[y]), x[1]))),
                self.libraries))
        self.libraries = get_enumerated_tuple_list(self.libraries)

    def print(self):
        print(self.num_books, self.num_libraries, self.days)
        print(len(self.libraries))


class Library:

    def __init__(self, n: int, s: int, p: int, b: List[Tuple[int, int]]):
        self.number_of_books = n
        self.signup = s
        self.per_day = p
        self.books = b
        self.books.sort(key=lambda x: x[1], reverse=True)
        self.books_chosen_num = 0

    def print(self):
        print('N: ', self.number_of_books, '\tS: ', self.signup, '\tP: ', self.per_day)
        print(self.books)


def transform_result(result: List[Tuple[int, Library]], total_days: int) -> List[Tuple[int, List[int]]]:
    """
    Transform list of Libraries into writable result list
    """
    res = []
    start = 0
    books_scanned = set()
    for i, library in result:
        books = get_scanable_books(library, total_days, start, books_scanned)
        if not books:
            continue
        res.append((i, list(map(lambda x: x[0], books))))
        books_scanned = books_scanned.union(set(books))

        start += library.signup

    return res


def save_result(result: List[Tuple[int, List[int]]], filename: str):
    with open(filename, 'w+') as f:
        f.write(str(len(result))+'\n')
        for r in result:
            f.write(str(r[0]) + ' ' + str(len(r[1])) + '\n')
            f.write(" ".join(list(map(str, r[1]))) + '\n')


def score(libraries: List[Tuple[int, Library]], total_days: int, num_books: int = -1, num_libraries: int = -1, verbose: bool = True) -> int:
    start = 0
    sc = 0
    books_scanned = set()
    free_slots = 0
    libs_used = 0
    all_slots = 0
    for i, library in libraries:
        books = get_scanable_books(library, total_days, start, books_scanned)
        if not books:
            continue

        sc += sum(list(map(lambda x: x[1], books)))
        books_scanned = books_scanned.union(set(books))

        val = max(0, total_days - start - library.signup) * library.per_day
        all_slots += val
        free_slots += (val - len(books))

        library.books_chosen_num = len(books)
        start += library.signup
        libs_used += 1
    
    if verbose:
        if num_books > 0:
            print("Used:\t", len(books_scanned), "of", num_books, "books")
            print("Percent:\t", len(books_scanned)/num_books)
        else:
            print("Books used: \t", len(books_scanned))
        if num_libraries > 0:
            print("Used:\t", libs_used, "of", num_libraries, "libraries")
            print("Percent:\t", libs_used/num_libraries)
        else:
            print("Libraries used: \t", libs_used)
        print("Used:\t", all_slots - free_slots, "of", all_slots, "slots")
        print("Percent:\t", (all_slots - free_slots)/all_slots)

    return sc


def get_scanable_books(library: Library, total_days: int, start: int, books_scanned: set) -> list:
    days = max(0, total_days - start - library.signup)
    able_to_be_scanned = days*library.per_day
    books_to_scan = list(set(library.books).difference(books_scanned))
    books_to_scan.sort(key=lambda x: x[1], reverse=True)
    return books_to_scan[:able_to_be_scanned]


class GracefulKiller:
    kill_now = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self,signum, frame):
        print('Kill signal is bein handled, wait for iteration to finish')
        self.kill_now = True