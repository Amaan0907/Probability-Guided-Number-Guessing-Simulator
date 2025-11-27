# 🎯 Probability-Guided Number Guessing Game

A command-line number-guessing game written in Python.
The game randomly selects a secret number, and the player must guess it within a limited number of attempts.
The game provides helpful hints (Higher / Lower) and dynamically updates the suggested range.

-----------

## 📌 Features

* 🔢 Random secret number generation
* 🎛 Adjustable max range and attempts
* 📁 Optional JSON config file
* 📉 Range updates after each guess
* ❗ Input validation
* 🎉 Win/lose message

---------

## 🚀 How to Run

### 1. Install Python (if needed)

Ensure you have ""Python 3.6 or newer" installed.

### 2. Run the script

python perfect_guess.py


## ⚙️ Command-Line Arguments

You can customize the game using command-line flags:

| Argument     | Description                             | Example                  |
| ------------ | --------------------------------------- | ------------------------ |
|  --max       | Maximum number the secret number can be |   --max 500              |
|  --attempts  | Number of attempts the player gets      |   --attempts 10          |
|  --config    | Path to a JSON config file              |  --config settings.json  |

Example:


```python perfect_guess.py --max 200 --attempts 8```


----------

## 🕹 How to Play

1. The game chooses a secret number between **1** and **max_range**
2. You guess a number
3. The game tells you:

   * `"Higher number please"` if you're too low
   * `"Lower number please"` if you're too high
4. Your available range updates
5. Keep guessing until:

   * 🎉 You get it right
   * ❌ You run out of attempts

----------

## 📜 Example Gameplay

```
Attempt: 1/5
Range: 1 to 100
Guess a number: 50
Lower number please
Updated range: 1 to 49
```

---------

## 🛠 Requirements

* Python 3.6 or newer
* No external dependencies

---------

## 🤝 Contributing

Feel free to submit improvements, bug fixes, or enhancements!

---------

## 📄 License

This project is open-source and free to use.

---------

## ✍️ Author

* Amaan
* Nandini
