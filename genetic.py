from typing import List, Tuple
from random import shuffle
from copy import copy,deepcopy
from multiprocessing import Pool

class Instance:

    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            lines = list(map(lambda x: x.strip().split(' '), f.readlines()))
        self.books = int(lines[0][0])
        self.num_libraries = int(lines[0][1])
        self.days = int(lines[0][2])
        self.scoring = dict(list(enumerate(list(map(int, lines[1])))))
        self.libraries = []
        for i in range(2, len(lines)-1, 2):
            self.libraries.append([list(map(int, lines[i])), list(map(int, lines[i+1]))])
        self.libraries = list(map(lambda x: Library(x[0][0], x[0][1], x[0][2], list(map(lambda y: (y, self.scoring[y]),x[1]))), self.libraries))
        self.libraries = list(enumerate(self.libraries))
    
    def print(self):
        print(self.books, self.num_libraries, self.days)
        print(len(self.libraries))


class Library:

    books_choosen_num = 0

    def __init__(self, n: int, s: int, p: int, b: List[Tuple[int, int]]):
        self.number_of_books = n
        self.signup = s
        self.perday = p
        self.books = b
        self.books.sort(key = lambda x: x[1], reverse=True)

    def print(self):
        print('N: ',self.number_of_books, '\tS: ', self.signup, '\tP: ', self.perday)
        print(self.books)


def score(libraries: List[Tuple[int, Library]], total_days: int) -> int:
    start = 0
    score = 0
    books_scaned = set()
    for id, library in libraries:
        days_val = total_days - start - library.signup
        if days_val <= 0:
            break
        scanable = days_val * library.perday
        # TODO obejść jakoś kasowanie zbędnych i ponowne sortowanie
        # teoretycznie można sprawdzać czy dany element istnieje w zbiorze i kasować
        # pytanie co zajmuje więcej czasu
        books = list(set(library.books).difference(books_scaned))
        if not books:
            continue
        books.sort(key=lambda x: x[1], reverse=True)

        score += sum(list(map(lambda x: x[1], books[:scanable])))
        books_scaned = books_scaned.union(set(books[:scanable]))
        library.books_choosen_num = len(books[:scanable])
        start += library.signup
        # print(scanable, library.books_choosen_num, score, len(books_scaned))
    return score


def just_shuffle(instance: Instance):
    libraries = instance.libraries.copy()
    best_libra = libraries.copy()
    best_score = score(best_libra, instance.days)
    for _ in range(10**4):
        current = libraries.copy()
        shuffle(current)
        current_score = score(current, instance.days)
        # print(current_score)
        if current_score > best_score:
            best_libra = current
            best_score = current_score
            print(best_score)
    return best_libra

'''
Transform list of Libraries into writable result list
'''       
def transform_result(result: List[Tuple[int, Library]], total_days: int) -> List[Tuple[int, List[int]]]:
    res = []
    start = 0
    books_scaned = set()
    for id, library in result:
        days_val = total_days - start - library.signup
        if days_val <= 0:
            break
        scanable = days_val * library.perday
        books = list(set(library.books).difference(books_scaned))
        if not books:
            continue
        books.sort(key=lambda x: x[1], reverse=True)
        res.append(id, list(map(lambda x: x[0], books)))
        books_scaned = books_scaned.union(set(books[:scanable]))

'''
Save result to file
'''
def save_result(result: List[Tuple[int, List[int]]], filename: str):
    with open(filename, 'w+') as f:
        f.write(str(len(result))+'\n')
        for r in result:
            f.write(str(r[0]) + ' ' + str(len(r[1])) + '\n')
            f.write(" ".join(list(map(str, r[1]))) + '\n')

def just_shuffle_operation(instance: Instance):
    return transform_result(just_shuffle(instance), instance.days)

def do_nothing_operation(instance: Instance):
    return transform_result(instance.libraries.copy(), instance.days)

def perform_on_population(instance: Instance, size=16, func=do_nothing_operation):
    population = []
    for _ in range(size):
        dc = deepcopy(instance)
        population.append(dc)
    p = Pool()
    return p.map(func, population)
    

if __name__ == '__main__':

    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    file = files[2]

    instance = Instance(file)
    print(instance.books)
    print(score(instance.libraries, instance.days))
    print('--------')

    # instance.libraries[0][1].print()

    # result = just_shuffle(instance);

    results = perform_on_population(instance, size=4, func=just_shuffle)

    print('--------')
    # print(score(result, instance.days))
    print(list(map(lambda x: score(x, instance.days), results)))
    
    