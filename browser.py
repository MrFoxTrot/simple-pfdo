from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from enum import Enum


class ContractTypes(Enum):
    Free = 1
    Paid = 2


months_names = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
                'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']


class Browser:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.program = "Неизвестно"
        self.module = "Неизвестно"
        self.contract_type = ContractTypes.Free
        self.contract_date = datetime.now()

    def auth(self, login: str, password: str):
        self.browser.get("https://yar.pfdo.ru/app/start-page/signin")
        sleep(0.25)
        login_element = self.browser.find_element_by_name("login")
        pass_element = self.browser.find_element_by_name("password")
        login_element.send_keys(login)
        pass_element.send_keys(password)
        sleep(0.2)
        pass_element.send_keys(Keys.ENTER)
        sleep(0.5)
        self.browser.maximize_window()

    def add_contract_setup(self, program="Неизвестно", module="Неизвестно", contract_type=ContractTypes.Free,
                           contract_date=datetime.now()):
        self.program = program
        self.module = module
        self.contract_type = contract_type
        self.contract_date = contract_date

    def add_contract(self, pfdo_number: str, surname: str, firstname: str, middlename: str, group: str):
        """Добавить договор в систему"""

        # Страница 1 (Проверка сертификата)
        self.browser.get("https://yar.pfdo.ru/app/contracts/create")

        if "Создать запись" not in self.browser.title:
            raise Exception(f"{pfdo_number} - Произошла внутренняя ошибка сервера!")
        pfdo_element = self.browser.find_element_by_name("certificate_number")
        pfdo_element.clear()

        if len(pfdo_number) != 10:
            raise Exception(f"{pfdo_number} - невалидный!")

        pfdo_element.send_keys(pfdo_number)

        sleep(0.5)

        if f"Сертификат {pfdo_number} не найден" in self.browser.page_source:
            raise Exception(f"{pfdo_number} - не найден!")

        # Проверка элементов ФИО на их налчие
        try:
            surname_element = self.get_fio_elem(1)
            firstname_element = self.get_fio_elem(2)
            middlename_element = self.get_fio_elem(3)
        except NoSuchElementException:
            raise Exception(
                f"{pfdo_number} - требуется ввод дополнительного кода!")

        # Ввод ФИО Ребенка
        surname_element.send_keys(surname)
        firstname_element.send_keys(firstname)
        middlename_element.send_keys(middlename)
        sleep(0.25)

        middlename_element.send_keys(Keys.ENTER)
        sleep(1)

        # Проверка на корректность ФИО
        if "Неверно указаны ФИО сертификата." in self.browser.page_source:
            raise Exception(f"{pfdo_number} - Неверные ФИО!")

        # Переход на следующую страницу
        try:
            self.browser.find_element_by_xpath(
                "//button[contains(@class,'success')]").click()
            sleep(1)
        except NoSuchElementException:
            raise Exception(
                f"{pfdo_number} - Произошла внутренняя ошибка сервера!")

        # Страница 2 (Группа)

        # Выбор программы
        program_element = self.browser.find_element_by_xpath(
            "//div[contains(@class,'select-group-step')]/div/div[1]//input")
        program_element.click()
        sleep(0.5)
        program_element.send_keys(self.program)
        sleep(0.5)
        self.list_item_choose()
        sleep(0.25)

        # Выбор модуля
        module_element = self.browser.find_element_by_xpath(
            "//div[contains(@class,'select-group-step')]/div/div[2]//input")
        module_element.click()
        sleep(0.5)
        module_element.send_keys(self.module)
        sleep(0.5)
        self.list_item_choose()
        sleep(0.25)

        # Выбор группы
        group_element = self.browser.find_element_by_xpath(
            "//div[contains(@class,'select-group-step')]//*[2]/input")
        group_element.click()
        sleep(0.5)
        group_element.send_keys(group)
        sleep(0.5)
        self.browser.find_element_by_xpath(
            "//div[contains(@class,'v-list-item v-list-item--link')][1]/span").click()
        sleep(0.5)

        # Проверка на наличие в программе ученика
        if "Вы уже подали заявку на обучение по программе" in self.browser.page_source:
            raise Exception(f"{pfdo_number} - Уже добавлен!")

        # Переход на след. страницу
        self.browser.find_element_by_xpath(
            "//div[contains(@class,'v-card__text')]/button[2]").click()
        sleep(1)

        # Страница 3 (тип создания заявки)
        self.browser.find_element_by_xpath(
            "//div[@class='v-radio theme--light']").click()
        sleep(0.1)
        self.browser.find_element_by_xpath(
            f"//div[@class='mt-2']/button[2]").click()
        sleep(1)

        # Страница 4 (Выбор даты)
        # Открыть календарь
        self.browser.find_element_by_xpath(
            "//div[contains(@class,'create-contract')]//div[@class='v-input__control']").click()
        sleep(0.2)

        # Выбрать необходимый месяц
        target_month_year_string = f"{months_names[self.contract_date.month-1]} {self.contract_date.year} г."
        selected_month_year_string = self.browser.find_element_by_xpath(
            "//div[contains(@class,'v-date-picker-header')]/div/button").text
        selected_year = int(selected_month_year_string.split(" ")[1])
        selected_month = months_names.index(
            selected_month_year_string.split(" ")[0]) + 1

        previous_month_button = self.browser.find_element_by_xpath(
            "//div[contains(@class,'v-date-picker-header')]/button[1]")
        next_month_button = self.browser.find_element_by_xpath(
            "//div[contains(@class,'v-date-picker-header')]/button[2]")

        while selected_month_year_string != target_month_year_string:
            if self.contract_date.year < selected_year or self.contract_date.month < selected_month:
                previous_month_button.click()
            else:
                next_month_button.click()

            sleep(1)
            selected_month_year_string = self.browser.find_element_by_xpath(
                "//div[contains(@class,'v-date-picker-header')]/div/button").text
            selected_year = int(selected_month_year_string.split(" ")[1])
            selected_month = months_names.index(
                selected_month_year_string.split(" ")[0])+1

        sleep(0.5)

        # Выбрать дату
        self.browser.find_element_by_xpath(
            f"//table//div[text()='{self.contract_date.day}']").click()
        sleep(0.2)

        # Подтвердить
        self.browser.find_element_by_xpath(
            "//button[@class='ml-2 v-btn v-btn--has-bg theme--light v-size--default primary']").click()
        sleep(3)

        # Активация заявления
        if "Ожидающий подтверждения" in self.browser.page_source:
            try:
                self.browser.find_element_by_xpath(
                    "//div[@class='v-input pl-3 theme--light v-input--selection-controls v-input--checkbox']").click()
                sleep(0.2)
                self.browser.find_element_by_xpath(
                    "//button[@class='mr-2 v-btn v-btn--has-bg theme--light v-size--default success']").click()
                sleep(0.2)
                print(f"Сертификат {pfdo_number} [{surname}] успешно добавлен")
            except:
                print(f"Сертификат {pfdo_number} не удалось добавить")

    def get_group_info(self, group_id: str):
        """Получить информацию о группе (название, обучающиеся, общее число обучающих[включая заявки])"""
        # Переход на страницу группы
        self.browser.get(f"https://yar.pfdo.ru/app/group-view/{group_id}")
        sleep(1)

        # Получение сведений об группе
        group_name = self.browser.find_element_by_xpath(
            '//span[@class="title"]').text
        group_amount = self.browser.find_element_by_xpath(
            '//div[@class="v-list-item theme--light"][5]/div/div[2]/span').text

        # Переход на список учеников группы
        self.browser.find_element_by_xpath(
            f"//div[@class='v-slide-group__content v-tabs-bar__content']/a[4]").click()
        sleep(3)

        # Получение списка группы
        members = self.browser.find_elements_by_xpath("//table//td[2]")

        # Проверка на доп. учеников
        if not self.check_exists_by_xpath(
                "//div[@class='v-data-footer__icons-after']/button[contains(@class,'v-btn--disabled')]"):
            # Если есть переход на доп. страницу и подгрузка данных
            self.browser.find_element_by_xpath(
                "//div[@class='v-data-footer__icons-after']/button").click()
            sleep(1)
            # Дополение списка группы учениками
            members += self.browser.find_elements_by_xpath("//table//td[2]")

        members = map(lambda x: x.text, members)

        return [group_name, members, int(group_amount)]

    def check_exists_by_xpath(self, xpath):
        try:
            self.browser.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

    def get_fio_elem(self, id):
        return self.browser.find_element_by_xpath(
            f"//div[@class='verification-method-fio']/div[{id}]//input")

    def list_item_choose(self):
        self.browser.find_element_by_xpath(
            "//div[@class='v-list-item__title']/span").click()
        pass

    def close(self):
        self.browser.close()
