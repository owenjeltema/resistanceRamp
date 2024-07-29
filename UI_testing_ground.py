from kivy.config import Config

Config.set('graphics', 'minimum_width', 450)
Config.set('graphics', 'minimum_height', 300)
Config.set('graphics', 'resizable', True)

import figures as fig
from yearlyCalendar import Calendar
from customKivy import CustomLabel,LayeredButton,ImageButton,RoundedButton,NavigationButton
from time import localtime,time
from random import randint
from itertools import chain

from kivymd.app import MDApp
from kivymd.uix.button import *
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Triangle, RoundedRectangle
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors.hover_behavior import HoverBehavior

calendar = Calendar(2000,51)

class TopRibbon(Widget):
    def __init__(self,ribbonHeight,ribbonColor,textColor = (.3,.3,.3,1), staticBool = True,smallImageSize = .3,smallImageBuffer = .1, **kwargs):
        super(TopRibbon, self).__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.ribbonHeight = ribbonHeight
        self.smallImageSize = smallImageSize
        self.smallImagePos = 1 - smallImageBuffer - smallImageSize/2
        self.smallImageBuffer = smallImageBuffer

        self.staticHeight = staticBool
        self.staticSize = Window.height*ribbonHeight

        self.unreadMessages = 1

        self.navigationButtons = {
            'Organization' : 'OrganizationScreen',
            'People' : 'EmployeeScreen',
            'Stores' : 'StoresScreen',
            'Analytics' : 'AnalyticsScreen',
            'Calendar' : 'CalendarScreen'
        }
        
        with self.canvas:
            self.color = Color(*ribbonColor)
            self.rectangle = Rectangle(
                pos=(0, Window.height * (1-ribbonHeight/2)),
                size=(Window.width,Window.height*ribbonHeight)
            )

        self.layout = BoxLayout(
            size=(Window.width,.4*ribbonHeight),
            pos = (0,Window.height*(1-ribbonHeight))
        )
        self.navigationWidgets = []

        for button,screen in self.navigationButtons.items():
            self.navigationWidgets.append(
                NavigationButton(
                    text = button,
                    background_color = (0,0,0,0),
                    color = textColor,
                    font_size = ribbonHeight*.15*Window.height
                )
            )
            self.layout.add_widget(self.navigationWidgets[-1])
            self.navigationWidgets[-1].bind(on_release=lambda instance: self.getScreen("dashboard"))

        self.floatLayout = FloatLayout(
            pos = self.rectangle.pos,
            size = self.rectangle.size
        )

        self.orgButton = ImageButton(
            source = "cf-logo_v2-5ffefd3d86ea7.png",
            pos_hint = {'center_x' : .35*self.ribbonHeight*Window.height/Window.width,'center_y' : .65}, # (.01*Window.width,Window.height*(1-.6*ribbonHeight))
            size_hint = (.5*self.ribbonHeight*Window.height/Window.width,.5)
        )
        self.orgButton.bind(on_release=lambda instance,dashboard="dashboard": self.getScreen(dashboard))

        self.userAccountImage = ImageButton(
            source = "user_img.png",
            pos_hint = {'center_x' : 1-.35*self.ribbonHeight*Window.height/Window.width,'center_y' : self.smallImagePos},
            size_hint = (smallImageSize,smallImageSize)
        )
        self.userAccountImage.bind(on_release=lambda instance: self.getScreen("dashboard"))

        self.settingsImage = ImageButton(
            source = 'settings_image.png',
            pos_hint = {'center_x' : 1-(self.userAccountImage.size[0] + .25*self.ribbonHeight*Window.height)/Window.width,'center_y' : self.smallImagePos},
            size_hint = (smallImageSize,smallImageSize)
        )
        self.settingsImage.bind(on_release=lambda instance: self.getScreen("dashboard"))

        self.mailImage = ImageButton(
            source = 'mail_image.png',
            pos_hint = {'center_x' : 1-(self.userAccountImage.size[0] + .5*self.ribbonHeight*Window.height + .15*self.ribbonHeight*Window.height)/Window.width,'center_y' : self.smallImagePos},
            size_hint = (smallImageSize,smallImageSize)
        )
        self.mailImage.bind(on_release=lambda instance: self.getScreen("dashboard"))

        
        if self.unreadMessages > 0:
            r = .15*self.mailImage.size[0]
            self.unreadMessagesAlert = RoundedButton(
                button_color = (1,0,0,1),
                pos_hint = {'center_x' : 1-(self.userAccountImage.size[0] + .5*self.ribbonHeight*Window.height + .15*self.ribbonHeight*Window.height - .15*self.mailImage.size[0])/Window.width,'center_y' : 1.125*self.smallImagePos},
                size_hint = (None,None),
                size = (.015*self.rectangle.size[0],.015*self.rectangle.size[0]),
                radii = [r],
                font_size = .1*self.rectangle.size[1],
                text = str(self.unreadMessages)
            )
        if self.unreadMessages > 99:
            self.unreadMessagesAlert.text = '99'

        self.floatLayout.add_widget(self.orgButton)
        self.floatLayout.add_widget(self.userAccountImage)
        self.floatLayout.add_widget(self.settingsImage)
        self.floatLayout.add_widget(self.mailImage)
        try:
            self.floatLayout.add_widget(self.unreadMessagesAlert)
        except:pass

        self.add_widget(self.layout)
        self.add_widget(self.floatLayout)
    def update_rect(self, instance, value):
        if self.staticHeight:
            self.rectangle.pos = (0 ,Window.height - self.staticSize)
            self.rectangle.size = (Window.width, self.staticSize)
        else:
            self.rectangle.pos = (0, Window.height * (1-self.ribbonHeight))
            self.rectangle.size = (Window.width, Window.height * self.ribbonHeight)
        self.layout.pos = self.rectangle.pos
        self.layout.size=(Window.width,.35*self.rectangle.size[1])
        self.floatLayout.pos = self.rectangle.pos
        self.floatLayout.size = self.rectangle.size
        for button in self.navigationWidgets:
            try:
                button.font_size = self.ribbonHeight*self.rectangle.size[1]
            except:
                pass
        self.orgButton.size_hint = (self.smallImageSize,self.smallImageSize)
        self.orgButton.pos_hint = {'center_x' : self.orgButton.image_ratio*.25*self.rectangle.size[1]/Window.width,'center_y' : .65}
        
        self.userAccountImage.pos_hint = {'center_x' : 1-(.5*self.smallImageSize+self.smallImageBuffer)*self.rectangle.size[1]/Window.width,'center_y' : self.smallImagePos}
        self.userAccountImage.size_hint = (self.smallImageSize,self.smallImageSize)

        self.settingsImage.pos_hint = {'center_x' : 1-(1.5*self.smallImageSize+3*self.smallImageBuffer)*self.rectangle.size[1]/Window.width,'center_y' : self.smallImagePos}
        self.settingsImage.size_hint = (self.smallImageSize,self.smallImageSize)

        self.mailImage.pos_hint = {'center_x' : 1-(2.5*self.smallImageSize+5*self.smallImageBuffer)*self.rectangle.size[1]/Window.width,'center_y' : self.smallImagePos}
        self.mailImage.size_hint = (self.smallImageSize,self.smallImageSize)

        #try:
            #self.unreadMessagesAlert.pos_hint['center_x'] = 1-(self.userAccountImage.size[0] + .65*self.rectangle.size[1] - .15*self.mailImage.size[0])/self.rectangle.size[0]
        #self.unreadMessagesAlert.pos = (self.mailImage.pos[0],Window.height*(.94))
        self.unreadMessagesAlert.pos_hint = {'center_x' : 1-(2.5*self.smallImageSize+5*self.smallImageBuffer - .5*self.smallImageSize)*self.rectangle.size[1]/self.rectangle.size[0],'center_y' : self.smallImagePos + self.smallImageSize/3}
        #except:pass
    def getScreen(self,screen):
        self.parent.manager.current=screen
class BottomRibbon(Widget):
    def __init__(self,ribbonHeight,ribbonColor,textColor = (.3,.3,.3,1), staticBool = True, **kwargs):
        super(BottomRibbon, self).__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.staticHeight = staticBool
        self.ribbonSize = ribbonHeight*Window.height
        self.ribbonHeight = ribbonHeight
        
        with self.canvas:
            self.color = Color(*ribbonColor)
            self.rectangle = Rectangle(pos=(0, 0),size=(Window.width,Window.height*self.ribbonHeight))

        self.layout = FloatLayout(
            pos = self.rectangle.pos,
            size = self.rectangle.size
        )
        
        if localtime().tm_hour < 12:
            presentTimeSuffix = ' AM'
        else:
            presentTimeSuffix = ' PM'
        if localtime().tm_min < 10:
            if localtime().tm_hour % 12 == 0:
                presentTime = '12:' + '0' + str(localtime().tm_min) + presentTimeSuffix
            else:
                presentTime = str(localtime().tm_hour % 12) + ':' + '0' + str(localtime().tm_min) + presentTimeSuffix
        else:
            if localtime().tm_hour % 12 == 0:
                presentTime = '12:' + str(localtime().tm_min) + presentTimeSuffix
            else:
                presentTime = str(localtime().tm_hour % 12) + ':' + str(localtime().tm_min) + presentTimeSuffix
        presentTime = presentTime + '\n' + str(localtime().tm_mon) + '/' + str(localtime().tm_mday) + '/' + str(localtime().tm_year)

        self.timeLabel = Label(
            text = presentTime,
            color = textColor,
            halign = 'right',
            pos_hint = {"center_x" : 1-ribbonHeight,"center_y" : .5},
            size = (1.8*self.ribbonSize,self.ribbonSize),
            font_size = .3*self.ribbonSize
        )
        self.layout.add_widget(self.timeLabel)
        self.add_widget(self.layout)
        Clock.schedule_interval(self.time_update, 1)
    def update_rect(self, instance, value):
        self.rectangle.pos = (0, 0)
        if self.staticHeight:
            self.rectangle.size = (Window.width, self.ribbonSize)
        else:
            self.rectangle.size = (Window.width, Window.height * self.ribbonHeight)
        self.layout.pos = self.rectangle.pos
        self.layout.size = self.rectangle.size
        self.timeLabel.size = (1.8*self.ribbonSize,self.rectangle.size[1])
        self.timeLabel.font_size = .3*self.rectangle.size[1]
        self.timeLabel.pos_hint = {'center_x' : 1-2.6*self.timeLabel.font_size/self.rectangle.size[0],"center_y" : .5}
    def time_update(self,instance):
        if localtime().tm_hour < 12:
            presentTimeSuffix = ' AM'
        else:
            presentTimeSuffix = ' PM'
        if localtime().tm_min < 10:
            if localtime().tm_hour % 12 == 0:
                presentTime = '12:' + '0' + str(localtime().tm_min) + presentTimeSuffix
            else:
                presentTime = str(localtime().tm_hour % 12) + ':' + '0' + str(localtime().tm_min) + presentTimeSuffix
        else:
            if localtime().tm_hour % 12 == 0:
                presentTime = '12:' + str(localtime().tm_min) + presentTimeSuffix
            else:
                presentTime = str(localtime().tm_hour % 12) + ':' + str(localtime().tm_min) + presentTimeSuffix
        presentTime = presentTime + '\n' + str(localtime().tm_mon) + '/' + str(localtime().tm_mday) + '/' + str(localtime().tm_year)
        self.timeLabel.text = presentTime
