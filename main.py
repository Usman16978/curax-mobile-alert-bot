from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.add_widget(Label(
            text="CuraX Alert Bot",
            font_size="24sp"
        ))

        self.add_widget(Label(
            text="APK Build Successful",
            font_size="18sp"
        ))

        btn = Button(text="Exit App", size_hint=(1, 0.3))
        btn.bind(on_press=self.exit_app)
        self.add_widget(btn)

    def exit_app(self, instance):
        App.get_running_app().stop()


class CuraXAlertBot(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    CuraXAlertBot().run()
