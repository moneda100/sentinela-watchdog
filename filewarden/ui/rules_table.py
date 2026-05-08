"""
Tabla para gestionar las reglas de un centinela seleccionado.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QComboBox, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from core.rules import Rule

class RulesTable(QWidget):
    """
    Widget con tabla para mostrar y editar las reglas de un centinela.
    """
    rules_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_sentinel = None
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabla
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Extensión", "Carpeta Destino", "Acción"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        
        layout.addWidget(self.table)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Añadir fila")
        self.btn_del = QPushButton("Eliminar fila seleccionada")
        self.btn_save = QPushButton("Guardar reglas")
        
        self.btn_add.clicked.connect(self.add_empty_row)
        self.btn_del.clicked.connect(self.delete_selected_row)
        self.btn_save.clicked.connect(self.save_rules)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_del)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        
        self.setEnabled(False) # Deshabilitado hasta que se seleccione un centinela
        
    def load_sentinel(self, sentinel):
        """Carga las reglas del centinela en la tabla."""
        self.current_sentinel = sentinel
        self.table.setRowCount(0)
        
        if not sentinel:
            self.setEnabled(False)
            return
            
        self.setEnabled(True)
        for rule in sentinel.rules:
            self._add_rule_to_table(rule)
            
    def _add_rule_to_table(self, rule: Rule):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        ext_item = QTableWidgetItem(rule.extension)
        dest_item = QTableWidgetItem(str(rule.destination))
        dest_item.setFlags(dest_item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Solo editable por doble clic
        
        combo = QComboBox()
        combo.addItems(["move", "copy", "rename"])
        combo.setCurrentText(rule.action)
        
        self.table.setItem(row, 0, ext_item)
        self.table.setItem(row, 1, dest_item)
        self.table.setCellWidget(row, 2, combo)
        
    def add_empty_row(self):
        """Añade una fila en blanco."""
        if not self.current_sentinel:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.table.setItem(row, 0, QTableWidgetItem(".ext"))
        dest_item = QTableWidgetItem(str(Path.home()))
        dest_item.setFlags(dest_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 1, dest_item)
        
        combo = QComboBox()
        combo.addItems(["move", "copy", "rename"])
        self.table.setCellWidget(row, 2, combo)
        
    def delete_selected_row(self):
        """Elimina la fila seleccionada."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            
    def _on_cell_double_clicked(self, row, column):
        """Maneja el doble clic en la celda de destino para abrir el selector de carpetas."""
        if column == 1:
            current_path = self.table.item(row, column).text()
            dir_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Destino", current_path)
            if dir_path:
                self.table.item(row, column).setText(dir_path)
                
    def save_rules(self):
        """Guarda las reglas de la tabla en el objeto centinela actual."""
        if not self.current_sentinel:
            return
            
        new_rules = []
        for row in range(self.table.rowCount()):
            ext_item = self.table.item(row, 0)
            dest_item = self.table.item(row, 1)
            combo = self.table.cellWidget(row, 2)
            
            if not ext_item or not dest_item or not combo:
                continue
                
            extension = ext_item.text().strip()
            if not extension:
                continue
                
            rule = Rule(
                extension=extension,
                destination=Path(dest_item.text()),
                action=combo.currentText()
            )
            new_rules.append(rule)
            
        self.current_sentinel.rules = new_rules
        self.rules_changed.emit()