class ScreenBuilder(Widget):
    def __init__(self,topRibbonHeight:float, bottomRibbonHeight:float,screen,staticBuffers = False,baseColor = (.8,.8,.8,1),sideBuffer = .05, topBuffer = 0, textColor = (.3,.3,.3,1), **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_rect, size=self.update_rect)
        self.screen = screen

        self.textColor = textColor
        self.staticBuffers = staticBuffers
        self.topRibbonHeight = topRibbonHeight*Window.height
        self.bottomRibbonHeight = bottomRibbonHeight*Window.height
        self.topBuffer = topBuffer
        self.sideBuffer = sideBuffer
        self.screenBottomBuffer = self.bottomRibbonHeight + Window.height*topBuffer
        self.screenTopBuffer = self.topRibbonHeight + Window.height*topBuffer
        self.screenSideBuffer = sideBuffer*Window.width
        self.screenBottomBuffer = self.bottomRibbonHeight + Window.height*topBuffer
        self.screenTopBuffer = self.topRibbonHeight + Window.height*topBuffer
        self.screenSideBuffer = sideBuffer*Window.width
        self.color = baseColor

        with self.canvas:
            Color(*baseColor)
            self.rectangle = Rectangle(
                pos=(self.screenSideBuffer, self.screenBottomBuffer),
                size = (Window.width-2*self.screenSideBuffer,Window.height - self.screenTopBuffer - self.screenBottomBuffer)
            )
        
        self.layout = FloatLayout(
            size = self.rectangle.size,
            pos = self.rectangle.pos
        )
    def update_rect(self,instance,value):
        if not self.staticBuffers:
            self.screenBottomBuffer = self.bottomRibbonHeight + Window.height*self.topBuffer
            self.screenTopBuffer = self.topRibbonHeight + Window.height*self.topBuffer
            self.screenSideBuffer = self.sideBuffer*Window.width
        self.rectangle.pos = (self.screenSideBuffer, self.screenBottomBuffer)
        self.rectangle.size = (Window.width-2*self.screenSideBuffer,Window.height - self.screenTopBuffer - self.screenBottomBuffer)
        self.layout.size = self.rectangle.size
        self.layout.pos = self.rectangle.pos
class NormalScreen(Screen):
    def __init__(self, ribbonColor,topRibbonHeight = 0.15, bottomRibbonHeight = 0.05, textColor = (.3,.3,.3,1), **kw):
        super(NormalScreen,self).__init__(**kw)
        self.ribbonColor = ribbonColor
        self.topRibbonHeight = topRibbonHeight
        self.bottomRibbonHeight = bottomRibbonHeight
        self.textColor = textColor
    def on_enter(self):
        self.bottomRibbon = BottomRibbon(self.bottomRibbonHeight,self.ribbonColor,textColor = self.textColor)
        self.topRibbon = TopRibbon(self.topRibbonHeight,self.ribbonColor,textColor = self.textColor)
        self.add_widget(self.bottomRibbon)
        self.add_widget(self.topRibbon)
    def changeScreenBuilder(self,type:str):
        try:
            self.remove_widget(self.screenBuilder)
        except:
            pass
    def teardown(self):
        for widget in self.widgets:
            pass
