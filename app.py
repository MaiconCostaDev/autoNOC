from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from jira import JIRA
from datetime import datetime
import threading
import time
import pytz
import webbrowser

app = Flask(__name__)
socketio = SocketIO(app)

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

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    print("Cliente conectado")

@socketio.on('disconnect')
def on_disconnect():
    print("Cliente desconectado")

@socketio.on('atualizar')
def on_atualizar():
    try:
        contagem, total, issues = buscar_chamados()
        proximos_de_estourar = buscar_chamados_proximos_de_estourar()
        
        emit('status', {'contagem': contagem, 'total': total, 'sla': len(proximos_de_estourar)})
    except Exception as e:
        emit('error', {'message': f"Erro ao atualizar: {str(e)}"})

def atualizar_automaticamente():
    while True:
        try:
            socketio.emit('atualizar')
        except Exception as e:
            print(f"⚠️ Erro durante atualização: {e}")
        time.sleep(30)

if __name__ == '__main__':
    # Thread para atualizar automaticamente
    thread = threading.Thread(target=atualizar_automaticamente, daemon=True)
    thread.start()

    # Rodar o servidor Flask com SocketIO
    socketio.run(app, host="0.0.0.0", port=5000)
