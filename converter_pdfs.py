import shutil
import threading
from pathlib import Path
from typing import Optional, Callable
import customtkinter as ctk
import pdfplumber
import pandas as pd

# ==============================================================================
#  BACKEND (Lógica de Processamento)
# ==============================================================================
class PDFProcessor:
    def __init__(self, log_callback: Callable[[str], None], progress_callback: Callable[[float], None]):
        self.log = log_callback
        self.update_progress = progress_callback

    def extrair_tabela(self, caminho_pdf: Path) -> Optional[pd.DataFrame]:
        dados_totais = []
        try:
            with pdfplumber.open(caminho_pdf) as pdf:
                if len(pdf.pages) == 0: return None
                for page in pdf.pages:
                    tabela = page.extract_table()
                    if tabela:
                        dados_totais.extend([linha for linha in tabela if any(linha)])
        except Exception:
            raise 

        if not dados_totais: return None

        header = dados_totais[0]
        dados = dados_totais[1:] if len(dados_totais) > 1 else []
        header = [str(h) if h else f"col_{i}" for i, h in enumerate(header)]
        return pd.DataFrame(dados, columns=header)

    def executar_lote(self, pasta_origem: Path):
        self.log(f">>> INICIANDO OPERAÇÃO EM: {pasta_origem.name}\n")
        
        dir_convertidos = pasta_origem / "01_Convertidos"
        dir_escaneados = pasta_origem / "02_Escaneados_Sem_Texto"
        dir_falhas = pasta_origem / "03_Falhas_Corrompidos"
        
        for p in [dir_convertidos, dir_escaneados, dir_falhas]:
            p.mkdir(exist_ok=True)

        arquivos = list(pasta_origem.glob("*.pdf"))
        total = len(arquivos)
        
        if total == 0:
            self.log("[!] Nenhum arquivo PDF encontrado.")
            self.update_progress(0)
            return

        sucesso = 0
        escaneados = 0
        falhas = 0
        lista_dfs = []

        for i, arquivo in enumerate(arquivos):
            progresso = (i + 1) / total
            self.update_progress(progresso)
            nome = arquivo.name
            
            try:
                df = self.extrair_tabela(arquivo)
                if df is None:
                    shutil.move(str(arquivo), str(dir_escaneados / nome))
                    self.log(f"[IMG] Movido: {nome}")
                    escaneados += 1
                else:
                    df.to_excel(dir_convertidos / (arquivo.stem + ".xlsx"), index=False)
                    df_temp = df.copy()
                    df_temp.insert(0, 'Origem', nome)
                    lista_dfs.append(df_temp)
                    self.log(f"[OK] Convertido: {nome}")
                    sucesso += 1
            except Exception as e:
                shutil.move(str(arquivo), str(dir_falhas / nome))
                self.log(f"[ERR] Falha: {nome} | {str(e)}")
                falhas += 1

        if lista_dfs:
            self.log("\n>>> Gerando Relatório Consolidado...")
            try:
                pd.concat(lista_dfs, ignore_index=True).to_excel(pasta_origem / "Relatorio_Geral_Master.xlsx", index=False)
                self.log("[OK] Relatório Geral criado.")
            except Exception as e:
                self.log(f"[ERR] Erro no consolidado: {e}")

        self.log("\n" + "="*30)
        self.log(f"RESUMO FINAL:")
        self.log(f"   Sucessos:   {sucesso}")
        self.log(f"   Escaneados: {escaneados}")
        self.log(f"   Falhas:     {falhas}")
        self.log("="*30)
        self.update_progress(1.0)

