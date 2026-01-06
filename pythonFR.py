from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.core.window import Window
import sqlite3 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from sqlite3 import Error
import bcrypt
conn = sqlite3.connect('userInfo.db')


class IndexScreen(Screen):
    pass         # As it doesn't need any validation in this class, I will leave this page empty.


class SignUpScreen(Screen):
    def validatePass(self, password):
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char in "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`" for char in password):
            return False
        return True
    
    def filter(self, username):
        rude = ["vomit", "ass", "shit"]  
        for word in rude:
            if word in username.lower():
                return False
        return True

    def signup(self):
        username = self.username.text
        email = self.newEmail.text
        password = self.newPass.text
        confirm_password = self.confirmPass.text

        if not self.filter(username):
            self.ids.errorMessage.text = "Username contains inappropriate language. Please choose a different username."
            return


        if not self.validatePass(password):
            self.ids.errorMessage.text = "Password must be at least 8 characters long and contain a number and a special character."
            return
    
        if not username or not email or not password or not confirm_password:
            self.errorMessage.text = "All fields are required"
            return

        if password != confirm_password:
            self.errorMessage.text = "Passwords do not match"
            return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = sqlite3.connect('userInfo.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO userInfo (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, hashed_password))
            conn.commit()
            self.errorMessage.text = "Sign up successful!"
            self.manager.current = 'home'
        except sqlite3.IntegrityError:
            self.errorMessage.text = "Username or email already exists"
        except Exception as e:
            self.errorMessage.text = f"Eoor: {str(e)}"
        finally:
            conn.close()



class LoginScreen(Screen):
    def login(self):
        email = self.email.text
        password = self.password.text

        if not email or not password:
            self.errorMessage.text = "Please enter both email and password"
            return

        try:
            conn = sqlite3.connect('userInfo.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM userInfo WHERE email = ?', (email,))
            user = cursor.fetchone()

            if user:
                stored_hashed_password = user[3] 
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    self.errorMessage.text = "Login successful!"
                    self.manager.current = 'home'
                else:
                    self.errorMessage.text = "Invalid password, please try again."
            else:
                self.errorMessage.text = "User not found."
        except Exception as e:
            self.errorMessage.text = f"An error occurred: {str(e)}"
        finally:
            if conn:
                conn.close()


class AboutScreen(Screen):
    pass

class ForgotPassScreen(Screen):
    def resetPass(self):
        email = self.ids.email.text
        new_password = self.ids.newPass.text
        confirm_password = self.ids.confirmPass.text
        error_label = self.ids.errorMessage

        if not email:
            error_label.text = "Email cannot be empty!"
            return

        if not new_password or not confirm_password:
            error_label.text = "Password fields cannot be empty!"
            return

        if new_password != confirm_password:
            error_label.text = "Passwords do not match!"
            return

        if self.reset_password_in_backend(email, new_password):
            error_label.text = "Password reset successfully!"
        else:
            error_label.text = "Failed to reset password. Check email."

    def reset_password_in_backend(self, email, password):
        if email == "test@example.com":
            print(f"Password reset for {email}: {password}")
            return True
        return False

class ChangePassScreen(Screen):
    pass

class AccountInfoScreen(Screen):
    pass


class HomeScreen(Screen):
    pass

import sqlite3
from kivy.uix.screenmanager import Screen

class DeleteAccountScreen(Screen):
    def deleteAccount(self):
        email = self.ids.email.text
        confirmationInput = self.ids.confirmInput.text

        if confirmationInput.lower() != "delete":
            self.ids.errorMessage.text = "You need to type 'delete' to confirm."
            return

        try:
            conn = sqlite3.connect('userInfo.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM userInfo WHERE email = ?', (email,))
            if cursor.rowcount == 0:
                self.ids.errorMessage.text = "No account found"
            else:
                self.manager.current = 'index'
            conn.commit()
        except Exception as e:
            self.ids.errorMessage.text = f"Error: {str(e)}"
        finally:
            conn.close()

class WindowManager(ScreenManager):
    pass
import sqlite3
from kivy.uix.screenmanager import Screen


class User:
  def __init__(self, email, username, password):
    self.email= email
    self.username=username
    self.password=password
  @staticmethod
  def createConn():
    conn = None
    try:
      conn = sqlite3.connect('userInfo.db')
    except Error as e:
      print(e)
    return conn
  @staticmethod
  def createTable(conn):
    try:
      sql = '''CREATE TABLE userInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT ,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL,
                password TEXT NOT NULL
      )'''
      conn.execute(sql)
      print("Table created successfully")
    except Error as e:
      print(e)


def createDb():
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS recipes")
    cursor.execute('''CREATE TABLE IF NOT EXISTS recipes (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        ingredients TEXT,
                        instructions TEXT,
                        time INTEGER NOT NULL,
                        image TEXT  
                   )
                   ''')

    
    cursor.executemany('''
        INSERT INTO recipes (name, ingredients, instructions, time, image)
        VALUES (?, ?, ?, ?, ?)
    ''', [("Spaghetti", "pasta, tomato sauce", "Boil pasta, add sauce", 20, "Tomato Spaghetti.jpg"),("Salad", "lettuce, tomato, cucumber", "Mix ingredients", 10, "TLC Salad.jpg"),
        ("Pizza", "Flower 300g, tomato Sauce 50ml, 1egg", "Mix flower, egg and water and put tomato sauce on it and bake it for 30 mins", 45, "CheesePizza.jpg")
    ])
    conn.commit()
    conn.close()
createDb()


def addRecipe(name, ingredients, instructions, time, image_path):
    conn = sqlite3.connect('recipes.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO recipes (name, ingredients, instructions, time, image)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, ingredients, instructions, time, image_path))
    conn.commit()
    conn.close()

def searchRecipes(self, ingredients):
    ingredient = self.ids.search.text.strip()
    if not ingredient:
        print("No ingredient entered for search")  # Debugging print
        self.displayResults(["Please enter an ingredient to search."])
        return
    print(f"Searching for recipes with ingredient: {ingredient}")

    try:
        results = searchRecipes(ingredient)
        print(f"Raw Search results: {results}")  # Add this line to check raw output

        if results:
            formatted_results = [
                f"{recipe[0]} (Time: {recipe[3]} min)\nIngredients: {recipe[1]}\nInstructions: {recipe[2]}\n"
                for recipe in results
            ]
        else:
            formatted_results = ["No recipes found."]
    except Exception as e:
        formatted_results = [f"An error occurred: {str(e)}"]
        
    print(f"Formatted Results: {formatted_results}")  # Check the formatted results

    self.displayResults(formatted_results)

def getDbConnection(dbName):
    try:
        return sqlite3.connect(dbName)
    except Error as e:
        print(f"Database connection failed: {e}")
        return None    

class RecipeFinderScreen(Screen):
    def searchRecipes(self):
        ingredient = self.ids.search.text.strip()
        if not ingredient:
            self.displayResults(["Please enter an ingredient to search."])
            return

        try:
            conn = sqlite3.connect('recipes.db')
            cursor = conn.cursor()
            query = '''
                SELECT name, ingredients, instructions, time, image 
                FROM recipes 
                WHERE ingredients LIKE ?
            '''
            cursor.execute(query, (f"%{ingredient}%",))
            results = cursor.fetchall()
            conn.close()

            if results:
                formatted_results = [
                    (recipe[0], recipe[1], recipe[2], recipe[3], recipe[4])  # Ensure consistency
                    for recipe in results
                ]
                self.displayResults(formatted_results)
            else:
                self.displayResults(["No recipes found."])

        except Exception as e:
            self.displayResults([f"An error occurred: {str(e)}"])

    def displayResults(self, results):
        self.ids.searchResults.clear_widgets()  # Clear previous results
        for result in results:
            if isinstance(result, str):  # Error or message
                label = Label(text=result, size_hint_y=None, height=dp(40))
                self.ids.searchResults.add_widget(label)
                continue

            # Display recipe results
            name, ingredients, instructions, time, image_path = result
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(140), spacing=dp(10))

            try:
                image = Image(source=image_path or 'default_image.jpg', size_hint=(None, None), size=(dp(100), dp(100)))
            except Exception:
                image = Image(source='default_image.jpg', size_hint=(None, None), size=(dp(100), dp(100)))

            box.add_widget(image)

            label = Label(
                text=f"{name} (Time: {time} min)\nIngredients: {ingredients}\nInstructions: {instructions}",
                size_hint_y=None,
                height=dp(100),
                halign='left',
                valign='top'
            )
            box.add_widget(label)

            self.ids.searchResults.add_widget(box)


def displayResults(self, results):
    try:
        self.ids.searchResults.clear_widgets()  # Clear previous results

        for result in results:
            # Create a BoxLayout to hold the image and the text side by side
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(140), spacing=dp(10)) 

            # Check if the image file exists, and use a default image if not
            image_path = result[4]  # Assuming result[4] is the image path
            try:
                # Load the image with fixed size (100x100 dp)
                image = Image(source=image_path if image_path else 'default_image.jpg', 
                                size_hint=(None, None), size=(dp(100), dp(100)))
            except Exception as e:
                print(f"Error loading image: {e}")
                image = Image(source='default_image.jpg', size_hint=(None, None), size=(dp(100), dp(100)))

            # Add the image to the layout, aligned to the left
            box.add_widget(image)

            # Create the label for the text
            label = Label(
                text=f"{result[0]} (Time: {result[3]} min)\nIngredients: {result[1]}\nInstructions: {result[2]}",
                size_hint_y=None,
                height=dp(100),
                halign='left',  
                valign='top',   
                font_name="Impact",
                font_size=dp(14),
                color=(1, 1, 1, 1),  # White color for text
                size_hint_x=1,  # Allow the label to expand to take remaining space
            )

            label.width = self.width - dp(120)  
            # Add the label to the BoxLayout
            box.add_widget(label)

            # Add the BoxLayout containing the image and text to the results container
            self.ids.searchResults.add_widget(box)

        # Debugging output
        print(f"Results displayed: {results}")

    except Exception as e:
        print(f"Unexpected error displaying results: {e}")
    
