from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.image import Image, AsyncImage
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import RiseInTransition
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from datetime import datetime, timedelta
from time import strftime
from twilio.rest import Client

class LoginWindow(Screen):

    user_phone = ObjectProperty(None)
    wrong_num = ObjectProperty('')

    def create_btn(self):
        '''move to 'create' window'''
        sm.current = 'create'

    def login_btn(self):
        '''check if phone number in accounts file and log-in'''
        if self.user_phone.text.isdigit() and len(self.user_phone.text)==10:
            global glb_user_name
            global glb_user_phone
            user_name= None
            with open('accounts', 'r') as f:
                for line in f:
                    if self.user_phone.text in line.split(',')[1]:
                        user_name= line.split(',')[0]
            if user_name != None:
                glb_user_name = user_name
                glb_user_phone = self.user_phone.text
                sm.add_widget(HomePage(name='home'))
                sm.current='home'
            else:
                self.wrong_num = 'Unknown phone number, you don\'t have an account? sign in!'
        else:
            self.wrong_num = 'Invalid phone number'
            self.user_phone.text=''
class CreateAccount(Screen):

    user_name = ObjectProperty(None)
    user_phone = ObjectProperty(None)
    wrong_num = ObjectProperty('')

    def go_back_btn(self):
        ''''''
        sm.current= 'login'

    def sign_btn(self):
        '''Add name and phone to account file'''
        phone= self.user_phone.text
        name= self.user_name.text
        #check for valid name and phone number
        if len(phone)==10 and phone[0]=='0' and phone.isdigit and len(name.split(' '))>1 and name.replace(' ','').isalpha():
            with open('accounts', 'a') as f:
                f.write(f'\n{self.user_name.text},{self.user_phone.text}')
                f.close()
            sm.current='login'
        else:
            self.wrong_num = 'invalid phone number or name'
            phone=''
            name=''
class MainScreen(Screen):
    grid = ObjectProperty()

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.table= self.table_build()

    def table_build(self):
        '''
        build a weekly schedule in the format:
        weekly_sched={}: key:day, values:appointments
        day={}: key:appointments time, values: name
        weeklly_sched{day{},...}
        '''
        weekly_sched = {}
        appo_time = 20
        start_time_work_h = 11
        start_time_work_m = 30
        end_time_work_h = 19
        end_time_work_m = 00
        today = datetime.today()
        # append day to weekly schedule dictionary
        for k in range(7):
            day = {}
            d = today + timedelta(hours=24 * k)
            # append time appointment to day dictionary
            for i in range(
                    ((end_time_work_h * 60 + end_time_work_m) -
                     (start_time_work_h * 60 + start_time_work_m)) // appo_time):
                appo = str((start_time_work_h * 60 + start_time_work_m + i * appo_time) // 60) + ':' + str(
                    (start_time_work_h * 60 + start_time_work_m + i * appo_time) % 60)
                day[appo] = None        # None is default for unscheduled appointment
            weekly_sched[d.strftime('%a,%d/%m')] = day
        print(weekly_sched)
        return weekly_sched

    def main(self):
        '''
        Make day in weekly schedule to tab,
        if owner:
        add for every tab: time appointments with user's name
        if user:
        add for every tab: empty appointments as buttons
       '''
        self.table = self.update_appos(self.table)
        for day in self.table:
            print(day)
            tab= TabbedPanelItem(text=f'{day}' ,on_press= self.appo_day_change) #add the tab
            b=ScrollView(size=(Window.width, Window.height))    #add option to scroll
            box= GridLayout(cols=1, spacing=10, size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))
            for appo in self.table[day]:
                if glb_user_name== 'owner':
                    box.add_widget(Label(text=(appo+' '+str(self.table[day][appo])), size_hint_y=None, height=40))
                else:
                    if self.table[day][appo] == None:
                        box.add_widget(Button(text=appo, size_hint_y=None, height=40, on_release= self.appo_btn))
            if None not in self.table[day].values():
                box.add_widget(Label(text='No appointments left'))
            tab.add_widget(b)
            b.add_widget(box)
            self.grid.add_widget(tab)
        return self.grid
    def update_appos(self,table):
        '''
        adjust appointments from schedule file to weekly schedule dictionary
        remove past appointments
        '''
        with open('sched','r') as f:
            s=f.readlines()
        with open('scehd', 'w') as f:
            for line in s:
                x=line.split()
                if x[0] in table.keys():
                    f.write(line)
                    table[x[0]][x[1]]=x[2]
        #remove past appointments
        time_now = strftime('%H:%M')
        today = strftime('%a,%d/%m')
        for appo in self.table[today]:
            if ((int(appo[:2]) < int(time_now[:2])+1) and (self.table[today][appo] == None)):
                table[today][appo] = ''
        return table
    def appo_day_change(self,day):
        self.appo_day = day

    def get_name(self):
        '''get user's name'''
        return glb_user_name

    def appo_btn(self,appo):
        ''' raise pop-up window to confirm appointments '''
        self.appo_time=appo
        layout = GridLayout(cols=1)
        confirm_btn = Button(text= 'confirm', size_hint=(1,.3), background_color='green')
        back_btn_ = Button(text='go back', size_hint=(1, .3))
        layout.add_widget(Label(text="Make an appointment?"))
        layout.add_widget(Label(text= f'{self.appo_day.text},  {appo.text}'))
        layout.add_widget(confirm_btn)
        layout.add_widget(back_btn_)
        self.popup = Popup( title='confirm', title_align='center' ,content=layout, size_hint=(None, None), size=(400, 400))
        self.popup.open()
        confirm_btn.bind(on_press= self.appo_confirm)
        back_btn_.bind(on_press= self.popup.dismiss)
        return
    def appo_confirm(self,x):
        '''add time appointment and name to schedule file'''
        self.popup.dismiss()
        with open('sched','a') as f:
            f.write(f'{self.appo_day.text} {self.appo_time.text} {glb_user_name}\n')
        #self.send_sms()    # activate when fix twillio details
        sm.remove_widget(sm.get_screen(name='home'))
        sm.add_widget(HomePage(name='home'))
        sm.current = 'home'
        return

    def send_sms(self):
        '''send SMS to user with appointment's details through'''
        import SMS
        '''
        # in SMS file :
        account_sid = '***'
        auth_token = '****'
        twilio_phone_number = '****'
        ####this variables censored for privacy####
        '''
        client = Client(SMS.account_sid, SMS.auth_token)  # connect to twilio account
        client.messages.create(
            body=f'\nHey {glb_user_name} you made an appointment in {self.appo_day.text} at {self.appo_time.text}',
            from_=SMS.twilio_phone_number,
            to= '+972'+glb_user_phone[1:])
        return

    def go_back(self):
        sm.current='home'

