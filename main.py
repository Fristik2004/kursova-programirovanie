import sys
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableView, \
    QMessageBox, QHeaderView, QDialog, QDialogButtonBox

from PyQt5.QtCore import Qt, QAbstractTableModel


class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Додати контакт")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ПІБ")
        layout.addWidget(self.name_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Адреса")
        layout.addWidget(self.address_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Електронна пошта")
        layout.addWidget(self.email_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")
        layout.addWidget(self.phone_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_contact_info(self):
        name = self.name_input.text()
        address = self.address_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        return name, address, email, phone


class ContactModel(QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        super(ContactModel, self).__init__(parent)
        self._data = data
        self._headers = headers

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._headers)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]


class PhoneBookApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Телефонний довідник")
        self.setGeometry(100, 100, 600, 400)

        self.contacts = []
        self.load_contacts_from_csv()  # Завантаження контактів з CSV

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук за ПІБ або номером телефону")
        self.search_input.textChanged.connect(self.search_contacts)
        layout.addWidget(self.search_input)

        self.contacts_table = QTableView()
        self.model = ContactModel(self.contacts, ["ПІБ", "Адреса", "Електронна пошта", "Телефони"])
        self.contacts_table.setModel(self.model)
        self.contacts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Розтягнути стовпці
        layout.addWidget(self.contacts_table)

        buttons_layout = QHBoxLayout()

        add_contact_button = QPushButton("Додати контакт")
        add_contact_button.setFixedHeight(40)
        add_contact_button.clicked.connect(self.add_contact)
        buttons_layout.addWidget(add_contact_button)

        delete_contact_button = QPushButton("Видалити контакт")
        delete_contact_button.setFixedHeight(40)
        delete_contact_button.clicked.connect(self.delete_selected_contact)
        buttons_layout.addWidget(delete_contact_button)

        edit_contact_button = QPushButton("Редагувати контакт")
        edit_contact_button.setFixedHeight(40)
        edit_contact_button.clicked.connect(self.edit_selected_contact)
        buttons_layout.addWidget(edit_contact_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_contacts_from_csv(self):
        try:
            with open("phonebook.csv", newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.contacts.append(row)
        except FileNotFoundError:
            # Якщо файл не знайдено, створити порожній список контактів
            self.contacts = []

    def save_contacts_to_csv(self):
        with open("phonebook.csv", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(self.contacts)

    def search_contacts(self):
        search_term = self.search_input.text().lower()
        if not search_term:
            self.model = ContactModel(self.contacts, ["ПІБ", "Адреса", "Електронна пошта", "Телефони"])
        else:
            filtered_contacts = [contact for contact in self.contacts if
                                 any(search_term in field.lower() for field in contact)]
            self.model = ContactModel(filtered_contacts, ["ПІБ", "Адреса", "Електронна пошта", "Телефони"])
        self.contacts_table.setModel(self.model)

    def add_contact(self):
        dialog = AddContactDialog(self)
        if dialog.exec_():
            contact_info = dialog.get_contact_info()
            self.contacts.append(contact_info)
            self.save_contacts_to_csv()
            self.search_contacts()  # Оновити відображення контактів

    def delete_contact(self, index):
        row = index.row()
        del self.contacts[row]
        self.save_contacts_to_csv()
        self.search_contacts()  # Оновити відображення контактів

    def edit_contact(self, index):
        row = index.row()
        old_contact_info = self.contacts[row]

        dialog = AddContactDialog(self)
        dialog.name_input.setText(old_contact_info[0])
        dialog.address_input.setText(old_contact_info[1])
        dialog.email_input.setText(old_contact_info[2])
        dialog.phone_input.setText(old_contact_info[3])

        if dialog.exec_():
            new_contact_info = dialog.get_contact_info()
            self.contacts[row] = new_contact_info
            self.save_contacts_to_csv()
            self.search_contacts()  # Оновити відображення контактів

    def delete_selected_contact(self):
        selected_indexes = self.contacts_table.selectionModel().selectedIndexes()
        if selected_indexes:
            reply = QMessageBox.question(self, 'Видалити контакт',
                                         "Ви впевнені, що хочете видалити цей контакт?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                for index in selected_indexes:
                    self.delete_contact(index)

    def edit_selected_contact(self):
        selected_indexes = self.contacts_table.selectionModel().selectedIndexes()
        if len(selected_indexes) == 1:
            self.edit_contact(selected_indexes[0])
        else:
            QMessageBox.warning(self, 'Помилка', 'Будь ласка, виберіть лише один контакт для редагування.')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    phonebook = PhoneBookApp()
    phonebook.show()
    sys.exit(app.exec_())