class AddRecipeScreen(Screen):
    def addRecipe(self):
        # Retrieve input values
        recipe_name = self.ids.recipe_name.text
        recipe_ingredients = self.ids.recipe_ingredients.text
        recipe_instructions = self.ids.recipe_instructions.text
        recipe_time = self.ids.recipe_time.text
        error_label = self.ids.error_label

        # Validate inputs
        if not recipe_name:
            error_label.text = "Recipe name cannot be empty!"
            return

        if not recipe_ingredients:
            error_label.text = "Ingredients cannot be empty!"
            return

        if not recipe_instructions:
            error_label.text = "Instructions cannot be empty!"
            return

        if not recipe_time.isdigit() or int(recipe_time) <= 0:
            error_label.text = "Preparation time must be a positive number!"
            return

        # Clear error message
        error_label.text = ""

        # Simulated backend saving logic
        success = self.saveRecipeToDatabase(
            recipe_name, recipe_ingredients, recipe_instructions, recipe_time
        )

        if success:
            error_label.text = "Recipe added successfully!"
        else:
            error_label.text = "Failed to add recipe. Please try again."

    def clearFields(self):

        self.ids.recipe_name.text = ""
        self.ids.recipe_ingredients.text = ""
        self.ids.recipe_instructions.text = ""
        self.ids.recipe_time.text = ""
        self.ids.error_label.text = ""

    def saveRecipeToDatabase(self, name, ingredients, instructions, time):
        """
        Simulates saving recipe data to a database or backend.
        Replace this with your actual backend logic.
        """
        print("Saving recipe:")
        print(f"Name: {name}")
        print(f"Ingredients: {ingredients}")
        print(f"Instructions: {instructions}")
        print(f"Preparation Time: {time} minutes")
        return True


