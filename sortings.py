from typing import List, Tuple
from common import Instance, Library


# works ery best for instance C
def sort_by_setup_time_asc(libraries: List[Tuple[int, Library]]) -> List[Tuple[int, Library]]:
    libraries = libraries.copy()
    libraries.sort(key=lambda x: x[1].signup)

    return libraries

def sort_by_num_books_desc(libraries: List[Tuple[int, Library]]) -> List[Tuple[int, Library]]:
    libraries = libraries.copy()
    libraries.sort(key=lambda x: x[1].number_of_books, reverse=True)

    return libraries

def sort_by_sum_book_scores_desc(libraries: List[Tuple[int, Library]]) -> List[Tuple[int, Library]]:
    libraries = libraries.copy()
    libraries.sort(key=lambda x: sum(list(map(lambda y: y[1], x[1].books))), reverse=True)

    return libraries

def sort_by_perday_desc(libraries: List[Tuple[int, Library]]) -> List[Tuple[int, Library]]:
    libraries = libraries.copy()
    libraries.sort(key=lambda x: x[1].per_day, reverse=True)

    return libraries