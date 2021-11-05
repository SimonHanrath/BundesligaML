"""
Add your GUI code here.
"""
import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.base import runTouchApp
from kivy.uix.spinner import Spinner
from kivy.lang import Builder
from kivy.uix.widget import Widget

def window():
    """
    class MyGridLayout(GridLayout):
        spinner = Spinner(
            # default value shown
            text='Home',
            # available values
            values=('Home', 'Work', 'Other', 'Custom'),
            # just for positioning in our example
            size_hint=(None, None),
            size=(100, 44),
            pos_hint={'center_x': .5, 'center_y': .5})

       def show_selected_value(spinner, text):
            print('The spinner', spinner, 'has text', text)

        spinner.bind(text=show_selected_value)

        runTouchApp(spinner)

       def __init__(self, **kwargs):
            #Call grid layout constructor
            super(MyGridLayout, self).__init__(**kwargs)
            
            #Set columns
            self.cols = 2
            
            # Create a Button for training
            self.training = Button(text="Start Training", font_size=32)
            self.add_widget(self.training)
            # Create a Button for the crawler
            self.crawler = Button(text="Crawler", font_size=32)
            self.add_widget(self.crawler)
            
            # Create a Button for the Winn percentage
            self.win = Button(text="Show Win percentage", font_size=32)
            self.add_widget(self.win)
    """
    #Designate the .kv design file 
    Builder.load_file('guikivy.kv')
    
    
    class MyLayout(Widget):
        pass
    
    
    
    class MyApp(App):
        def build(self):
            return MyLayout()

    
    if __name__ == 'teamproject.gui':
        MyApp().run()

from teamproject.crawler import fetch_data
from teamproject.models import ExperienceAlwaysWins


def main():
    """
    Creates and shows the main window.
    """
    # Add code here to create and initialize window.
    window()



   # For demo purposes, this is how you could access methods from other
    # modules:
    data = fetch_data()
    model = ExperienceAlwaysWins(data)
    winner = model.predict_winner('Tübingen', 'Leverkusen')
    print(winner)
