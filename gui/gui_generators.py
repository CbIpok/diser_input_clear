#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox,
    QLabel, QComboBox, QLineEdit, QTextEdit, QPushButton, QFileDialog, QCheckBox, QFormLayout
)
from PyQt5.QtCore import Qt

# Определение параметров для каждого генератора
generator_params = {
    "generate_data": {
        "script": "generate_data.py",
        "params": [
            {"flag": "--form", "type": "choice", "choices": ["gradient_x", "gradient_y", "parabola", "parabola_sine"],
             "default": "gradient_x", "label": "Форма"},
            {"flag": "--output", "type": "str", "default": "data/output.txt", "label": "Путь вывода"},
            {"flag": "--min_value", "type": "float", "default": 0.0, "label": "Мин. значение"},
            {"flag": "--max_value", "type": "float", "default": 1.0, "label": "Макс. значение"},
            {"flag": "--sin_amp", "type": "float", "default": 0.5, "label": "Амплитуда синуса",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
            {"flag": "--sin_period_x", "type": "int", "default": 50, "label": "Период X",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
            {"flag": "--sin_period_y", "type": "int", "default": 50, "label": "Период Y",
             "depends_on": {"flag": "--form", "value": "parabola_sine"}},
        ]
    },
    "generate_subduction": {
        "script": "generate_subduction.py",
        "params": [
            {"flag": "--form", "type": "choice", "choices": ["gaussian", "double_gaussian"],
             "default": "gaussian", "label": "Форма"},
            {"flag": "--output", "type": "str", "default": "subduction/output.txt", "label": "Путь вывода"},
            {"flag": "--sigma", "type": "float", "default": 50.0, "label": "Sigma"},
            {"flag": "--amplitude", "type": "float", "default": 1.0, "label": "Амплитуда",
             "depends_on": {"flag": "--form", "value": "gaussian"}},
            {"flag": "--amplitude1", "type": "float", "default": 1.0, "label": "Амплитуда верхней",
             "depends_on": {"flag": "--form", "value": "double_gaussian"}},
            {"flag": "--amplitude2", "type": "float", "default": 1.0, "label": "Амплитуда нижней",
             "depends_on": {"flag": "--form", "value": "double_gaussian"}},
        ]
    },
    "generate_basis": {
        "script": "generate_basis.py",
        "params": [
            {"flag": "--tile-height", "type": "int", "default": 50, "label": "Высота плитки"},
            {"flag": "--tile-width", "type": "int", "default": 100, "label": "Ширина плитки"},
            {"flag": "--output-dir", "type": "str", "default": "basis_functions", "label": "Директория вывода"},
            {"flag": "--value", "type": "float", "default": 1.0, "label": "Значение"},
            {"flag": "--visualize", "type": "bool", "default": False, "label": "Визуализировать"},
        ]
    }
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор BAT-файла для запуска генераторов")
        self.resize(800, 600)

        # Словари для хранения виджетов параметров и их значений (для сохранения при обновлении формы)
        self.paramWidgets = {}
        self.paramValues = {}

        central = QWidget(self)
        self.setCentralWidget(central)

        mainLayout = QHBoxLayout(central)

        # Левая панель
        leftWidget = QWidget()
        leftLayout = QVBoxLayout(leftWidget)

        # Выбор генератора
        leftLayout.addWidget(QLabel("Выберите генератор:"))
        self.genCombo = QComboBox()
        self.genCombo.addItems(list(generator_params.keys()))
        self.genCombo.currentIndexChanged.connect(self.updateParameterLayout)
        leftLayout.addWidget(self.genCombo)

        # Группа параметров
        self.paramGroup = QGroupBox("Параметры")
        self.paramFormLayout = QFormLayout()
        self.paramGroup.setLayout(self.paramFormLayout)
        leftLayout.addWidget(self.paramGroup)

        # Кнопка для добавления команды
        self.addButton = QPushButton("Добавить текст запуска")
        self.addButton.clicked.connect(self.addCommand)
        leftLayout.addWidget(self.addButton)

        leftLayout.addStretch()
        mainLayout.addWidget(leftWidget, 1)

        # Правая панель
        rightWidget = QWidget()
        rightLayout = QVBoxLayout(rightWidget)
        self.textEdit = QTextEdit()
        self.textEdit.setAcceptRichText(False)
        # QTextEdit по умолчанию поддерживает стандартные сочетания клавиш (Ctrl+C/V/X)
        rightLayout.addWidget(self.textEdit)
        self.saveButton = QPushButton("Сохранить в файл")
        self.saveButton.clicked.connect(self.saveToFile)
        rightLayout.addWidget(self.saveButton)
        mainLayout.addWidget(rightWidget, 2)

        self.updateParameterLayout()  # инициализируем параметры

    def clearParameterLayout(self):
        # Сохраняем текущие значения (если есть) перед очисткой
        for flag, widget in self.paramWidgets.items():
            if isinstance(widget, QComboBox):
                self.paramValues[flag] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                self.paramValues[flag] = widget.text()
            elif isinstance(widget, QCheckBox):
                self.paramValues[flag] = widget.isChecked()
        # Удаляем все элементы из формы
        while self.paramFormLayout.count():
            item = self.paramFormLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.paramWidgets.clear()

    def updateParameterLayout(self):
        self.clearParameterLayout()
        currentGen = self.genCombo.currentText()
        params = generator_params[currentGen]["params"]

        for param in params:
            # Если параметр зависит от другой, проверяем условие
            if "depends_on" in param:
                ctrlFlag = param["depends_on"]["flag"]
                reqValue = str(param["depends_on"]["value"])
                # Если в сохранённых значениях есть controlling параметр, сравниваем; иначе используем дефолт
                ctrlVal = self.paramValues.get(ctrlFlag, str(param.get("default", "")))
                if str(ctrlVal) != reqValue:
                    continue

            flag = param["flag"]
            label = param["label"]
            pType = param["type"]
            default = self.paramValues.get(flag, str(param.get("default", "")))

            if pType == "choice":
                widget = QComboBox()
                widget.addItems(param["choices"])
                index = widget.findText(default)
                if index >= 0:
                    widget.setCurrentIndex(index)
                else:
                    widget.setCurrentIndex(0)
                # При изменении управляющего параметра обновляем всю форму
                widget.currentIndexChanged.connect(self.updateParameterLayout)
            elif pType in ["int", "float", "str"]:
                widget = QLineEdit()
                widget.setText(default)
            elif pType == "bool":
                widget = QCheckBox()
                widget.setChecked(True if default in [True, "True", "true"] else False)
            else:
                widget = QLineEdit()
                widget.setText(default)
            self.paramWidgets[flag] = widget
            self.paramFormLayout.addRow(label + ":", widget)

    def addCommand(self):
        currentGen = self.genCombo.currentText()
        script = generator_params[currentGen]["script"]
        # Добавляем префикс для установки PYTHONPATH
        cmdParts = [f"set PYTHONPATH=%CD% && python scripts/{script}"]

        params = generator_params[currentGen]["params"]
        for param in params:
            flag = param["flag"]
            # Проверка зависимых параметров
            if "depends_on" in param:
                ctrlFlag = param["depends_on"]["flag"]
                reqValue = str(param["depends_on"]["value"])
                ctrlWidget = self.paramWidgets.get(ctrlFlag)
                if ctrlWidget:
                    if isinstance(ctrlWidget, QComboBox):
                        if ctrlWidget.currentText() != reqValue:
                            continue
                    elif isinstance(ctrlWidget, QLineEdit):
                        if ctrlWidget.text() != reqValue:
                            continue
                    elif isinstance(ctrlWidget, QCheckBox):
                        if str(ctrlWidget.isChecked()) != reqValue:
                            continue
                else:
                    continue

            widget = self.paramWidgets.get(flag)
            if widget is None:
                continue
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            elif isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QCheckBox):
                value = widget.isChecked()
            else:
                value = ""
            if param["type"] == "bool":
                if value:
                    cmdParts.append(flag)
            else:
                if value != "":
                    cmdParts.append(f"{flag} {value}")
        cmdLine = " ".join(cmdParts)
        self.textEdit.append(cmdLine)

    def saveToFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Сохранить BAT файл", "", "BAT Files (*.bat);;All Files (*)")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(self.textEdit.toPlainText())
            except Exception as e:
                print("Ошибка сохранения:", e)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