from datetime import datetime, timedelta

class FridgeScreen(Screen):
    foodData = {
        "milk": {"category": "Dairy", "expiry_range": [7]},
        "egg": {"category": "Dairy", "expiry_range": [21]},
        "chicken": {"category": "Meat", "expiry_range": [3, 5]},
        "fish": {"category": "Seafood", "expiry_range": [3]},
        "apple": {"category": "Fruit", "expiry_range": [30]},
        "bread": {"category": "Bakery", "expiry_range": [7]},
    }

    def recommendFields(self, item_name):
        item_name_lower = item_name.lower()
        recommendation_label = self.ids.recommendation_label
        food_category = self.ids.food_category
        suggested_dates_container = self.ids.suggested_dates_container
        suggested_dates_container.clear_widgets()

        found = False  # Flag to check if item is there
        for keyword, info in self.foodData.items():
            if keyword == item_name_lower:
                found = True
                food_category.text = info["category"]
                expiry_suggestions = []

                for days in info["expiry_range"]:
                    suggested_date = datetime.now() + timedelta(days=days)
                    expiry_suggestions.append(suggested_date.strftime("%d/%m/%y"))

                recommendation_label.text = f"Suggested category: {info['category']} | Expiry range: {info['expiry_range']} days"

                for date in expiry_suggestions:
                    btn = Button(
                        text=f"Is the expiry date: {date}?",
                        size_hint_y=None,
                        height=dp(40)
                    )
                    btn.bind(on_press=partial(self.setExpiryDate, date))  
                    suggested_dates_container.add_widget(btn)

                break

        if not found:
            recommendation_label.text = "No recomendations available for this item."

    def setExpiryDate(self, date):
        self.ids.item_expiry.text = date

    def addItem(self):
        item_name = self.ids.item_name.text
        item_amount = self.ids.item_amount.text
        item_expiry = self.ids.item_expiry.text
        food_category = self.ids.food_category.text

        if item_name and item_amount and item_expiry and food_category:
            print(f"Added: {item_name}, {item_amount}, {item_expiry}, {food_category}")
            self.ids.successText.text = "Item successfully added!"  # outpt success message
        else:
            print("Please fill in all fields before adding.")
            self.ids.successText.text = "Please fill in all fields before adding."  # Show error message if fields are missing

    def clearFields(self):
    #to clear the input field for user to enter next recipes.
        self.ids.item_name.text = ""
        self.ids.item_amount.text = ""
        self.ids.item_expiry.text = ""
        self.ids.food_category.text = ""
        self.ids.recommendation_label.text = ""
        self.ids.suggested_dates_container.clear_widgets()
        self.ids.successText.text = ""


kv = Builder.load_file("kivyFR.kv")

class myApp(App):  #myApp is inheriting the superclass attributes App
    def build(self): #build creates the class
        return kv

if __name__ == '__main__':
    conn = User.createConn()  
    if conn is not None:
        User.createTable(conn)
    try:
        app = myApp()
        app.run()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
