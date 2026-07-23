from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
import screens
from interfaces import DBInterface
from platformdirs import PlatformDirs
from textual import log


class KernelCli(App):
    CSS_PATH = 'styles.tcss'
    SCREENS = {
      'main': screens.MainScreen, 
      'new_project': screens.NewScreen, 
      'questions': screens.QuestionScreen, 
      'pitch': screens.NewPitchScreen, 
      # 'chat': screens.ChatScreen, 
      'mockup': screens.MockupScreen, 
      'menu': screens.MenuScreen, 
      'settings': screens.SettingsScreen,
      'start': screens.StartScreen
    }
    CURRENT_KERNEL_ID = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dirs = PlatformDirs("StartupBuddy", "TorresCorp")
        self.db = DBInterface(self.dirs.user_data_dir)
        self.business_answers = None

    def confirm_new_project_name(self, project):
        new_id = self.db.create_new_project(project["name"], project["folder"])
        self.CURRENT_KERNEL_ID = new_id
        log(f"Current id is {self.CURRENT_KERNEL_ID}")
        # self.push_screen('questions', self.business_questions_answered)
        self.push_screen('menu')
  

    def pitch_created(self, pitch_status):
        pass

    

    def business_questions_answered(self, answers):
        log(f"business answers are {answers}")
        self.business_answers = {
          'business_idea': answers[0],
          'the_problem': answers[1],
          'the_insight': answers[2], 
          'traction': answers[3], 
          'business_model': answers[4], 
          'the_team': answers[5], 
          'the_ask': answers[6]
        }
        if self.CURRENT_KERNEL_ID is not None:
            self.db.update_project(self.CURRENT_KERNEL_ID, {"business_answers": self.business_answers})
        self.push_screen('menu')
        
    def check_main_selection(self, selection):
        log("In the check_main_selection")
        if not isinstance(selection, tuple):
            return
        log(f"inside of main selection. select_id is {selection[1]}")
        if selection[1] == 1:
            self.push_screen('new_project', self.confirm_new_project_name)
        else:
            self.CURRENT_KERNEL_ID = selection[1]
            log(f"Current id is {self.CURRENT_KERNEL_ID}")
            self.push_screen('menu')

    def on_mount(self):
        self.push_screen('start')
        # self.push_screen('main', self.check_main_selection)
    
    

if __name__ == "__main__":
    app = KernelCli()
    app.run()