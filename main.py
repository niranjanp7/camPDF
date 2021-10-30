from camPDF.edit import MyImage
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRectangleFlatIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from time import strftime
from shutil import move
from PIL import Image
import cv2
import os

filepathx = ""
open_box = ""
pdfpath = ""

class WindowManager(ScreenManager):
    filepath=""

    def setimg(self, path=None):
        global filepathx
        self.filepath = filepathx
        if path == None:
            path = "D:\\project\\camPDF\\History\\"+self.filepath
        if path[-4:] in ["jpeg", ".png", ".jpg"]:
            self.filepath = path
            self.ids.first_view_img.ids.image_view.source=path
            self.ids.first_view_img.ids.image_viwer.title=path

        else:
            self.current="main"
            self.transition.direction="right"

    def extractimg(self):
        global filepathx,pdfpath
        duration = strftime("%Y%m%d_%H%M%S")
        img = MyImage(self.filepath)
        extracted = img.extract_image()
        if filepathx[-4:]=='.png':os.remove(filepathx)
        filepathx = os.getcwd()+"\\camPDF_{}.jpg".format(duration)
        cv2.imwrite("camPDF_{}.jpg".format(duration), extracted)
        self.ids.second_view_img.ids.extracted_img.source = "camPDF_{}.jpg".format(duration)
        Image.open(r"camPDF_{}.jpg".format(duration)).convert('RGB').save(r"camPDF_{}.pdf".format(duration))
        pdfpath = "camPDF_{}.pdf".format(duration)
        self.current = "second_view"
    


class MainWindow(Screen):
    pass


class HistoryWindow(Screen):
    pass


class FileWindow(Screen):
    pass


class FirstView(Screen):
    pass


class Content(BoxLayout):
    pass


class SecondView(Screen):
    added = True
    def saving_option(self):
        self.ids.optionbox.pos_hint={'right': 1, 'top': 1}
        dirs = os.listdir()
        if 'History' in dirs:
            os.chdir('History')
        dirs = os.listdir()
        global open_box
        open_box = self.ids.optionbox
        if self.added:
            self.added = False
            for i in dirs:
                if '.' not in i:
                    btns = MDRectangleFlatIconButton()
                    btns.text = i
                    btns.icon = "folder"
                    btns.theme_text_color = "Custom"
                    btns.text_color = 0,0,1,1
                    btns.bind(on_press=partial(self.close, btn=btns))
                    self.ids.optionbox.add_widget(btns)
    
    def close(self, transfer = True, btn=None):
        global filepathx
        self.ids.optionbox.pos_hint={'right': 0}
        if transfer:
            cwd = os.getcwd()
            move(pdfpath, cwd+'\\'+btn.text)

class CameraWindow(Screen):
    def shutter(self):
        global filepathx
        camera = self.ids['camera_view']
        duration = strftime("%Y%m%d_%H%M%S")
        filepathx = "camPDF_{}.png".format(duration)
        camera.export_to_png("camPDF_{}.png".format(duration))


class MainApp(MDApp):
    def build(self):
        return #Builder.load_file("main.kv")

    def back_to_menu(self):
        self.root.current = "main"
        self.root.transition.direction = "right"

    def open_history(self):
        self.root.current = "history"
        self.root.transition.direction = "left"
    
    def privious(self):
        self.root.current = "main"
        self.root.transition.direction = "right"
    
    dialog = None

    def add_dir(self):
        if not self.dialog:
            self.dialog = MDDialog(title="Add New Category", type = "custom", content_cls=Content(),
                buttons=[
                    MDFlatButton(
                        text="CANCEL", text_color=self.theme_cls.primary_color, on_release=self.dialog_close
                    ),
                    MDFlatButton(
                        text="OK", text_color=self.theme_cls.primary_color, on_release=self.create_dir
                    )
                ])
        if os.getcwd()[-7:] != "History":
            os.chdir('History')
        self.dialog.open()
    
    def dialog_close(self, matter):
        self.dialog.dismiss()

    def create_dir(self, accpt):
        dir_name = accpt.parent.parent.parent.parent.content_cls.ids.dir_name.text
        try:
            os.mkdir(dir_name)
            global open_box
            btns = MDRectangleFlatIconButton()
            btns.text = dir_name
            btns.icon = "folder"
            btns.theme_text_color = "Custom"
            btns.text_color = 0,0,1,1
            btns.bind(on_press=partial(SecondView().close, btn=btns))
            open_box.add_widget(btns)
            self.dialog.dismiss()
        except:pass

if __name__ == "__main__":
    if 'History' not in os.listdir():
        os.makedirs('History')
    os.chdir('History')
    MainApp().run()