class Dashboard(NormalScreen):
    def __init__(self, ribbonColor, topRibbonHeight=0.15, bottomRibbonHeight=0.05,orgBool = False, **kw):
        super().__init__(ribbonColor, topRibbonHeight, bottomRibbonHeight, **kw)
        self.orgBool  = orgBool
    def on_enter(self):
        if self.orgBool:
            self.screenBuilder = self.OrgDashBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self)
        else:
            self.screenBuilder = self.BasicDashBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self)
        self.add_widget(self.screenBuilder)
        #self.screenBuilder.figure.showFigure() #Replace with: for figure in self.screenBuilder.figures (?)
        return super().on_enter()
    def teardown(self):
        return super().teardown()
    class DashboardBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, screen,staticBuffers=False, color=(0.8, 0.8, 0.8, 0), sideBuffer=0.05, topBuffer=0.05, **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, staticBuffers=staticBuffers, baseColor=color, sideBuffer=sideBuffer, topBuffer=topBuffer, **kwargs)
            self.bind(pos=self.update_rect,size=self.update_rect)
            self.weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
            self.dayButtons = {}
            self.dayLabels = {}
            self.calendarRibbonRelativeHeight = .25
            self.calendarRibbonTitleHeight = .06
            self.calendarSpacing = 10
            r=.01*self.rectangle.size[1] # RoundedRectangle spacing
            with self.canvas:
                Color(0.6,0.6,0.6,1)
                self.calendarRectangle=RoundedRectangle(
                    pos = (self.rectangle.pos[0],self.rectangle.pos[1] + (1-self.calendarRibbonRelativeHeight)*self.rectangle.size[1]),
                    size = (self.rectangle.size[0],self.calendarRibbonRelativeHeight*self.rectangle.size[1]),
                    radius = [(r,r),(r,r),(r,r),(r,r)]
                )
            self.calendarRibbon = BoxLayout(
                pos_hint = {'center_x' : .5,'center_y' : 1-(self.calendarRibbonRelativeHeight+self.calendarRibbonTitleHeight)/2},
                size_hint = (1 - 2*self.calendarSpacing/self.rectangle.size[0],self.calendarRibbonRelativeHeight - self.calendarRibbonTitleHeight - 2*self.calendarSpacing/self.rectangle.size[1]),
                spacing = self.calendarSpacing
            )
            for day in self.weekdays:
                self.dayButtons[day] = LayeredButton(
                    background_normal = '',
                    background_color = (.7,.7,.7,1),
                    layout_pos=(.5,.375),
                    layout_size = (1,.75),
                    color=self.textColor,
                    text_size = (self.calendarRectangle.size[0]/7-self.calendarRibbon.spacing,self.calendarRectangle.size[1]*(1-self.calendarRibbonTitleHeight/self.calendarRibbonRelativeHeight)-2*self.calendarRibbon.spacing),
                    font_size = .03*self.rectangle.size[1],
                    halign='center',
                    valign='top',
                    text=day
                )
                self.dayButtons[day].boxLayout.add_widget(
                    Button(
                        background_normal='',
                        background_color=(1,1,1,.333),
                        color=self.textColor,
                        text_size = (self.calendarRectangle.size[0]/7-3*self.calendarRibbon.spacing,self.calendarRectangle.size[1]*(1-self.calendarRibbonTitleHeight)*.75*(1-self.calendarRibbonTitleHeight/self.calendarRibbonRelativeHeight)-2*self.calendarRibbon.spacing),
                        font_size=.025*self.rectangle.size[1],
                        halign='left',
                        valign = 'top'
                    )
                )
                self.calendarRibbon.add_widget(self.dayButtons[day])
            self.calendarRibbonTitle = Label(
                pos_hint = {'center_x' : .5,'center_y' : 1-(self.calendarRibbonTitleHeight + self.calendarSpacing/self.rectangle.size[1])/2},
                color = (.2,.2,.2),
                text = 'July 28 - August 3, 2024'
            )
            self.layout.add_widget(self.calendarRibbonTitle)
            for label in chain(self.dayButtons['Tuesday'].boxLayout.children,self.dayButtons['Thursday'].boxLayout.children):
                label.text = 'New Shipment'
            for label in self.dayButtons['Tuesday'].boxLayout.children:
                label.text = label.text + '\nCompany Meeting'
            self.layout.add_widget(self.calendarRibbon)
        def update_rect(self,instance,value):
            super().update_rect(instance,value)
            self.calendarRectangle.pos = (self.rectangle.pos[0],self.rectangle.pos[1] + (1-self.calendarRibbonRelativeHeight)*self.rectangle.size[1])
            self.calendarRectangle.size = (self.rectangle.size[0],self.calendarRibbonRelativeHeight*self.rectangle.size[1])
            for dayButton in self.dayButtons.values():
                dayButton.text_size = (self.calendarRectangle.size[0]/7-self.calendarRibbon.spacing,self.calendarRectangle.size[1]*(1-self.calendarRibbonTitleHeight/self.calendarRibbonRelativeHeight)-.025*self.rectangle.size[1])
                dayButton.font_size = .03*self.rectangle.size[1]
                for label in dayButton.boxLayout.children:
                    label.text_size = (self.calendarRectangle.size[0]/7-3*self.calendarRibbon.spacing,self.calendarRectangle.size[1]*(1-self.calendarRibbonTitleHeight)*.75*(1-self.calendarRibbonTitleHeight/self.calendarRibbonRelativeHeight)-.025*self.rectangle.size[1])
                    label.font_size=.025*self.rectangle.size[1]
            self.calendarRibbonTitle.font_size = .04*self.rectangle.size[1]
            '''for day in self.weekdays:
                if self.rectangle.size[0] < self.rectangle.size[1]:
                    self.dayButtons[day].font_size = self.rectangle.size[0]*.025
                else:
                    self.dayButtons[day].font_size = self.rectangle.size[1]*.025
                self.dayButtons[day].text_size = (self.rectangle.size[0]/len(self.weekdays),self.calendarRibbonRelativeHeight*self.rectangle.size[1]-3*self.calendarRibbon.spacing)'''
            '''self.figure.pos = (self.layout.pos[0],self.layout.pos[1])
            self.figure.size = (.8*self.layout.size[0],.45*self.layout.size[1])
            self.figure2.pos = (self.layout.pos[0]+.55*self.layout.size[0],self.layout.pos[1])
            self.figure2.size = (self.rectangle.size[0],.45*self.rectangle.size[1])'''
            '''for widget in self.dayButtons.values():
                for label in widget.floatLayout.children:
                    label.font_size = .03*self.rectangle.size[1]'''
    class BasicDashBuilder(DashboardBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, screen, staticBuffers=False, color=(0.8, 0.8, 0.8, 0), sideBuffer=0.05, topBuffer=0.05, **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, staticBuffers, color, sideBuffer, topBuffer, **kwargs)
            r=.01*self.rectangle.size[1] # RoundedRectangle spacing
            with self.canvas:
                Color(0.6,0.6,0.6,1)
                self.inventoryBackgroundRectangle=RoundedRectangle(
                    pos = self.rectangle.pos,
                    size = (.55*self.rectangle.size[0],.6*self.rectangle.size[1]),
                    radius = [(0,0),(0,0),(r,r),(r,r)]
                )
                self.alertsBackgroundRectangle=RoundedRectangle(
                    pos=(self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]),
                    size = (.4*self.rectangle.size[0],.6*self.rectangle.size[1]),
                    radius = [(0,0),(0,0),(r,r),(r,r)]
                )
            self.inventoryWidgetHeader = RoundedButton(
                button_color=(.65,.8,.85,1),
                pos = (self.rectangle.pos[0],self.rectangle.pos[1]+.6*self.rectangle.size[1]),
                size_hint=(.55,.1),
                radii = (.1,.1,0,0),
                color = (.2,.2,.2),
                halign='left',
                text='Inventory Sheet'
            )
            self.layout.add_widget(self.inventoryWidgetHeader)
            self.inventoryNames=['Item','Stock','Restock','Price','Runout']
            self.inventoryWidget = LayeredButton(
                background_normal = '',
                background_color=(.8,.8,.8,0),
                layout='Grid',
                pos_hint = {'center_x':.275,'center_y':.3},
                size_hint = (.95*.55,.95*.6)
            )
            self.inventoryWidget.gridLayout.spacing=(5,5)
            self.inventoryWidget.gridLayout.cols=5
            for i in range(self.inventoryWidget.gridLayout.cols):
                self.inventoryWidget.gridLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.65,.8,.85,0),
                        color=(0,0,0,1),
                        font_size = .03*self.rectangle.size[1],
                        text=self.inventoryNames[i]
                    )
                )
            for i in range(10*self.inventoryWidget.gridLayout.cols):
                tempText=str(randint(0,20))
                if (i % self.inventoryWidget.gridLayout.cols) == 0:
                    tempText = 'Item ' + str(i//self.inventoryWidget.gridLayout.cols+1)
                self.inventoryWidget.gridLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.8,.8,.8,1),
                        color=(0,0,0,1),
                        font_size=.025*self.rectangle.size[1],
                        text=tempText
                    )
                )
            self.layout.add_widget(self.inventoryWidget)
            self.alertHeader = RoundedButton(
                button_color=(.65,.8,.85,1),
                pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]+.6*self.rectangle.size[1]),
                size_hint=(.4,.1),
                radii = (.1,.1,0,0),
                color=(.2,.2,.2),
                halign='left',
                text='Alerts'
            )
            self.layout.add_widget(self.alertHeader)
            self.alertsWidget = LayeredButton(
                background_normal = '',
                background_color=(.8,.8,.8,0),
                layout_pos=(.5,.5),
                layout_size=(1,1),
                layout='Box',
                pos_hint = {'center_x':.8,'center_y':.3},
                size_hint = (None,None),
                size = (.95*.4*self.rectangle.size[0],.95*.6*self.rectangle.size[1])
            )
            self.alertsWidget.boxLayout.orientation = 'vertical'
            self.alertsWidget.boxLayout.spacing=5

            alertsText = ['Incoming shipment','Company meeting today','Message from Nate','Out of chips','Out of soda','Alert: Check drink stock','Alert: Check candy stock','','','']
            
            for i in range(10):
                self.alertsWidget.boxLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color=(.8,.8,.8,1),
                        color = (.2,.2,.2),
                        text_size = (.92*self.alertsBackgroundRectangle.size[0],None),
                        font_size = .025*self.rectangle.size[1],
                        halign = 'left',
                        text = alertsText[i]
                    )
                )
            self.layout.add_widget(self.alertsWidget)
            self.add_widget(self.layout)
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            self.inventoryBackgroundRectangle.pos = self.rectangle.pos
            self.inventoryBackgroundRectangle.size = (.55*self.rectangle.size[0],.6*self.rectangle.size[1])
            self.alertsBackgroundRectangle.pos=(self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1])
            self.alertsBackgroundRectangle.size = (.4*self.rectangle.size[0],.6*self.rectangle.size[1])
            self.inventoryWidgetHeader.pos = (self.rectangle.pos[0],self.rectangle.pos[1]+.6*self.rectangle.size[1])
            self.inventoryWidgetHeader.size_hint = (.55,.1)
            self.inventoryWidgetHeader.font_size = .045*self.rectangle.size[1]
            self.alertHeader.pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]+.6*self.rectangle.size[1])
            self.alertHeader.size_hint=(.4,.1)
            self.alertHeader.font_size = .045*self.rectangle.size[1]
            self.alertsWidget.size = (.95*.4*self.rectangle.size[0],.95*.6*self.rectangle.size[1])
            for label in self.inventoryWidget.gridLayout.children:
                if label.background_color[3] == 0:
                    label.font_size = .03*self.rectangle.size[1]
                else:
                    label.font_size = .025*self.rectangle.size[1]
            for label in self.alertsWidget.boxLayout.children:
                label.font_size =.025*self.rectangle.size[1]
                label.text_size = (.91*.4*self.rectangle.size[0],None)
    class OrgDashBuilder(DashboardBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, screen, staticBuffers=False, color=(0.8, 0.8, 0.8, 0), sideBuffer=0.05, topBuffer=0.05, **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, staticBuffers, color, sideBuffer, topBuffer, **kwargs)
            r=.01*self.rectangle.size[1] # RoundedRectangle spacing
            with self.canvas:
                Color(.6,.6,.6,1)
                self.storesRectangle = RoundedRectangle(
                    pos=self.rectangle.pos,
                    size_hint = (None,None),
                    size=(.5*self.rectangle.size[0],.6*self.rectangle.size[1]),
                    radius = [(0,0),(0,0),(r,r),(r,r)],
                    text='hi'
                )
            self.storesWidgetHeader = RoundedButton(
                button_color=(.65,.8,.85,1),
                pos = (self.rectangle.pos[0],self.rectangle.pos[1]+.6*self.rectangle.size[1]),
                size_hint=(.5,.1),
                radii = (.1,.1,0,0),
                color=self.textColor,
                halign='left',
                text='Company Stores'
            )
            self.layout.add_widget(self.storesWidgetHeader)
            self.storeColNames=['Store','Employees','Revenue','Losses']
            self.storesWidget = LayeredButton(
                background_normal = '',
                background_color=(.8,.8,.8,0),
                layout='Grid',
                pos_hint = {'center_x':.25,'center_y':.3},
                size_hint = (.95*.5,.95*.6)
            )
            self.storesWidget.gridLayout.spacing=(5,5)
            self.storesWidget.gridLayout.cols=4
            for i in range(self.storesWidget.gridLayout.cols):
                self.storesWidget.gridLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.65,.8,.85,0),
                        color=self.textColor,
                        font_size = .03*self.rectangle.size[1],
                        text=self.storeColNames[i]
                    )
                )
            for i in range(10*self.storesWidget.gridLayout.cols):
                tempText=str(randint(0,20))
                if (i % self.storesWidget.gridLayout.cols) == 0:
                    tempText = 'Store ' + str(i//self.storesWidget.gridLayout.cols+1)
                self.storesWidget.gridLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.8,.8,.8,1),
                        color=self.textColor,
                        font_size=.025*self.rectangle.size[1],
                        text=tempText
                    )
                )
            self.layout.add_widget(self.storesWidget)

            self.profitFig = fig.ScatterPlot(
                pos = (self.rectangle.pos[0] + .575*self.rectangle.size[0],self.rectangle.pos[1] + .05*self.rectangle.size[1]),
                size_hint = (None,None),
                size  =(.4*self.rectangle.size[0],.6*self.rectangle.size[1]),
                showDots = False,
                color = (.8,.8,.8,1),
                titleName = 'Total Profits'
            )
            self.layout.add_widget(self.profitFig)
            self.profitFig.showFigure()

            self.add_widget(self.layout)
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            self.storesRectangle.pos=self.rectangle.pos
            self.storesRectangle.size=(.5*self.rectangle.size[0],.6*self.rectangle.size[1])
            self.storesWidgetHeader.pos = (self.rectangle.pos[0],self.rectangle.pos[1]+.6*self.rectangle.size[1])
            self.storesWidgetHeader.size_hint=(.5,.1)
            self.profitFig.pos = (self.rectangle.pos[0] + .575*self.rectangle.size[0],self.rectangle.pos[1] + .05*self.rectangle.size[1]) # Annoying positioning bug
class OrganizationScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
class EmployeeScreen(NormalScreen):
    def __init__(self, ribbonColor, topRibbonHeight=0.15, bottomRibbonHeight=0.05, **kw):
        super().__init__(ribbonColor, topRibbonHeight, bottomRibbonHeight, **kw)
    def on_enter(self):
        super().on_enter()
        self.screenBuilder = self.EmployeeBuilder(.15,.05,self)
    class EmployeeBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, screen, staticBuffers=False, baseColor=(0.8, 0.8, 0.8, 1), sideBuffer=0.05, topBuffer=0, textColor=(0.3, 0.3, 0.3, 1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, baseColor=baseColor, **kwargs)
            self.hi = 'hi'
class AnalyticsScreen(NormalScreen):
    def __init__(self, ribbonColor, topRibbonHeight=0.15, bottomRibbonHeight=0.05, **kw):
        super().__init__(ribbonColor ,topRibbonHeight, bottomRibbonHeight, **kw)
    def on_enter(self):
        super().on_enter()
        self.screenBuilder = self.AnalyticsBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self, sideBuffer=0.05, topBuffer=0.05)
        self.add_widget(self.screenBuilder)
    def update_rect(self,instance,value):
        super().update_rect(instance,value)
    class AnalyticsBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight, bottomRibbonHeight, screen, staticBuffers=False, baseColor=(0.8, 0.8, 0.8, 0), sideBuffer=0.05, topBuffer=0, textColor=(0.3, 0.3, 0.3, 1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, staticBuffers, baseColor, sideBuffer, topBuffer, textColor, **kwargs)
            self.bind(pos=self.update_rect,size=self.update_rect)

            # Positioning
            self.spacing = 10

            self.weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
            self.dayButtons = {}
            self.dayLabels = {}
            self.calendarRibbonRelativeHeight = .2
            self.calendarSpacing = 10
            r=.01*self.rectangle.size[1] # RoundedRectangle spacing
            with self.canvas:
                Color(0.8,0.8,0.8,1)
                self.analyticsBoardBackground = RoundedRectangle(
                    pos = self.rectangle.pos,
                    size = (.55*self.rectangle.size[0],.85*self.rectangle.size[1]),
                    radius = [(0,0),(0,0),(r,r),(r,r)]
                )
                Color(.65,.8,.85)
                self.analyticsBoardHeader = RoundedRectangle(
                    pos = (self.rectangle.pos[0], self.rectangle.pos[1] + .85*self.rectangle.size[1]),
                    size = (.55*self.rectangle.size[0],.15*self.rectangle.size[1]),
                    radius = [(r,r),(r,r),(0,0),(0,0)]
                )

            self.analyticsBoardTitle = CustomLabel(
                pos_hint = {'x':0,'y':.85}, #(self.rectangle.pos[0], self.rectangle.pos[1] + .85*self.rectangle.size[1]),
                size_hint = (.25,.15), #(.25*self.rectangle.size[0],.15*self.rectangle.size[1]),
                color = (.2,.2,.2,1),
                text = 'Analytics Board'
            )
            self.layout.add_widget(self.analyticsBoardTitle)

            self.analyticsBoardButton = RoundedButton(
                button_color = (.8,.8,.8),
                pos_hint = {'center_x':.425,'center_y':.925},
                size_hint = (.2,.1),
                color = (.2,.2,.2),
                text = 'Customize'
            )
            self.layout.add_widget(self.analyticsBoardButton)

            self.analyticsBoard = BoxLayout(
                pos = (self.analyticsBoardBackground.pos[0] + self.spacing,self.analyticsBoardBackground.pos[1] + self.spacing),
                size = (self.analyticsBoardBackground.size[0] - 2*self.spacing,self.analyticsBoardBackground.size[1] - 2*self.spacing),
                orientation = 'vertical',
                spacing = 5
            )
            for i in range(5):
                self.analyticsBoard.add_widget(
                    Button(
                        text='Analytic Specifics'
                    )
                )

            self.figure = fig.Pie(
                pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]),
                size = (.4*self.rectangle.size[0],.46*self.rectangle.size[1])
            )
            self.layout.add_widget(self.figure)
            self.figure.showFigure()

            self.figure2 = fig.ScatterPlot(
                pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]+.27*self.rectangle.size[1]),
                size = (.4*self.rectangle.size[0],.46*self.rectangle.size[1])
            )
            self.layout.add_widget(self.figure2)
            self.figure2.showFigure()
            
            self.add_widget(self.analyticsBoard)
            self.add_widget(self.layout)
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            self.analyticsBoardBackground.pos = self.rectangle.pos
            self.analyticsBoardBackground.size = (.55*self.rectangle.size[0],.85*self.rectangle.size[1])
            self.analyticsBoardHeader.pos = (self.rectangle.pos[0], self.rectangle.pos[1] + .85*self.rectangle.size[1])
            self.analyticsBoardHeader.size = (.55*self.rectangle.size[0],.15*self.rectangle.size[1])
            self.analyticsBoard.pos = (self.analyticsBoardBackground.pos[0] + self.spacing,self.analyticsBoardBackground.pos[1] + self.spacing)
            self.analyticsBoard.size = (self.analyticsBoardBackground.size[0] - 2*self.spacing,self.analyticsBoardBackground.size[1] - 2*self.spacing)
            self.analyticsBoardButton.font_size = .045*self.rectangle.size[1]
            self.analyticsBoardTitle.font_size = .045*self.rectangle.size[1]
            self.figure.pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1])
            self.figure.size = (.4*self.rectangle.size[0],.46*self.rectangle.size[1])
            self.figure2.pos = (self.rectangle.pos[0]+.6*self.rectangle.size[0],self.rectangle.pos[1]+.27*self.rectangle.size[1])
            self.figure2.size = (.4*self.rectangle.size[0],.46*self.rectangle.size[1])
    class SpecificAnalyticBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, screen, staticBuffers=False, baseColor=(0.8, 0.8, 0.8, 0), sideBuffer=0.05, topBuffer=0, textColor=(0.3, 0.3, 0.3, 1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen, staticBuffers, baseColor, sideBuffer, topBuffer, textColor, **kwargs)

            # Positioning
            self.edgeSpacing = 10
            r=.01*self.rectangle.size[1]

            with self.canvas:
                Color(0.8,0.8,0.8,1)
                self.tableBackground = RoundedRectangle(
                    pos = self.rectangle.pos,
                    size = (.5*self.rectangle.size[0],.85*self.rectangle.size[1]),
                    radius = [(0,0),(0,0),(r,r),(r,r)]
                )
                Color(.65,.8,.85)
                self.tableHeader = RoundedRectangle(
                    pos = (self.rectangle.pos[0], self.rectangle.pos[1] + .85*self.rectangle.size[1]),
                    size = (.5*self.rectangle.size[0],.15*self.rectangle.size[1]),
                    radius = [(r,r),(r,r),(0,0),(0,0)]
                )

            self.table = GridLayout(
                pos = self.tableBackground.pos,
                size = self.tableBackground.size
            )
class StoresScreen(NormalScreen):
    def __init__(self, ribbonColor, **kw):
        super().__init__(ribbonColor,**kw)
    def on_enter(self):
        self.add_widget(self.StoreBuilder(.15,.05,self.ribbonColor))
    class StoreBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float, ribbonColor, staticBuffers=False, color=(1,1,1,0), sideBuffer=0.05, topBuffer=0.05, textColor=(0.3, 0.3, 0.3, 1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, staticBuffers, color, sideBuffer, topBuffer, textColor, **kwargs)
            self.layout.add_widget(
                Button(
                    background_normal = '',
                    background_color = ribbonColor,
                    pos_hint = {'center_x' : .8,'center_y' : .2},
                    size_hint = (.4,.4),
                    color = (0,0,0,1),
                    text = 'Store Calendar'
                )
            )
            self.add_widget(self.layout)
