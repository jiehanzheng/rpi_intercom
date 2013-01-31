from __future__ import print_function


def indented_print(indentation, *stuff):
  print('  '*(indentation-1), *stuff)