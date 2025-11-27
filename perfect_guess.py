import random
import argparse

import json


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading JSON:", e)
        return {}

def get_args():
    parser = argparse.ArgumentParser(description="Probability Guided Guessing Number")

    parser.add_argument("--max", type=int, help="Maximum range of Number")
    parser.add_argument("--attempts", type=int, help="MAximum Number Of Attempts")
    parser.add_argument("--config", type=str, help="Path to JSON Config")
    

    return parser.parse_args()



def game_logic(max_range,attempts):
    sec_num= random.randint(1,max_range)
    low,high=1,max_range
    a=-1
    guesses=1
    for attempt in range(1,attempts+1):
        print(f"\n Attempts:-{attempt}/{attempts} ")
        print(f"Range {low} to {high}")

        a=int(input("Guess a number:- "))
        if a == sec_num:
            print("\n🎉 Correct! You guessed the number!")
            print("Correct guess")
            return
        if(a>sec_num):
            print("Lower number please")
            guesses +=1
        elif(a<sec_num):
            print("Higher number please")
            guesses +=1
        print(f"Updated range:- {low} to {high}")

    print(f"\n❌ Out of attempts! The number was: {sec_num}")
    print("Game over – user failed")

def main():
     args=get_args()
     config = load_json(args.config) if args.config else {}

     max_range=args.max or config.get("max_range",100)
     attempts=args.attempts or config.get("attempts",5)
    
     game_logic(max_range,attempts)


if __name__=="__main__":
     main()
