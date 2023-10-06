from util import *
from apis import *

api = SHU24hAPI()   # Use previous session
# api = SHU24hAPI(username, encryptPass(password))

def executer(fn):
    while True:
        try:
            data = fn()
            sleep(10)
        except InvalidBookingError as e:
            print("Invalid booking parameters! Please check your input.")
            print(e)
            return
        except NetworkError as e:
            print("Network error:",e)
            continue
        except RecentFailCooldown as e:
            print(e)
            # If previous reserved the same seat, then you might want to chage the seat.
            # Or you can just try again.
            print("Next action after 1 seconds...")
            sleep(1)
            continue
        except TooManyRequests as e:
            print(e)
            print("Next action after 1 seconds...")
            sleep(1)
            continue
        except CannotBookYetError as e:
            print(e)
            # It might not be 20:00 yet or you should check your param.
            print("Next action after 1 seconds...")
            sleep(1)
            continue
        except ConflictError as e:
            print(e)
            # Its up to you to decide whether to continue or not. No need to sleep if you try another seat.
            # If you want to try the same seat, you should sleep for 15s.
            return
        except Exception as e:
            print(e)
            # Unrecognized error
            return
        print(data)
        print("Next action after 10 seconds...")
        sleep(10)

# write your own tasks here
def task1():
    return api.bookSeat("B-123",*checktimelength("11:00","19:00",1))

def task2():
    return api.bookSeat("B-123",*checktimelength("19:00","24:00",1))

executer(task1)
executer(task2)