class HomePage(Screen):

    def home(self):
        ''' returns list of user appointments'''
        appos=[]
        name=''
        with open('sched','r') as f:
            for line in f:
                x=line.split()
                if x[2]+' '+x[3] == glb_user_name:
                    appos.append((x[0],x[1]))
        print(appos)
        return appos

    def make_appo_btn(self):
        '''move to main window'''
        sm.current='main'
        return

    def get_name(self):
        '''return user's name'''
        return glb_user_name
    def restart(self):
        '''remove and add widget to refresh appointments list'''
        self.parent.remove_widget(self)
        sm.add_widget(HomePage(name='home'))
        sm.current = 'home'
        return

    def cancel_pop(self,day,time):
        ''' raise pop-up window to confirm canceling'''
        layout = GridLayout(cols=1)
        confirm_btn = Button(text='confirm', size_hint=(1, .3), background_color='green')
        back_btn = Button(text='go back', size_hint=(1, .3))
        layout.add_widget(Label(text="Cancel appointment?"))
        layout.add_widget(Label(text= f'{day} ; {time}'))
        layout.add_widget(confirm_btn)
        layout.add_widget(back_btn)
        self.popup = Popup(title='confirm', title_align='center', content=layout, size_hint=(None, None),size=(400, 400))
        self.popup.open()
        confirm_btn.bind(on_press=lambda *args: self.cancel_appo(day,time))
        back_btn.bind(on_press= self.popup.dismiss)
        return
    def cancel_appo(self,day,time):
        ''' remove appointment from schedule file'''
        self.popup.dismiss()
        with open('sched','r') as f:
            s=f.readlines()
        with open('sched', 'w') as f:
            for line in s:
                x=line.split()
                if ((x[0] != day) or (x[1] != time)):
                    f.write(line)
        self.restart()
        return
class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("my.kv")
sm = WindowManager(transition = RiseInTransition())
#add screens to manager
screens = [LoginWindow(name="login"), CreateAccount(name="create"), MainScreen(name='main')]
for screen in screens:
    sm.add_widget(screen)
class Appointment_scheduling_appApp(App):
    def build(self):
        self.icon='logo.png'
        return sm

if __name__ == "__main__":
    Appointment_scheduling_appApp().run()