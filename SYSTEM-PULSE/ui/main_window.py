import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTabWidget, QTableWidget, QTableWidgetItem, 
    QHeaderView, QProgressBar, QPushButton, QMessageBox
)
from modules.hardware import obter_metricas_gerais, listar_processos_ativos, finalizar_processo
from modules.database import init_db, registrar_metrica

SYSTEM_PULSE_STYLE = """
QMainWindow {
    background-color: #0b0f19;
}
QWidget {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
QLabel {
    color: #38bdf8;
    font-weight: bold;
}
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0f172a;
    border-radius: 8px;
}
QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background-color: #0284c7;
    color: #ffffff;
}
QTableWidget {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    gridline-color: #1e293b;
    color: #f1f5f9;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #38bdf8;
    padding: 6px;
    border: none;
    font-weight: bold;
}
QProgressBar {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #0284c7;
    border-radius: 5px;
}
QProgressBar[warning="true"]::chunk {
    background-color: #ef4444; /* Vermelho de alerta quando passar de 90% */
}
QPushButton {
    background-color: #ef4444;
    color: white;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #dc2626;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Pulse - Monitor de Desempenho")
        self.setGeometry(100, 100, 1000, 720)
        self.setStyleSheet(SYSTEM_PULSE_STYLE)

        init_db()
        self.contador_historico = 0
        self.contador_processos = 0

        self._init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_dados)
        self.timer.start(1000)

    def _init_ui(self):
        tabs = QTabWidget()

        # -------------------------------------------------------------
        # ABA 1: VISÃO GERAL DE HARDWARE
        # -------------------------------------------------------------
        tab_geral = QWidget()
        layout_geral = QVBoxLayout(tab_geral)

        lbl_titulo = QLabel("📊 MÉTRICAS DE HARDWARE E REDE EM TEMPO REAL")
        lbl_titulo.setStyleSheet("font-size: 16px; color: #38bdf8; margin-bottom: 5px;")
        layout_geral.addWidget(lbl_titulo)

        self.lbl_cpu = QLabel("CPU: 0%")
        self.barra_cpu = QProgressBar()
        self.barra_cpu.setMaximum(100)

        self.lbl_ram = QLabel("Memória RAM: 0 GB / 0 GB (0%)")
        self.barra_ram = QProgressBar()
        self.barra_ram.setMaximum(100)

        self.lbl_disco = QLabel("Disco Principal (C:): 0 GB / 0 GB (0%)")
        self.barra_disco = QProgressBar()
        self.barra_disco.setMaximum(100)

        self.lbl_rede = QLabel("🌐 Rede — Download: 0 KB/s  |  Upload: 0 KB/s")
        self.lbl_rede.setStyleSheet("color: #34d399; font-size: 14px; margin-top: 5px;")

        layout_geral.addWidget(self.lbl_cpu)
        layout_geral.addWidget(self.barra_cpu)
        layout_geral.addSpacing(10)
        
        layout_geral.addWidget(self.lbl_ram)
        layout_geral.addWidget(self.barra_ram)
        layout_geral.addSpacing(10)

        layout_geral.addWidget(self.lbl_disco)
        layout_geral.addWidget(self.barra_disco)
        layout_geral.addSpacing(15)

        layout_geral.addWidget(self.lbl_rede)
        layout_geral.addStretch()

        tabs.addTab(tab_geral, "⚡ Visão Geral")

        # -------------------------------------------------------------
        # ABA 2: PROCESSOS ATIVOS
        # -------------------------------------------------------------
        tab_processos = QWidget()
        layout_processos = QVBoxLayout(tab_processos)

        lbl_proc_titulo = QLabel("🖥️ TOP PROCESSOS ATIVOS (Atualiza a cada 5 segundos)")
        lbl_proc_titulo.setStyleSheet("font-size: 14px; color: #38bdf8; margin-bottom: 5px;")
        layout_processos.addWidget(lbl_proc_titulo)

        self.tabela_processos = QTableWidget()
        self.tabela_processos.setColumnCount(4)
        self.tabela_processos.setHorizontalHeaderLabels(["PID", "Nome do Processo", "Uso de CPU (%)", "Uso de Memória (%)"])
        self.tabela_processos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_processos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout_processos.addWidget(self.tabela_processos)

        btn_finalizar = QPushButton("Encerrar Processo Selecionado")
        btn_finalizar.clicked.connect(self.matar_processo_selecionado)
        layout_processos.addWidget(btn_finalizar)

        tabs.addTab(tab_processos, "📋 Processos")

        self.setCentralWidget(tabs)
        
        self.atualizar_metricas_gerais()
        self.atualizar_tabela_processos()

    def atualizar_dados(self):
        self.atualizar_metricas_gerais()

        self.contador_processos += 1
        if self.contador_processos >= 5:
            self.contador_processos = 0
            self.atualizar_tabela_processos()

        self.contador_historico += 1
        if self.contador_historico >= 30:
            self.contador_historico = 0
            try:
                metricas = obter_metricas_gerais()
                registrar_metrica(metricas['cpu'], metricas['ram_percent'], metricas['disco_percent'])
            except Exception as e:
                print(f"Erro ao salvar histórico: {e}")

    def atualizar_metricas_gerais(self):
        metricas = obter_metricas_gerais()
        
        # CPU
        cpu_val = int(metricas['cpu'])
        self.lbl_cpu.setText(f"CPU: {metricas['cpu']}%")
        self.barra_cpu.setValue(cpu_val)
        self.verificar_alerta_barra(self.barra_cpu, cpu_val)

        # RAM (O seu costuma ficar alto, então o limite de 90% vai monitorar com precisão)
        ram_val = int(metricas['ram_percent'])
        self.lbl_ram.setText(f"Memória RAM: {metricas['ram_usada']} GB / {metricas['ram_total']} GB ({ram_val}%)")
        self.barra_ram.setValue(ram_val)
        self.verificar_alerta_barra(self.barra_ram, ram_val)

        # Disco
        disco_val = int(metricas['disco_percent'])
        self.lbl_disco.setText(f"Disco Principal (C:): {metricas['disco_usado']} GB / {metricas['disco_total']} GB ({disco_val}%)")
        self.barra_disco.setValue(disco_val)
        self.verificar_alerta_barra(self.barra_disco, disco_val)

        # Rede
        down = metricas['rede_down']
        up = metricas['rede_up']
        down_str = f"{round(down / 1024, 2)} MB/s" if down >= 1024 else f"{down} KB/s"
        up_str = f"{round(up / 1024, 2)} MB/s" if up >= 1024 else f"{up} KB/s"
        self.lbl_rede.setText(f"🌐 Rede — Download: {down_str}  |  Upload: {up_str}")

    def verificar_alerta_barra(self, barra: QProgressBar, valor: int):
        """Muda a propriedade visual da barra para vermelho se passar de 90%."""
        if valor > 90:
            if barra.property("warning") != "true":
                barra.setProperty("warning", "true")
                barra.style().unpolish(barra)
                barra.style().polish(barra)
        else:
            if barra.property("warning") == "true":
                barra.setProperty("warning", "false")
                barra.style().unpolish(barra)
                barra.style().polish(barra)

    def atualizar_tabela_processos(self):
        processos = listar_processos_ativos()
        self.tabela_processos.setRowCount(len(processos))
        
        for row, proc in enumerate(processos):
            self.tabela_processos.setItem(row, 0, QTableWidgetItem(str(proc['pid'])))
            self.tabela_processos.setItem(row, 1, QTableWidgetItem(str(proc['name'])))
            self.tabela_processos.setItem(row, 2, QTableWidgetItem(f"{proc['cpu_percent']}%"))
            self.tabela_processos.setItem(row, 3, QTableWidgetItem(f"{proc['memory_percent']}%"))

    def matar_processo_selecionado(self):
        linha_atual = self.tabela_processos.currentRow()
        if linha_atual < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um processo na tabela para encerrar.")
            return

        pid_item = self.tabela_processos.item(linha_atual, 0)
        nome_item = self.tabela_processos.item(linha_atual, 1)

        if pid_item:
            pid = int(pid_item.text())
            nome = nome_item.text() if nome_item else "Desconhecido"

            resposta = QMessageBox.question(
                self, "Confirmar Encerramento",
                f"Tem certeza que deseja encerrar o processo '{nome}' (PID: {pid})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if resposta == QMessageBox.StandardButton.Yes:
                sucesso = finalizar_processo(pid)
                if sucesso:
                    QMessageBox.information(self, "Sucesso", f"Processo {nome} encerrado com sucesso.")
                    self.atualizar_tabela_processos()
                else:
                    QMessageBox.critical(self, "Erro", f"Não foi possível encerrar o processo {nome}. Pode ser um processo protegido do sistema.")