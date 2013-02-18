from threading import Thread
import time


def main():
  thread = Thread(target=call_me_maybe)
  thread.start()

  while True:
    print "Going to sleep..."
    time.sleep(10)
    print "Wake up..."


def hello_world():
  print "Hello world!"


def call_me_maybe():
  while True:
    time.sleep(1)
    hello_world()


if __name__ == "__main__":
  main()
