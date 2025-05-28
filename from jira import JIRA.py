from flask import Flask
from jira import JIRA
from datetime import datetime
import tkinter as tk
import threading
import time
import pytz
import webbrowser
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Conexão com o Jira
jira = JIRA(
    server='https://jiracpfl.atlassian.net',
    basic_auth=(
        "maicon.manoel@cpfl.com.br",
        "ATATT3xFfGF0iSE1VKAO_bVqiJJUcO6m5Qhmwfpz-dlUzdzOIah0ux0zldjZkLgol92MTdhOVagdM1KdURblzxf5vJnlrEtpxUOa9evR-_vwU1Be938Dg70e4adV9bXXoHoJTcIRC9B7OCpN5SbQ-l0JMBY8eAPugY8LEH2tQrqKGr1Faj6JStw=1E09D3FD"
    )
)
 
status_monitorados = [
    "Aguardando Atendimento",
    "Em Atendimento",
    "Aguardando Fornecedor",
    "Reaberto"
]
 
def buscar_chamados(status_filtro=None):
    if status_filtro:
        jql_query = f'(reporter = currentUser() OR assignee = currentUser()) AND status = "{status_filtro}" AND status NOT IN ("Fechado", "Resolvido", "Finalizado", "Cancelado") ORDER BY created DESC'
    else:
        jql_query = '(reporter = currentUser() OR assignee = currentUser()) AND status NOT IN ("Fechado", "Resolvido", "Finalizado", "Cancelado") ORDER BY created DESC'
 
    issues = jira.search_issues(jql_query, maxResults=100, expand='changelog')
 
    contagem_status = {status: 0 for status in status_monitorados}
    total = 0
 
    for issue in issues:
        status = issue.fields.status.name
        if status in contagem_status:
            contagem_status[status] += 1
            total += 1
 
    return contagem_status, total, issues
 
def abrir_chamados_por_status(status_filtro):
    contagem, total, issues = buscar_chamados(status_filtro)
    if not issues:
        feedback_label.config(text=f"🔴 Sem chamados no status '{status_filtro}', meu chapa.", fg="red")
    else:
        urls = [f"https://jiracpfl.atlassian.net/browse/{issue.key}" for issue in issues]
        feedback_label.config(text=f"📂 Acessar chamados no status '{status_filtro}':", fg="green")
        for url in urls:
            webbrowser.open(url)
 
def buscar_chamados_proximos_de_estourar():
    jql = "assignee = currentUser() AND duedate >= now() AND status NOT IN ('Fechado', 'Resolvido', 'Finalizado', 'Cancelado') ORDER BY duedate ASC"
    issues = jira.search_issues(jql, maxResults=100)
    timezone = pytz.timezone("America/Sao_Paulo")
    proximos_de_estourar = []
 
    for issue in issues:
        duedate = issue.fields.duedate
        if duedate:
            due_time = datetime.strptime(duedate, "%Y-%m-%d").replace(tzinfo=timezone)
            now = datetime.now(timezone)
            if 0 <= (due_time - now).total_seconds() <= 14400:  # até 4 horas para vencer
                proximos_de_estourar.append(issue)
 
    return proximos_de_estourar
 
def abrir_chamados_proximos_de_estourar():
    proximos_de_estourar = buscar_chamados_proximos_de_estourar()
    urls = [f"https://jiracpfl.atlassian.net/browse/{issue.key}" for issue in proximos_de_estourar]
    if urls:
        for url in urls:
            webbrowser.open(url)
    else:
        feedback_label.config(text="🔴 Nenhum chamado próximo de estourar.", fg="red")
 
def atualizar_labels():
    status_label.config(text="🔄 Atualizando...", fg="#FF5722")
    janela.update_idletasks()
    contagem, total, _ = buscar_chamados()
 
    for status, label in labels.items():
        label.config(text=f"{status}: {contagem.get(status, 0)}")
    label_total.config(text=f"📦 Total de Chamados: {total}")
 
    try:
        sla_issues = buscar_chamados_proximos_de_estourar()
        label_sla.config(text=f"⏱️ Chamados SLA próximos: {len(sla_issues)}", fg=COR_ERRO if sla_issues else COR_SUCESSO)
    except Exception as e:
        label_sla.config(text="⏱️ Erro ao buscar SLA", fg=COR_ERRO)
 
    status_label.config(text="✅ Atualizado", fg="#2E7D32")
 
