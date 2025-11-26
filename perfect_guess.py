import random

def game():
     max_range=int(input("Enter the maximum range you want to take:- "))
     sec_num= random.randint(1,max_range)
     
     low,high=1,max_range
     guess=-1
     guesses=1
     attempts=int(input("Enter the no. of Attempts:- "))
     for attempt in range(1,attempts+1):

          remaining=high-low+1
          probability=round(((1/remaining)*100),2)

          print(f"\nAttempts:- {attempt}/{attempts}")
          print(f"Current Range:- {low} to {high}")
          print(f"Probablity to guess No. in new range:- {probability}%")
          
          
          guess=input("\nGuess guess number:- ")
          if not guess.isdigit():
               print("Invalid input! please enter guess number")
               continue
          guess=int(guess)
          if(guess==sec_num):
               print(f"Congrats🎉 Guessed Correctly!")
               print(f"Number is {sec_num}")
               return
          if(guess>sec_num):
               print("Lower number please")
               if guess-1<high:
                    high=guess-1
               guesses +=1
          elif(guess<sec_num):
               print("Higher number please")
               if guess+1>low:
                    low=guess+1
               guesses +=1
               

game()
              