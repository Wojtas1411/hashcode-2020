from multiprocessing import Pool


class Instance:

    def __init__(self, filename):
        with open(filename, 'r') as f:
            lines = list(map(lambda x: x.strip().split(' '), f.readlines()))
        self.books = int(lines[0][0])
        self.libraries = int(lines[0][1])
        self.days = int(lines[0][2])
        self.scoring = dict(list(enumerate(list(map(int, lines[1])))))
        self.library = []
        for i in range(2, len(lines)-1, 2):
            self.library.append([list(map(int, lines[i])), list(map(int, lines[i+1]))])
        self.library = list(map(lambda x: Library(x[0][0], x[0][1], x[0][2], x[1]), self.library))


class Library:

    def __init__(self, n, s, p, b):
        self.number_of_books = n
        self.signup = s
        self.perday = p
        self.books = b

    def to_string(self) -> str:
        return str(self.number_of_books) + '\t' + str(self.signup) + '\t' + str(self.perday) + '\t' + " ".join(list(map(str,self.books)))


def best_libraries(instance: Instance) -> list:
    ranking = []
    start = 0
    books_scanned = set()
    libraries_signed = list()
    while start < instance.days:
        lib_rank = []
        did_change = False
        # print(books_scanned)
        for i, library in enumerate(instance.library):
            if i in libraries_signed:
                continue
            if start + library.signup >= instance.days:
                continue
            did_change = True

            days = max(0, instance.days - library.signup - start)
            scanable = days*library.perday

            books_to_scan = list(set(library.books).difference(books_scanned))

            scored_books = list(map(lambda x: (x, instance.scoring[x]), books_to_scan))
            scored_books.sort(key=lambda x: x[1], reverse=True)
            score = sum(list(map(lambda x: x[1], scored_books[:scanable])))

            lib_rank.append((i, score))

        if not did_change:
            # print(libraries_signed)
            # print(start)
            # print(books_scanned)
            print('No change done')
            break

        lib_rank.sort(key=lambda x: x[1], reverse=True)

        chosen = instance.library[lib_rank[0][0]]
        days = max(0, instance.days - chosen.signup - start)
        scanable = days * chosen.perday

        books_to_scan = list(set(chosen.books).difference(books_scanned))
        scored_books = list(map(lambda x: (x, instance.scoring[x]), books_to_scan))
        scored_books.sort(key=lambda x: x[1], reverse=True)
        temp_books = list(map(lambda x: x[0], scored_books[:scanable]))
        # print(temp_books)

        start += chosen.signup
        ranking.append((lib_rank[0][0], temp_books))
        libraries_signed.append(lib_rank[0][0])

        books_scanned = books_scanned.union(set(temp_books))

        print(len(libraries_signed), len(instance.library))

    return ranking


def prepare_result(result: list, filename: str):
    with open(filename, 'w+') as f:
        f.write(str(len(result))+'\n')
        for r in result:
            f.write(str(r[0]) + ' ' + str(len(r[1])) + '\n')
            f.write(" ".join(list(map(str, r[1]))) + '\n')


if __name__ == '__main__':
    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    results = list(map(lambda x: (best_libraries(Instance(x)), x), files))

    # p = Pool()
    # results = list(p.map(lambda x: (best_libraries(Instance(x)), x), files))

    for r, f in results:
        prepare_result(r, f[0] + '_result.out')