def atualizar_automaticamente():
    while True:
        try:
            atualizar_labels()
        except Exception as e:
            print(f"⚠️ Erro durante atualização: {e}")
            status_label.config(text="❌ Erro ao atualizar", fg="red")
        time.sleep(30)
 
# Interface
janela = tk.Tk()
janela.title("📊 Monitoramento Jira")
janela.geometry("620x780")
janela.configure(bg="#E9EEF6")
 
# Estilo visual
COR_FUNDO = "#E9EEF6"
COR_TEXTO = "#1C1C1C"
COR_TITULO = "#0B2545"
COR_BOTAO = "#1F7A8C"
COR_BOTAO_HOVER = "#155E75"
COR_SUCESSO = "#2E7D32"
COR_ERRO = "#C62828"
 
# Título
titulo = tk.Label(janela, text="📊 Monitoramento Jira", font=("Segoe UI", 24, "bold"), bg=COR_FUNDO, fg=COR_TITULO)
titulo.pack(pady=20)
 
# Status de atualização
status_label = tk.Label(janela, text="⏳ Aguardando atualização...", font=("Segoe UI", 12), bg=COR_FUNDO, fg=COR_TEXTO)
status_label.pack(pady=5)
 
# Feedback
feedback_label = tk.Label(janela, text="🔎 Aqui você verá os resultados", font=("Segoe UI", 10), bg=COR_FUNDO, fg=COR_TEXTO)
feedback_label.pack(pady=5)
 
# Ordena por nome para manter consistência visual
status_monitorados.sort(key=lambda x: len(x))
 
# Labels
labels_frame = tk.Frame(janela, bg=COR_FUNDO)
labels_frame.pack(pady=20)
 
labels = {}
for status in status_monitorados:
    frame_status = tk.Frame(labels_frame, bg=COR_FUNDO)
    frame_status.pack(pady=8, fill='x', padx=40)
 
    lbl = tk.Label(frame_status, text=f"{status}: 0", font=("Segoe UI", 12), bg=COR_FUNDO, fg=COR_TITULO)
    lbl.pack(side="left", anchor="w")
 
    botao = tk.Button(
        frame_status,
        text=f"Vizualizar",
        command=lambda s=status: abrir_chamados_por_status(s),
        bg='black',
        fg="white",
        font=("Segoe UI", 10, "bold"),
        activebackground=COR_BOTAO_HOVER,
        relief="flat",
        width=18
    )
    botao.pack(side="right", anchor="e")
    labels[status] = lbl
 
# Total de chamados
label_total = tk.Label(janela, text="📦 Total de Chamados: 0", font=("Segoe UI", 13, "bold"), bg=COR_FUNDO, fg=COR_TITULO)
label_total.pack(pady=10)
 
# Label SLA
label_sla = tk.Label(janela, text="⏱️ Chamados SLA próximos: 0", font=("Segoe UI", 13, "bold"), bg=COR_FUNDO, fg=COR_ERRO)
label_sla.pack(pady=5)
 
# Botão atualizar
botao_atualizar = tk.Button(
    janela,
    text="🔄 Atualizar Agora",
    command=atualizar_labels,
    bg="#388E3C",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    activebackground="#2E7D32",
    relief="flat",
    width=25
)
botao_atualizar.pack(pady=15)
 
# Botão próximos a estourar
botao_proximos_estourar = tk.Button(
    janela,
    text="🚨 SLA 🚨",
    command=abrir_chamados_proximos_de_estourar,
    bg="#D84315",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    activebackground="#BF360C",
    relief="flat",
    width=25
)
botao_proximos_estourar.pack(pady=10)
 
# Thread de atualização automática
thread = threading.Thread(target=atualizar_automaticamente, daemon=True)
thread.start()
 
# Mainloop
janela.mainloop()