# ==============================================================================
#  FRONTEND (Interface Gráfica Premium)
# ==============================================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurações Iniciais ---
        self.title("PDF Extract Pro")
        
        # Cores Personalizadas (Hex)
        self.color_sidebar = "#1F2937"    # Cinza Azulado Escuro
        self.color_bg = "#111827"         # Quase preto
        
        # --- ATUALIZAÇÃO 1: Cor mais viva (Vivid Green / Neon) ---
        self.color_accent = "#00E676"     # Verde Neon Vibrante
        self.color_accent_hover = "#00C853" # Verde um pouco mais escuro para hover
        self.color_panel = "#374151"      # Cinza Painel

        # --- ATUALIZAÇÃO 2: Centralização da Janela ---
        window_width = 900
        window_height = 650
        
        # Pega a largura e altura da tela do monitor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calcula a posição X e Y para centralizar
        pos_x = (screen_width - window_width) // 2
        pos_y = (screen_height - window_height) // 2
        
        # Define a geometria centralizada
        self.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")

        ctk.set_appearance_mode("Dark") 
        ctk.set_default_color_theme("dark-blue")

        self.pasta_selecionada: Optional[Path] = None

        # --- Layout Principal ---
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)    

        self.setup_sidebar()
        self.setup_main_area()

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=self.color_sidebar)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) 

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="PDF\nEXTRACTOR\nPRO", 
            font=ctk.CTkFont(size=24, weight="bold", family="Helvetica")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 20))

        self.btn_home = self.create_sidebar_btn("Dashboard", row=1, state="normal")
        self.btn_settings = self.create_sidebar_btn("Configurações", row=2, state="disabled")
        self.btn_help = self.create_sidebar_btn("Ajuda", row=3, state="disabled")

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode_event,
            fg_color=self.color_panel
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 20))

    def create_sidebar_btn(self, text, row, state="normal"):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            fg_color="transparent", 
            text_color=("gray10", "gray90"), 
            hover_color=("gray70", "gray30"),
            anchor="w",
            state=state,
            height=40
        )
        btn.grid(row=row, column=0, sticky="ew", padx=20, pady=5)
        return btn

    def setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_frame.grid_rowconfigure(2, weight=1) 
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame, 
            text="Painel de Controle de Automação",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Card de Ação
        self.action_card = ctk.CTkFrame(self.main_frame, fg_color=self.color_panel, corner_radius=15)
        self.action_card.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.action_card.grid_columnconfigure(0, weight=1)

        # Input Path
        self.entry_path = ctk.CTkEntry(
            self.action_card, 
            placeholder_text="Selecione a pasta contendo os PDFs...",
            height=40,
            border_width=0,
            fg_color=("gray90", "gray20")
        )
        self.entry_path.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.entry_path.configure(state="disabled")

        # Botão Buscar Pasta
        self.btn_browse = ctk.CTkButton(
            self.action_card, 
            text="📂 Buscar Pasta", 
            command=self.selecionar_pasta,
            height=40,
            fg_color="#4B5563",
            hover_color="#374151"
        )
        self.btn_browse.grid(row=0, column=1, padx=(0, 20), pady=20)

        # Botão Iniciar (Atualizado com cor vibrante e texto escuro para contraste)
        self.btn_start = ctk.CTkButton(
            self.action_card,
            text="INICIAR PROCESSAMENTO 🚀",
            command=self.iniciar_thread,
            height=50,
            fg_color=self.color_accent,       # Cor Neon
            hover_color=self.color_accent_hover,
            text_color="#000000",             # Texto preto para contraste no neon
            font=ctk.CTkFont(size=16, weight="bold"),
            state="disabled"
        )
        self.btn_start.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        # Barra de Progresso
        self.progressbar = ctk.CTkProgressBar(self.action_card, progress_color=self.color_accent)
        self.progressbar.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progressbar.set(0)

        # Terminal Log
        self.lbl_log = ctk.CTkLabel(self.main_frame, text="Log de Execução:", anchor="w")
        self.lbl_log.grid(row=2, column=0, sticky="nw")

        self.txt_log = ctk.CTkTextbox(
            self.main_frame, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#000000",
            text_color="#00FF00" 
        )
        self.txt_log.grid(row=3, column=0, sticky="nsew", pady=(5, 0))
        self.txt_log.configure(state="disabled")

    # --- Lógica de Eventos ---

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def selecionar_pasta(self):
        pasta = ctk.filedialog.askdirectory()
        if pasta:
            self.pasta_selecionada = Path(pasta)
            self.entry_path.configure(state="normal")
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, str(self.pasta_selecionada))
            self.entry_path.configure(state="disabled")
            self.btn_start.configure(state="normal")
            self.log_message(f"> Pasta carregada: {self.pasta_selecionada}")
            self.progressbar.set(0)

    def log_message(self, message: str):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", message + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def update_progress_bar(self, value: float):
        self.progressbar.set(value)

    def iniciar_thread(self):
        if not self.pasta_selecionada: return
        
        self.btn_start.configure(state="disabled", text="PROCESSANDO... AGUARDE")
        self.btn_browse.configure(state="disabled")
        self.log_message("\n--- Inicializando Engine ---")
        
        thread = threading.Thread(target=self.executar_backend)
        thread.start()

    def executar_backend(self):
        processor = PDFProcessor(
            log_callback=self.safe_log, 
            progress_callback=self.safe_progress
        )
        processor.executar_lote(self.pasta_selecionada)
        self.after(0, self.finalizar_processo)

    def safe_log(self, text):
        self.after(0, lambda: self.log_message(text))

    def safe_progress(self, val):
        self.after(0, lambda: self.update_progress_bar(val))

    def finalizar_processo(self):
        self.btn_start.configure(state="normal", text="INICIAR PROCESSAMENTO 🚀")
        self.btn_browse.configure(state="normal")
        self.log_message("\n>>> PROCESSO CONCLUÍDO! <<<")
        self.progressbar.configure(progress_color="#3B8ED0")

if __name__ == "__main__":
    app = App()
    app.mainloop()