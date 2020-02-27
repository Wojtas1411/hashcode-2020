from multiprocessing import Pool
from typing import List, Tuple
from common import Library, Instance, save_result, transform_result, score, get_scanable_books
import argparse
from sortings import sort_by_num_books_desc, sort_by_sum_book_scores_desc, sort_by_setup_time_asc, sort_by_perday_desc


def basic(instance: Instance) -> List[Tuple[int, Library]]:
    """
    Basic `sophisticated` heuristic approach.
    Works fast except instance D
    :param instance:
    :return:
    """
    ranking = []
    start = 0
    books_scanned = set()
    libraries_signed = list()
    while start < instance.days:
        lib_rank = []
        did_change = False
        for it, library in instance.libraries:
            if it in libraries_signed:
                continue
            if start + library.signup >= instance.days:
                continue
            did_change = True

            books = get_scanable_books(library, instance.days, start, books_scanned)
            sc = sum(list(map(lambda x: x[1], books)))

            lib_rank.append((it, sc))

        if not did_change:
            print('No change done')
            break

        lib_rank.sort(key=lambda x: x[1], reverse=True)

        chosen = instance.libraries[lib_rank[0][0]]

        temp_books = get_scanable_books(chosen[1], instance.days, start, books_scanned)
        books_scanned = books_scanned.union(set(temp_books))

        start += chosen[1].signup
        ranking.append(chosen)
        libraries_signed.append(lib_rank[0][0])

    return ranking


def do_basic(filename: str):
    instance = Instance('input/' + filename)
    result = basic(instance)
    print(filename[0], score(result, instance.days))
    save_result(transform_result(result, instance.days), 'output/' + filename[0] + '_result.out')


if __name__ == '__main__':
    files = ['a_example.txt',
             'b_read_on.txt',
             'c_incunabula.txt',
             'd_tough_choices.txt',
             'e_so_many_books.txt',
             'f_libraries_of_the_world.txt']
    
    parser = argparse.ArgumentParser(description="Basic algorithm to solve problem from round 1 of Google Hashcode 2020 competition")
    parser.add_argument('instance', type=str, choices=['a', 'b', 'c', 'd', 'e', 'f'], 
        help='Select instance to compute')
    args = parser.parse_args()

    index = ord(args.instance) - ord('a')

    file = files[index]

    i = Instance('input/' + file)

    r1 = sort_by_sum_book_scores_desc(i.libraries)
    r2 = sort_by_num_books_desc(i.libraries)
    r3 = sort_by_setup_time_asc(i.libraries)
    r4 = sort_by_perday_desc(i.libraries)

    print("Sum of books desc:\t", score(r1,i.days, i.num_books, i.num_libraries))
    print("Number of books desc:\t", score(r2,i.days, i.num_books, i.num_libraries))
    print("Setup time asc:\t", score(r3,i.days, i.num_books,i.num_libraries))
    print("Perday desc:\t", score(r4, i.days, i.num_books, i.num_libraries))

    # print(score(r, i.days, i.num_books, i.num_libraries))
    
    # t = transform_result(r, i.days)
    # save_result(t, 'output/' + file[0] + '_basic.out')
    print('Done')
