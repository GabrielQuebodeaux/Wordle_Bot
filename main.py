from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import copy
import random
import time

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://www.nytimes.com/games/wordle/index.html")    
play_button_x_path = "/html/body/div[2]/div/div/div/div/div[2]/button[2]"
x_button_x_path = "//*[@id=\"help-dialog\"]/div/div/button"
board_x_path = "//*[@id=\"wordle-app-game\"]/div[1]"
key_x_path_dict = {
    "q": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[1]",
    "w": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[2]",
    "e": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[3]",
    "r": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[4]",
    "t": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[5]",
    "y": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[6]",
    "u": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[7]",
    "i": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[8]",
    "o": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[9]",
    "p": "//*[@id=\"wordle-app-game\"]/div[2]/div[1]/button[10]",
    "a": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[1]",
    "s": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[2]",
    "d": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[3]",
    "f": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[4]",
    "g": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[5]",
    "h": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[6]",
    "j": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[7]",
    "k": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[8]",
    "l": "//*[@id=\"wordle-app-game\"]/div[2]/div[2]/button[9]",
    "z": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[2]",
    "x": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[3]",
    "c": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[4]",
    "v": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[5]",
    "b": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[6]",
    "n": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[7]",
    "m": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[8]",
    "enter": "//*[@id=\"wordle-app-game\"]/div[2]/div[3]/button[1]"
}
word_bank = None
with open("word_bank.txt", "r") as file:
    word_bank = file.readlines()

def wait_for_element(XPATH: str, timeout):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, XPATH))
    )

class WordleBot:
    def __init__(self):
        self.present_letters = []
        self.unknown_letters = list(key_x_path_dict.keys())
        self.word_dict = {
            0: copy.deepcopy(self.unknown_letters),
            1: copy.deepcopy(self.unknown_letters),
            2: copy.deepcopy(self.unknown_letters),
            3: copy.deepcopy(self.unknown_letters),
            4: copy.deepcopy(self.unknown_letters)
        }
        self.word_bank = word_bank

    def solve(self):
        solved = False
        for guess in range(1, 7):
            if solved:
                break
            first = guess == 1
            word = self.choose_word(first)
            self.guess(word)
            for col in range(1, 6):
                x_path = f"//*[@id=\"wordle-app-game\"]/div[1]/div/div[{guess}]/div[{col}]/div"
                element = driver.find_element(By.XPATH, x_path)
                letter_status = element.get_attribute("data-state")
                letter = word[col - 1]
                if letter_status == "correct":
                    self.word_dict[col - 1] = [letter]
                elif letter_status == "present":
                    self.word_dict[col - 1].remove(letter)
                    self.present_letters.append(letter)
                elif letter_status == "absent":
                    for i in range(5):
                        if len(self.word_dict[i]) != 1:
                            if letter in self.word_dict[i]:
                                self.word_dict[i].remove(letter)
                if letter in self.unknown_letters:
                    self.unknown_letters.remove(letter)
            self.update_word_bank()
            for i, letter_bank in self.word_dict.items():
                if len(letter_bank) != 1:
                    solved = False
                    break
                solved = True

    def guess(self, word: str):
        for i in word:
            if i == "\n":
                break
            driver.find_element(By.XPATH, key_x_path_dict[i]).click()
        driver.find_element(By.XPATH, key_x_path_dict["enter"]).click()
        time.sleep(2)
        
    def update_word_bank(self):
        word_bank_copy = copy.deepcopy(self.word_bank)
        for word in word_bank_copy:
            for letter in self.present_letters:
                if letter not in word:
                    self.word_bank.remove(word)
                    break
            if word not in self.word_bank:
                continue
            for i, letter in enumerate(word[:-1]):
                if letter not in self.word_dict[i]:
                    self.word_bank.remove(word)
                    break
    
    def choose_word(self, first):
        # if first:
        #     return "slate"
        letter_usage = [0 for x in self.unknown_letters]
        for word in self.word_bank:
            for letter in word:
                if letter in self.unknown_letters:
                    letter_usage[self.unknown_letters.index(letter)] += 1
        word_score_table = []
        max = 0
        best = []
        for word in self.word_bank:
            score = 0
            for letter in self.unknown_letters:
                if letter in word:
                    score += letter_usage[self.unknown_letters.index(letter)]
            word_score_table.append(score)
            if score > max:
                best = [word]
                max = score
            elif score == max:
                best.append(word)
        print(best)
        print(max)
        return random.choice(best)

wait_for_element(play_button_x_path, 5)
button = driver.find_element(By.XPATH, play_button_x_path)
button.click()

wait_for_element(x_button_x_path, 5)
button = driver.find_element(By.XPATH, x_button_x_path)
button.click()

wait_for_element(board_x_path, 5)
bot = WordleBot()
bot.solve()

time.sleep(15)

driver.quit()