class CalendarScreen(NormalScreen):
    def __init__(self,ribbonColor, **kw):
        super().__init__(ribbonColor, **kw)
    def on_enter(self):
        self.screenBuilder = self.MonthBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self,calendarElementColor = self.ribbonColor,textColor = self.textColor,color = (.6,.6,.6,0))
        self.add_widget(self.screenBuilder)
        return super().on_enter()
    def changeScreenBuilder(self, type: str,day=None,week=None,month=None,year = localtime().tm_year):
        if type == 'Year':
            super().changeScreenBuilder(type)
            self.screenBuilder = self.YearBuilder(year,self.topRibbonHeight,self.bottomRibbonHeight,self,calendarElementColor = self.ribbonColor,textColor = self.textColor,color = (.6,.6,.6,0))
        elif type == 'Month':
            if month==None:
                raise ValueError('Month not specified.')
            super().changeScreenBuilder(type)
            self.screenBuilder = self.MonthBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self,monthNumber=month,yearNumber=year,calendarElementColor = self.ribbonColor,textColor = self.textColor,color = (.6,.6,.6,0))
        elif type == 'Week':
            super().changeScreenBuilder(type)
            if week==None:
                raise ValueError('Week number not specified.')
            self.screenBuilder = self.WeekBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self,weekNumber=week,calendarElementColor = self.ribbonColor,textColor = self.textColor,color = (.6,.6,.6,0))
        elif type == 'Day':
            if month==None:
                raise ValueError('Month not specified.')
            elif day==None:
                raise ValueError('Day not specified.')
            super().changeScreenBuilder(type)
            self.screenBuilder = self.DayBuilder(self.topRibbonHeight,self.bottomRibbonHeight,self,date=[day,month+1,year],calendarElementColor = self.ribbonColor,textColor = self.textColor,color = (.6,.6,.6,0))
        else:
            raise ValueError('Invalid screenBuilder type.')
        self.add_widget(self.screenBuilder)
    class YearBuilder(ScreenBuilder):
        def __init__(self, yearNumber, topRibbonHeight: float, bottomRibbonHeight: float,screen, staticBuffers=False, color=(0,0,0,0), sideBuffer=0.05, topBuffer=0.05,calendarElementColor = (.5,.5,.5,1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight,screen , staticBuffers, color, sideBuffer, topBuffer, **kwargs)
            self.gridSpacing = (10,10)
            self.calendarRelativeSize = .85
            calendarYearIndex = yearNumber - calendar.beginningYear

            self.floatLayout = FloatLayout(
                size = (self.rectangle.size[0],(1-self.calendarRelativeSize)*self.rectangle.size[1]),
                pos = (self.rectangle.pos[0], self.rectangle.pos[1] + self.calendarRelativeSize*self.rectangle.size[1])
            )

            self.gridLayout = GridLayout(
                size = (self.rectangle.size[0],self.calendarRelativeSize*self.rectangle.size[1]),
                pos = self.rectangle.pos,
                cols = 4,
                spacing = self.gridSpacing
            )
            monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December']

            self.floatLayout.add_widget(
                Label(
                    size_hint = (.5,2/3),
                    pos_hint = {'center_x' : .5,'center_y' : 2/3},
                    color = (.3,.3,.3,1),
                    font_size = self.gridLayout.size[1]*.1,
                    text = str(yearNumber)
                )
            )
            self.floatLayout.add_widget(
                RoundedButton(
                    background_normal = '',
                    button_color = calendarElementColor,
                    opacity = .5,
                    size_hint = (.1,.5),
                    pos_hint = {'center_x' : .35,'center_y' : 2/3},
                    color = (0,0,0,1),
                    font_size = self.gridLayout.size[1]*.05,
                    text = str(yearNumber-1)
                )
            )
            self.floatLayout.add_widget(
                RoundedButton(
                    background_normal = '',
                    button_color = calendarElementColor,
                    opacity = .5,
                    size_hint = (.1,.5),
                    pos_hint = {'center_x' : .65,'center_y' : 2/3},
                    color = (0,0,0,1),
                    font_size = self.gridLayout.size[1]*.05,
                    text = str(yearNumber+1)
                )
            )


            self.months = {} # do we need?
            for month in range(len(monthNames)):
                monthButton = Button(
                    background_normal = '',
                    background_color = (.7,.7,.7,0),
                    size_hint = (None,None),
                    pos_hint = {'center_x' : .5,'center_y' : .5}
                )
                monthButton.bind(on_release=lambda instance: self.changeToMonthBuilder(month))
                self.gridLayout.add_widget(monthButton)

                monthFloatLayout = FloatLayout(
                    size = (self.gridLayout.size[0]/4 - 2*self.gridSpacing[0],self.gridLayout.size[1]/3-2*self.gridSpacing[1]),
                    pos = (self.gridLayout.pos[0] + self.gridLayout.size[0]*(month % 4)/4 + self.gridSpacing[0],self.gridLayout.pos[1]+self.gridLayout.size[1]*(2-month//4)/3+self.gridSpacing[1])
                )
                monthGridLayout = GridLayout(
                    size_hint = (1,.8),
                    pos_hint = {'center_x' : .5,'center_y' : .4},
                    cols = 7,
                    spacing = (1,1)
                )
                monthFloatLayout.add_widget(monthGridLayout)

                tempRoundedRadius = .1*monthFloatLayout.size[1]
                monthLabel = CustomLabel(
                    background_color=(.7,.7,.7,1),
                    pos_hint = {'center_x' : .5,'center_y' : .9},
                    size_hint = (1,.2),
                    top_round=tempRoundedRadius,
                    color = (.3,.3,.3,1),
                    text = monthNames[month]
                )
                monthFloatLayout.add_widget(monthLabel)

                firstDay = (calendar.years[calendarYearIndex].yearlySchedule[month][0][2] + 1) % 7
                lastDay = (calendar.years[calendarYearIndex].yearlySchedule[month][-1][2] + 1) % 7
                numberOfDays = firstDay + len(calendar.years[calendarYearIndex].yearlySchedule[month])
                numberOfRows = (numberOfDays + firstDay + 6 - lastDay)/7

                for day in range(firstDay):
                    dayButtonColor = list(calendarElementColor)
                    dayButtonColor[0] += .2
                    dayButtonColor[1] += .2
                    dayButtonColor[2] += .2
                    monthGridLayout.add_widget(
                        CustomLabel(
                            background_color = dayButtonColor,
                            pos_hint = {'center_x' : .5, 'center_y' : .5},
                            size_hint = (.1,.1),
                            color = (0,0,0,1),
                            font_size = monthGridLayout.size[1]*.1,
                            text_size = (.9*monthGridLayout.size[0]/monthGridLayout.cols,.9*monthGridLayout.size[1]/numberOfRows - monthGridLayout.spacing[1]),
                            halign = 'center',
                            valign = 'middle',
                            text = str(len(calendar.years[calendarYearIndex].yearlySchedule[month]) - firstDay + 1 + day)
                        )
                    )

                for day in range(len(calendar.years[calendarYearIndex].yearlySchedule[month])):
                    dayButtonColor = list(calendarElementColor)
                    if (localtime().tm_mday == day+1) and (localtime().tm_mon == calendar.years[calendarYearIndex].yearlySchedule[month][localtime().tm_mday - 1][1]):
                        dayButtonColor[1] -= .1
                        dayButtonColor[2] -= .1
                    monthGridLayout.add_widget(
                        CustomLabel(
                            background_color = dayButtonColor,
                            pos_hint = {'center_x' : .5, 'center_y' : .5},
                            color = (0,0,0,1),
                            font_size = monthGridLayout.size[1]*.1,
                            text_size = (.9*monthGridLayout.size[0]/monthGridLayout.cols,.9*monthGridLayout.size[1]/numberOfRows - monthGridLayout.spacing[1]),
                            halign = 'center',
                            valign = 'middle',
                            text = str(day+1)
                        )
                    )

                for day in range(6 - lastDay):
                    dayButtonColor = list(calendarElementColor)
                    dayButtonColor[0] += .2
                    dayButtonColor[1] += .2
                    dayButtonColor[2] += .2
                    if (localtime().tm_mday == calendar.years[calendarYearIndex].yearlySchedule[month-1][-(day+1)][0]) and (localtime().tm_mon == calendar.years[calendarYearIndex].yearlySchedule[month-1][localtime().tm_mday-1][1]):
                        dayButtonColor[1] -= .1
                        dayButtonColor[2] -= .1
                    monthGridLayout.add_widget(
                        CustomLabel(
                            background_color = dayButtonColor,
                            pos_hint = {'center_x' : .5, 'center_y' : .5},
                            size_hint = (.1,.1),
                            color = (0,0,0,1),
                            font_size = monthGridLayout.size[1]*.1,
                            text_size = (.9*monthGridLayout.size[0]/monthGridLayout.cols,.9*monthGridLayout.size[1]/numberOfRows - monthGridLayout.spacing[1]),
                            halign = 'right',
                            valign = 'top',
                            text = str(day + 1)
                        )
                    )

                monthButton.add_widget(monthFloatLayout)
                self.months[month] = [monthFloatLayout,monthGridLayout]

            self.layout.add_widget(self.gridLayout)
            self.add_widget(self.floatLayout)
            self.add_widget(self.layout)
        def changeToMonthBuilder(self,month):
            self.screen.changeScreenBuilder('Month',month=month)
            del self
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            self.gridLayout.size = (self.rectangle.size[0],self.calendarRelativeSize*self.rectangle.size[1])
            self.gridLayout.pos = self.rectangle.pos
            self.floatLayout.size = (self.rectangle.size[0],(1-self.calendarRelativeSize)*self.rectangle.size[1])
            self.floatLayout.pos = (self.rectangle.pos[0], self.rectangle.pos[1] + self.calendarRelativeSize*self.rectangle.size[1])
    class MonthBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float,screen, staticBuffers=False,monthNumber:int = localtime().tm_mon-1,yearNumber = localtime().tm_year, color=(0,0,0,0), sideBuffer=0.05, topBuffer=0.05,calendarElementColor = (.5,.5,.5,1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen,staticBuffers, color, sideBuffer, topBuffer, **kwargs)
            monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December']
            self.yearNumber = yearNumber
            calendarYearIndex = yearNumber - calendar.beginningYear
            if monthNumber >= len(monthNames):
                self.yearNumber += 1
            elif monthNumber < 0:
                self.yearNumber -= 1
            self.monthNumber = monthNumber % 12
            monthNames=monthNames*2 # temporary
            # temporary - must rework
            self.lastMonth = calendar.years[calendarYearIndex].yearlySchedule[localtime().tm_mon-2]
            self.month = calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber]
            self.nextMonth = calendar.years[calendarYearIndex].yearlySchedule[localtime().tm_mon]
            # positioning
            self.layoutSizeHint = .96
            
            firstDay = (self.month[0][2] + 1) % 7
            lastDay = (self.month[-1][2] + 1) % 7

            self.gridLayout = GridLayout(
                size = (self.layoutSizeHint*self.rectangle.size[0],.8*self.rectangle.size[1]),
                pos = self.rectangle.pos,
                cols = 7,
                spacing = (5,5)
            )

            self.boxLayout = BoxLayout(
                orientation = 'horizontal',
                pos = (self.rectangle.pos[0], self.rectangle.pos[1] + self.rectangle.size[1]*.81),
                size = (self.layoutSizeHint*self.rectangle.size[0],self.rectangle.size[1]*.05)
            )

            self.weekButtonLayout = BoxLayout(
                orientation = 'vertical',
                pos = self.rectangle.pos,
                size = (.9*(1-self.layoutSizeHint)*self.rectangle.size[0],.8*self.rectangle.size[1]),
                spacing = 5
            )

            numberOfDays = firstDay + len(self.month)
            self.numberOfRows = int((numberOfDays + firstDay + 6 - lastDay)/7)
            weekdayList = ['S','M','T','W','T','F','S']
            dayButtonColor = list(calendarElementColor)

            self.weekButtonList = []
            for week in range(self.numberOfRows):
                self.weekButtonList.append(
                    Button(
                        background_normal='',
                        background_color=(.8,.8,.8)
                    )
                )
                self.weekButtonList[-1].bind(on_release=lambda instance: self.changeToWeekBuilder(week))
            for weekButton in self.weekButtonList:
                self.weekButtonLayout.add_widget(weekButton)

            # End of last month
            self.PMDayButtons = [None]*firstDay
            for day in range(firstDay):
                self.PMDayButtons[day] = LayeredButton(
                    background_normal = '',
                    background_color = calendarElementColor,
                    opacity = .5,
                    pos_hint = {'center_x' : .5, 'center_y' : .5},
                    size_hint = (.1,.1),
                    color = (0,0,0,1),
                    layout='Box',
                    layout_size=(1,.7),
                    font_size = self.gridLayout.size[1]*.04,
                    text_size = (.9*self.gridLayout.size[0]/self.gridLayout.cols - self.gridLayout.spacing[0],.9*self.gridLayout.size[1]/self.numberOfRows - self.gridLayout.spacing[1]),
                    halign = 'right',
                    valign = 'top',
                    text = str(len(calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber-1]) - firstDay + 1 + day)
                )
                dayButtonLabelColor = (1,1,1)
                self.PMDayButtons[day].boxLayout.add_widget(
                    CustomLabel(
                        background_color=dayButtonLabelColor,
                        color = self.textColor,
                        opacity = .5,
                        text_size = (self.gridLayout.size[0]/self.gridLayout.cols - 4*self.gridLayout.spacing[0],self.gridLayout.size[1]/self.gridLayout.cols - 3*self.gridLayout.spacing[1]),
                        font_size = self.gridLayout.size[1]*.03,
                        text = calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber-1][len(calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber-1])-firstDay+day][-1],
                        halign = 'center',
                        valign = 'top'
                    )
                )
                #self.PMDayButtons[day].add_widget(self.PMDayButtons[day].boxLayout)
                self.gridLayout.add_widget(self.PMDayButtons[day])

            # Current Month
            self.dayButtons = [None] * len(self.month)
            for day in range(len(self.month)):
                dayButtonColor = list(calendarElementColor)
                if (localtime().tm_mday == day+1) and (localtime().tm_mon == self.month[localtime().tm_mday - 1][1]):
                    dayButtonColor[1] -= .1
                    dayButtonColor[2] -= .1
                self.dayButtons[day] = LayeredButton(
                    background_normal = '',
                    background_color = dayButtonColor,
                    pos_hint = {'center_x' : .5, 'center_y' : .5},
                    color = self.textColor,
                    layout='Box',
                    layout_size=(1,.7),
                    font_size = self.gridLayout.size[1]*.04,
                    text_size = (self.gridLayout.size[0]/self.gridLayout.cols - self.gridLayout.spacing[0],((self.gridLayout.size[1]+self.gridLayout.spacing[1])/self.numberOfRows + self.gridLayout.spacing[1])),
                    halign = 'right',
                    valign = 'top',
                    text = str(day+1)
                )
                dayButtonLabelColor = (dayButtonColor[0]+.05,dayButtonColor[1]+.05,dayButtonColor[2]+.05,1)
                self.dayButtons[day].boxLayout.add_widget(
                    CustomLabel(
                        background_color=dayButtonLabelColor,
                        color = self.textColor,
                        text_size = (self.gridLayout.size[0]/self.gridLayout.cols - 4*self.gridLayout.spacing[0],self.gridLayout.size[1]/self.numberOfRows - 3*self.gridLayout.spacing[1]),
                        font_size = self.gridLayout.size[1]*.03,
                        text = calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber][day][-1],
                        halign = 'center',
                        valign = 'top'
                    )
                )
                self.dayButtons[day].bind(on_release=lambda instance: self.changeToDayBuilder(day+1,self.monthNumber))
                #self.dayButtons[day].add_widget(self.dayButtons[day].boxLayout)
                self.gridLayout.add_widget(self.dayButtons[day])

            # Beginning of Next Month
            self.AMDayButtons = [None]*(6-lastDay)
            for day in range(6 - lastDay):
                dayButtonColor = list(calendarElementColor)
                if (localtime().tm_mday == self.lastMonth[-(day+1)][0]) and (localtime().tm_mon == self.lastMonth[localtime().tm_mday-1][1]):
                    dayButtonColor[1] -= .1
                    dayButtonColor[2] -= .1
                self.AMDayButtons[day] = LayeredButton(
                    background_normal = '',
                    background_color = dayButtonColor,
                    opacity = .5,
                    pos_hint = {'center_x' : .5, 'center_y' : .5},
                    size_hint = (.1,.1),
                    color = (0,0,0,1),
                    layout='Box',
                    layout_size=(1,.7),
                    font_size = self.gridLayout.size[1]*.04,
                    text_size = (.9*self.gridLayout.size[0]/self.gridLayout.cols - self.gridLayout.spacing[0],.9*self.gridLayout.size[1]/self.numberOfRows - self.gridLayout.spacing[1]),
                    halign = 'right',
                    valign = 'top',
                    text = str(day + 1)
                )
                dayButtonLabelColor = (1,1,1)
                self.AMDayButtons[day].boxLayout.add_widget(
                    CustomLabel(
                        background_color=dayButtonLabelColor,
                        color = self.textColor,
                        opacity = .5,
                        text_size = (self.gridLayout.size[0]/self.gridLayout.cols - 4*self.gridLayout.spacing[0],self.gridLayout.size[1]/self.gridLayout.cols - 3*self.gridLayout.spacing[1]),
                        font_size = self.gridLayout.size[1]*.03,
                        text = calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber-11][day][-1],
                        halign = 'center',
                        valign = 'top'
                    )
                )
                #self.AMDayButtons[day].add_widget(self.AMDayButtons[day].boxLayout)
                self.gridLayout.add_widget(self.AMDayButtons[day])
            for day in range(7):
                self.boxLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (0,0,0,0),
                        font_size = self.gridLayout.size[1]*.05,
                        text = weekdayList[day],
                        color = self.textColor
                    )
                )
            self.currentMonthLabel = Label(
                    pos_hint = {'center_x' : .5, 'center_y' : .95},
                    color = self.textColor,
                    text = monthNames[self.monthNumber],
                    font_size = self.gridLayout.size[1]*.1
                )
            self.layout.add_widget(self.currentMonthLabel)

            monthButtonColor = list(calendarElementColor)
            monthButtonColor.append(.5)

            self.lastMonthButton = RoundedButton(
                background_normal = '',
                button_color = monthButtonColor,
                pos_hint = {'center_x' : .35,'center_y' : .95},
                size_hint = (.1,.08),
                text = monthNames[monthNumber-1],
                font_size = self.gridLayout.size[1]*.05,
                color = self.textColor
            )
            self.lastMonthButton.bind(on_press=lambda instance: self.changeMonth(self.monthNumber-1))
            self.layout.add_widget(self.lastMonthButton)

            self.nextMonthButton = RoundedButton(
                background_normal = '',
                button_color = monthButtonColor,
                pos_hint = {'center_x' : .65,'center_y' : .95},
                size_hint = (.1,.08),
                text = monthNames[monthNumber+1],
                font_size = self.gridLayout.size[1]*.05,
                color =  self.textColor
            )
            self.nextMonthButton.bind(on_press=lambda instance: self.changeMonth(self.monthNumber+1))
            self.layout.add_widget(self.nextMonthButton)

            self.yearlyButton = RoundedButton(
                background_normal = '',
                button_color = monthButtonColor,
                pos_hint = {'center_x' : .9,'center_y' : .95},
                size_hint = (.1,.1),
                text = str(self.yearNumber),
                font_size = self.gridLayout.size[1]*.05,
                color =  self.textColor
            )
            self.yearlyButton.bind(on_press=lambda instance: self.changeToYearBuilder())
            self.layout.add_widget(self.yearlyButton)

            self.add_widget(self.gridLayout)
            self.add_widget(self.boxLayout)
            self.add_widget(self.weekButtonLayout)
            self.add_widget(self.layout)
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            self.gridLayout.size = (self.layoutSizeHint*self.rectangle.size[0],.8*self.rectangle.size[1])
            self.gridLayout.pos = (self.rectangle.pos[0] + (1-self.layoutSizeHint)*self.rectangle.size[0],self.rectangle.pos[1])
            self.boxLayout.pos = (self.rectangle.pos[0] + (1-self.layoutSizeHint)*self.rectangle.size[0], self.rectangle.pos[1] + self.rectangle.size[1]*.81)
            self.boxLayout.size = (self.layoutSizeHint*self.rectangle.size[0],self.rectangle.size[1]*.05)
            self.weekButtonLayout.pos = self.rectangle.pos
            self.weekButtonLayout.size = (.9*(1-self.layoutSizeHint)*self.rectangle.size[0],.8*self.rectangle.size[1])
            for widget in self.gridLayout.children:
                widget.text_size = (self.gridLayout.size[0]/self.gridLayout.cols - 4*self.gridLayout.spacing[0],((self.gridLayout.size[1]+self.gridLayout.spacing[1])/self.numberOfRows - 1.5*self.gridLayout.spacing[1])) #(.9*self.gridLayout.size[0]/self.gridLayout.cols - self.gridLayout.spacing[0],.9*self.gridLayout.size[1]/self.numberOfRows - self.gridLayout.spacing[1])
                widget.font_size = self.gridLayout.size[1]*.04
                for label in widget.boxLayout.children:
                    label.text_size = (self.gridLayout.size[0]/self.gridLayout.cols - 4*self.gridLayout.spacing[0],self.gridLayout.size[1]/self.gridLayout.cols - 3*self.gridLayout.spacing[1])
                    label.font_size = self.gridLayout.size[1]*.03
            for widget in self.boxLayout.children:
                widget.font_size = self.gridLayout.size[1]*.05
            if self.rectangle.size[1]*1.5 > self.rectangle.size[0]:
                sizeRatio = self.rectangle.size[0]/(self.rectangle.size[1]*1.5)
                for widget in self.layout.children:
                    widget.font_size = self.gridLayout.size[1]*.05*sizeRatio
                self.currentMonthLabel.font_size = self.gridLayout.size[1]*.1*sizeRatio
            else:
                for widget in self.layout.children:
                    widget.font_size = self.gridLayout.size[1]*.05
                self.currentMonthLabel.font_size = self.gridLayout.size[1]*.1
        def changeToDayBuilder(self,dayNum,month): # For some Reason only goes to a random day
            self.screen.changeScreenBuilder('Day',day=dayNum,month=month)
            del self
        def changeToWeekBuilder(self,weekNumber):
            self.screen.changeScreenBuilder('Week',week=weekNumber)
            del self
        def changeToYearBuilder(self):
            self.screen.changeScreenBuilder('Year')
            del self
        def getScreen(self,screen):
            self.parent.manager.current(screen)
        def changeMonth(self,month:int):
            self.screen.changeScreenBuilder('Month',month=month,year=self.yearNumber)
            del self
    class WeekBuilder(ScreenBuilder):
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float,screen, monthNumber = localtime().tm_mon, yearNumber = localtime().tm_year,weekNumber = 0,staticBuffers=False, color=(0.5, 0.5, 0.5, 1), sideBuffer=0.05, topBuffer=0.05, textColor=(0.3, 0.3, 0.3, 1), calendarElementColor = (.5,.5,.5,1), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight,screen, staticBuffers, color, sideBuffer, topBuffer, textColor, **kwargs)
            self.calendarRelativeSize = .92
            calendarYearIndex = calendar.beginningYear
            weekdayList = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
            monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December']
            self.weekNumber = weekNumber
            self.monthNumber = monthNumber
            self.yearNumber = yearNumber
            
            checkMonth = calendar.years[calendarYearIndex].yearlySchedule[self.monthNumber-1]
            firstDay = checkMonth[self.weekNumber*7]

            tempDayNumber = firstDay[0]-1
            tempMonthNumber = self.monthNumber-1
            tempYearNumber = self.yearNumber - calendar.beginningYear
            while firstDay[2] != 6:
                if firstDay[0] == 1:
                    tempMonthNumber -= 1
                    if tempMonthNumber == 0:
                        tempYearNumber -= 1
                        tempMonthNumber = 11
                    checkMonth = calendar.years[calendarYearIndex].yearlySchedule[tempMonthNumber]
                    tempDayNumber = len(checkMonth)
                tempDayNumber -= 1
                firstDay = calendar.years[calendarYearIndex].yearlySchedule[tempMonthNumber][tempDayNumber]
            firstDayNumber = calendar.countDay([firstDay[0],firstDay[1],calendar.beginningYear+tempYearNumber])

            self.boxLayout = BoxLayout(
                pos = self.rectangle.pos,
                size_hint = (1,self.calendarRelativeSize),
                spacing = 10
            )
            self.dayWidgets = []

            for day in range(7):
                date = calendar.nextDay(firstDayNumber + day)
                dayWidget = LayeredButton(
                    background_normal = '',
                    background_color = (.8,.8,.8,1),
                    layout='Float'
                )
                dayWidget.floatLayout.add_widget(
                    CustomLabel(
                        pos_hint = {'center_x' : .5,'center_y' : .46},
                        size_hint = (.9,.88),
                        background_color=(.9,.9,.9,1),
                        color = (0,0,0,1),
                        text = 'Details'
                    )
                )
                dayWidget.floatLayout.add_widget( # Day of week
                    CustomLabel(
                        pos_hint = {'center_x' : .375,'center_y' : .94},
                        size_hint = (.65,.08),
                        background_color=(.6,.6,.6,1),
                        color = (0,0,0,1),
                        font_size = .025*self.rectangle.size[1],
                        text_size = (.85*.65*self.rectangle.size[0]/7,None),
                        halign = 'left',
                        text = weekdayList[day]
                    )
                )
                dayWidget.floatLayout.add_widget(
                    CustomLabel(
                        background_color=(.65,.8,.85),
                        pos_hint = {'center_x' : .825,'center_y' : .94},
                        size_hint = (.25,.08),
                        color = (.2,.2,.2),
                        font_size = .025*self.rectangle.size[1],
                        text = str(date[0])
                    )
                )
                self.dayWidgets.append(dayWidget)

            # not sure why but loop doesn't work
            self.dayWidgets[0].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber)[0],month=calendar.nextDay(firstDayNumber)[1]))
            self.boxLayout.add_widget(self.dayWidgets[0])

            self.dayWidgets[1].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+1)[0],month=calendar.nextDay(firstDayNumber+1)[1]))
            self.boxLayout.add_widget(self.dayWidgets[1])

            self.dayWidgets[2].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+2)[0],month=calendar.nextDay(firstDayNumber+2)[1]))
            self.boxLayout.add_widget(self.dayWidgets[2])

            self.dayWidgets[3].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+3)[0],month=calendar.nextDay(firstDayNumber+3)[1]))
            self.boxLayout.add_widget(self.dayWidgets[3])

            self.dayWidgets[4].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+4)[0],month=calendar.nextDay(firstDayNumber+4)[1]))
            self.boxLayout.add_widget(self.dayWidgets[4])

            self.dayWidgets[5].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+5)[0],month=calendar.nextDay(firstDayNumber+5)[1]))
            self.boxLayout.add_widget(self.dayWidgets[5])

            self.dayWidgets[6].bind(on_press=lambda instance: self.changeToDayBuilder(day=calendar.nextDay(firstDayNumber+6)[0],month=calendar.nextDay(firstDayNumber+6)[1]))
            self.boxLayout.add_widget(self.dayWidgets[6])

            self.monthLabel = Button(
                background_normal = '',
                background_color = (0,0,0,0),
                pos_hint = {'x' : 0,'y' : .95},
                size_hint = (.1,.1),
                #text_size = (.09*self.rectangle.size[0],.09*self.rectangle.size[1]),
                font_size = .05*self.rectangle.size[1],
                color = (0,0,0,1),
                halign = 'left',
                valign = 'middle',
                text = monthNames[firstDay[1]-1]
            )
            self.monthLabel.bind(texture_size=self.update_text)
            self.monthLabel.bind(on_press=lambda instance: self.changeToMonthBuilder(firstDay[1]-1))
            self.layout.add_widget(self.monthLabel)

            if firstDay[1] != calendar.nextDay(firstDayNumber+6)[1]:
                self.slashText = Label(
                    color = (0,0,0,1),
                    pos_hint = {'x' : self.monthLabel.size[0]/self.rectangle.size[0],'y' : .95},
                    font_size = self.monthLabel.font_size,
                    text='/'
                )
                self.slashText.bind(texture_size=self.update_text)
                self.layout.add_widget(self.slashText)

                self.monthLabel2 = Button(
                    background_normal = '',
                    background_color = (0,0,0,0),
                    pos_hint = {'x' : (self.monthLabel.size[0]+self.slashText.size[0])/self.rectangle.size[0],'y' : .95},
                    size_hint = (.1,.1),
                    #text_size = (.09*self.rectangle.size[0],.09*self.rectangle.size[1]),
                    font_size = .05*self.rectangle.size[1],
                    color = (0,0,0,1),
                    halign = 'left',
                    valign = 'middle',
                    text = monthNames[firstDay[1]]
                )
                self.monthLabel2.bind(texture_size=self.update_text)
                self.monthLabel2.bind(on_press=lambda instance: self.changeToMonthBuilder(firstDay[1]))
                self.layout.add_widget(self.monthLabel2)
            
            self.spaceLabel = Label(
                color = (0,0,0,1),
                pos_hint = {'x' : self.monthLabel.size[0]/self.rectangle.size[0],'y' : .95},
                font_size = self.monthLabel.font_size,
                text=' '
            )
            self.spaceLabel.bind(texture_size=self.update_text)
            self.layout.add_widget(self.spaceLabel)

            self.yearButton = Button(
                background_normal = '',
                background_color = (0,0,0,0),
                pos_hint = {'x' : 0,'y' : .95},
                size_hint = (.1,.1),
                font_size = .05*self.rectangle.size[1],
                color = (0,0,0,1),
                halign = 'left',
                valign = 'middle',
                text = str(calendar.beginningYear+tempYearNumber)
            )
            self.yearButton.bind(texture_size=self.update_text)
            self.yearButton.bind(on_release=lambda instance: self.changeToYearBuilder(calendar.beginningYear+tempYearNumber))
            self.layout.add_widget(self.yearButton)

            self.layout.add_widget(self.boxLayout)
            self.add_widget(self.layout)
        def update_text(self,instance,value):
            instance.size_hint = (None, None)
            instance.size = instance.texture_size
            try:
                self.slashText.pos_hint['x'] = self.monthLabel.texture_size[0]/self.rectangle.size[0]
                self.monthLabel2.pos_hint['x'] = (self.monthLabel.texture_size[0]+self.slashText.texture_size[0])/self.rectangle.size[0]
            except:pass
            try:
                self.spaceLabel.pos_hint['x'] = (self.monthLabel.texture_size[0]+self.slashText.texture_size[0]+self.monthLabel2.texture_size[0])/self.rectangle.size[0]
                self.yearButton.pos_hint['x'] = (self.monthLabel.texture_size[0]+self.slashText.texture_size[0]+self.monthLabel2.texture_size[0]+self.spaceLabel.texture_size[0])/self.rectangle.size[0]
            except:
                self.spaceLabel.pos_hint['x'] = self.monthLabel.texture_size[0]/self.rectangle.size[0]
                self.yearButton.pos_hint['x'] = (self.monthLabel.texture_size[0]+self.spaceLabel.texture_size[0])/self.rectangle.size[0]
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            for dayWidget in self.boxLayout.children:
                for widget in dayWidget.children:
                    widget.pos_hint = {'center_x' : .5, 'center_y' : .9}
                    widget.size_hint = (1,.2)
            #self.slashText.pos_hint = {'x' : self.monthLabel.texture_size[0]/self.rectangle.size[0],'y' : .95}
            #self.monthLabel2.pos_hint = {'x' : (self.monthLabel.texture_size[0]+self.slashText.texture_size[0])/self.rectangle.size[0],'y' : .95}
        def changeToDayBuilder(self,day,month): # For some Reason only goes to a random day
            self.screen.changeScreenBuilder('Day',day=day,month=month,year=self.yearNumber) #Could have bug with end/beginning of year
            del self
        def changeToMonthBuilder(self,month): # For some Reason only goes to a random day
            self.screen.changeScreenBuilder('Month',month = month)
            del self
        def changeToYearBuilder(self,year):
            self.screen.changeScreenBuilder('Year')
            del self
    class DayBuilder(ScreenBuilder): # Does not scale properly yet
        def __init__(self, topRibbonHeight: float, bottomRibbonHeight: float,screen, staticBuffers=False,date:list[int,int,int] = [20,7,2024], color=(0.8, 0.8, 0.8, 1), sideBuffer=0.05, topBuffer=0.05, textColor=(0.3, 0.3, 0.3, 1),calendarElementColor = (0,0,0,0), **kwargs):
            super().__init__(topRibbonHeight, bottomRibbonHeight, screen,staticBuffers, color, sideBuffer, topBuffer, textColor, **kwargs)
            self.yearNumber = date[2]
            self.monthNumber = date[1]
            self.dayNumber = date[0]
            monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December']

            self.scheduleHeader = RoundedButton(
                button_color=(.65,.8,.85,1),
                pos_hint = {'center_x' : .225,'center_y' : .85},
                size_hint = (.45,.1),
                radii = (.25,.25,0,0)
            )
            self.layout.add_widget(self.scheduleHeader)

            self.dailySchedule = LayeredButton(
                background_normal = '',
                background_color = (.6,.6,.6,1),
                pos_hint = {'center_x' : .225,'center_y' : .4},
                size_hint = (.45,.8),
                layout='Box',
                layout_pos=(.5,.5),
                layout_size=(.96,.97)
            )
            self.dailySchedule.boxLayout.orientation = 'vertical'
            self.dailySchedule.boxLayout.spacing = 5
            for time in range(12):
                if time == 0:
                    time = 12
                self.dailySchedule.boxLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.8,.8,.8,1),
                        text_size = (600,50), # temporary
                        color = (0,0,0),
                        halign = 'left',
                        valign = 'center',
                        text = str(time) + ':00 PM'
                    )
                )
            self.layout.add_widget(self.dailySchedule)

            self.dailyEventsHeader = RoundedButton(
                button_color=(.8,.8,.8),
                pos_hint = {'center_x' : .75,'center_y' : .95},
                size_hint = (.5,.1),
                radii = (.25,.25,0,0),
                color = (0,0,0),
                font_size = .05*self.rectangle.size[1],
                text_size = (.5*self.rectangle.size[0]-20,.1*self.rectangle.size[1]-20),
                halign = 'left',
                valign = 'middle',
                text = 'Daily Events'
            )
            self.layout.add_widget(self.dailyEventsHeader)

            # Ex. fig 1
            self.figure = fig.Pie(
                color = (.9,.9,.9,1),
                text_color = (.2,.2,.2,1),
                pos = (self.rectangle.pos[0]+.5*self.rectangle.size[0],self.rectangle.pos[1]),
                size = (.235*self.rectangle.size[0],.45*self.rectangle.size[1])
            )
            self.layout.add_widget(self.figure)
            self.figure.showFigure()

            # Ex. fig 2
            self.figure2 = fig.ScatterPlot(
                color = (.9,.9,.9,1),
                text_color = (.2,.2,.2,1),
                pos = (self.rectangle.pos[0]+.765*self.rectangle.size[0],self.rectangle.pos[1]),
                size = (.235*self.rectangle.size[0],.45*self.rectangle.size[1])
            )
            self.layout.add_widget(self.figure2)
            self.figure2.showFigure()

            self.dailyEvents = LayeredButton(
                background_normal = '',
                background_color = (.6,.6,.6,1),
                pos_hint = {'center_x' : .75,'center_y' : .7},
                size_hint = (.5,.4),
                color = (0,0,0,1),
                layout='Box',
                layout_pos=(.5,.5),
                layout_size=(.975,.95)
            )
            self.dailyEvents.boxLayout.orientation = 'vertical'
            self.dailyEvents.boxLayout.spacing = 5
            for event in range(4):
                self.dailyEvents.boxLayout.add_widget(
                    Button(
                        background_normal = '',
                        background_color = (.8,.8,.8,1),
                        color = (.2,.2,.2),
                        text = str(event)
                    )
                )
            self.layout.add_widget(self.dailyEvents)

            self.monthButton = Button(
                background_normal = '',
                background_color = (.65,.8,.85,0),
                pos_hint = {'center_x' : .05,'center_y' : .95},
                size_hint = (.08,.08),
                color = (0,0,0,1),
                font_size = .06*self.rectangle.size[1],
                halign = 'left',
                text = monthNames[self.monthNumber-1] + ' '
            )
            self.monthButton.bind(on_press=lambda instance: self.changeToMonthBuilder(self.monthNumber-1))
            self.monthButton.bind(texture_size=self.update_text)
            self.layout.add_widget(self.monthButton)

            self.addEventButton = RoundedButton(
                button_color = (.8,.8,.8,1),
                pos_hint = {'center_x' : .35,'center_y' : .85},
                size_hint = (.18,.075),
                color = (0,0,0,1),
                font_size = .05*self.rectangle.size[1],
                halign = 'center',
                text = 'Add Event'
            )
            self.layout.add_widget(self.addEventButton)

            self.dayLabel = Label(
                pos_hint = {'center_x' : .115,'center_y' : .95},
                size_hint = (.1,.08),
                color = (0,0,0,1),
                font_size = .06*self.rectangle.size[1],
                halign = 'left',
                text = str(self.dayNumber) + ', '
            )
            self.layout.add_widget(self.dayLabel)
            self.dayLabel.bind(texture_size=self.update_text)

            self.yearButton = Button(
                background_normal = '',
                background_color = (.65,.8,.85,0),
                pos_hint = {'center_x' : .185,'center_y' : .95},
                size_hint = (.08,.08),
                font_size = .06*self.rectangle.size[1],
                color = (0,0,0,1),
                halign = 'left',
                text = str(self.yearNumber)
            )
            self.yearButton.bind(on_press=lambda instance: self.changeToYearBuilder(self.yearNumber))
            self.yearButton.bind(texture_size=self.update_text)
            self.layout.add_widget(self.yearButton)

            # Add elements to screen
            self.add_widget(self.layout)
        def update_text(self,instance,value):
            instance.size_hint = (None, None)
            instance.size = instance.texture_size
        def update_rect(self, instance, value):
            super().update_rect(instance, value)
            #self.figure.update_rect(self.figure,0)
        def ne(self,instance,value):
            try:
                self.dayLabel.pos_hint['x'] = self.monthButton.texture_size[0]/self.rectangle.size[0]
                self.yearButton.pos_hint['x'] = (self.monthButton.texture_size[0]+self.dayLabel.texture_size[0])/self.rectangle.size[0]
            except:pass
        def changeToMonthBuilder(self,month):
            self.screen.changeScreenBuilder('Month',month=month)
            del self
        def changeToYearBuilder(self,year):
            self.screen.changeScreenBuilder('Year')
            del self
class SmallBusinessApp(MDApp):
    def build(self):
        sm = ScreenManager()
        screen2 = AnalyticsScreen((0.65, 0.8,0.85),name='as1')
        sm.add_widget(screen2)
        dashboard = Dashboard((0.65, 0.8,0.85),orgBool=True,name='cal')
        sm.add_widget(dashboard)
        es = EmployeeScreen((0.65, 0.8,0.85),name = 'es1')
        sm.add_widget(es)
        myScreen = CalendarScreen((0.65, 0.8,0.85), name='dashboard')
        sm.add_widget(myScreen)
        #storesScreen = StoresScreen(name='StoresScreen')
        #sm.add_widget(storesScreen)
        
        return sm
SmallBusinessApp().run()