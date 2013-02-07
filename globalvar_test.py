import time
# from multiprocessing import Process
from threading import Thread


a = 0

def main():
  global a

  while True:
    time.sleep(1)
    a = a + 1
    print a


def override_a():
  print "overriding a"

  global a
  a = 0


def let_override_a_run():
  while True:
    time.sleep(2)
    override_a()


if __name__ == "__main__":
  the_thing = Thread(target=let_override_a_run)
  the_thing.start()

  main()