from ._anvil_designer import MainTemplate
from anvil import *
import anvil.server
import anvil.users


class Main(MainTemplate):
    def __init__(self, **properties):
        self.init_components(**properties)
        self.role = None
        self.records_loaded = False
        self.records_panel.items = []
        self.show_logged_out("Please log in to continue.")

    # ------------------------------------------------------------------
    # Login / logout
    # ------------------------------------------------------------------
    def form_show(self, **event_args):
        if anvil.users.get_user() is None:
            self.do_login()
        else:
            self.show_logged_in()

    def login_button_click(self, **event_args):
        self.do_login()

    def do_login(self):
        try:
            user = anvil.users.login_with_form(allow_cancel=True)
            if user is None:
                self.show_logged_out("Login is required to use this application.")
            else:
                self.show_logged_in()
        except Exception as e:
            self.show_logged_out(str(e))

    def show_logged_in(self):
        try:
            # The server decides the role; the client only displays it.
            anvil.server.call("ensure_default_role")
            self.role = anvil.server.call("get_my_role")
            user = anvil.users.get_user()
            self.user_label.text = "Logged in as {} ({})".format(user["email"], self.role)
        except Exception:
            self.user_label.text = "Logged in"
        self.app_panel.visible = True
        self.login_button.visible = False
        self.logout_button.visible = True
        self.status_label.text = "Welcome! You may now register students and view records."

    def show_logged_out(self, message):
        self.role = None
        self.records_loaded = False
        self.records_panel.items = []
        self.app_panel.visible = False
        self.login_button.visible = True
        self.logout_button.visible = False
        self.user_label.text = "Not logged in"
        self.status_label.text = message

    def logout_button_click(self, **event_args):
        anvil.users.logout()
        self.student_id_box.text = ""
        self.name_box.text = ""
        self.delete_id_box.text = ""
        self.course_dropdown.selected_value = None
        self.year_dropdown.selected_value = None
        self.show_logged_out("You have been logged out. Please log in to continue.")

    # ------------------------------------------------------------------
    # Register
    # ------------------------------------------------------------------
    def register_button_click(self, **event_args):
        try:
            result = anvil.server.call(
                "register_student",
                self.student_id_box.text,
                self.name_box.text,
                self.course_dropdown.selected_value,
                self.year_dropdown.selected_value
            )
            self.status_label.text = result
            self.student_id_box.text = ""
            self.name_box.text = ""
            self.course_dropdown.selected_value = None
            self.year_dropdown.selected_value = None
            if self.records_loaded:
                self.load_records(show_message=False)
        except Exception as e:
            self.status_label.text = str(e)

    # ------------------------------------------------------------------
    # View
    # ------------------------------------------------------------------
    def view_button_click(self, **event_args):
        self.load_records(show_message=True)

    def load_records(self, show_message=True):
        try:
            user = anvil.users.get_user()
            if user is None:
                self.status_label.text = "Please log in first."
                return

            # Display choice only. The server independently enforces access.
            role = anvil.server.call("get_my_role")
            if role == "Admin":
                records = anvil.server.call("get_all_registrations")
            else:
                records = anvil.server.call("get_my_registrations")

            self.records_panel.items = records
            self.records_loaded = True
            if show_message:
                self.status_label.text = "Loaded {} registration(s).".format(len(records))
        except Exception as e:
            self.status_label.text = str(e)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_button_click(self, **event_args):
        try:
            result = anvil.server.call(
                "delete_registration",
                self.delete_id_box.text
            )
            self.status_label.text = result
            self.delete_id_box.text = ""
            if self.records_loaded:
                self.load_records(show_message=False)
        except Exception as e:
            self.status_label.text = str(e)
