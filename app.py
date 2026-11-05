import os
import json
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

DB_FILE = "siscord_database.json"

def load_data():
    if not os.path.exists(DB_FILE):
        initial_data = {
            "annotations": {},
            "files": [],
            "cientes": {}
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"annotations": {}, "files": [], "cientes": {}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    return render_template_string(HTML_CONTENT)

@app.route("/api/data", methods=["GET"])
def get_data():
    return jsonify(load_data())

@app.route("/api/data", methods=["POST"])
def update_data():
    req_data = request.json
    if not req_data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    save_data(req_data)
    return jsonify({"status": "ok"})

@app.route("/api/clear-files", methods=["POST"])
def clear_files():
    data = load_data()
    data["files"] = []
    save_data(data)
    return jsonify({"status": "ok"})

@app.route("/api/clear-cientes", methods=["POST"])
def clear_cientes():
    data = load_data()
    data["cientes"] = {}
    save_data(data)
    return jsonify({"status": "ok"})

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="pt-BR" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISCORD - Sistema de Controle de Relatório e Documentação</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts Inter -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        military: {
                            50: '#f0fdf4',
                            100: '#dcfce7',
                            200: '#bbf7d0',
                            600: '#166534',
                            700: '#14532d',
                            800: '#064e3b',
                            900: '#022c22'
                        }
                    },
                    fontFamily: {
                        sans: ['Inter', 'sans-serif']
                    }
                }
            }
        }
    </script>
</head>
<body class="h-full bg-slate-100 text-slate-800 font-sans flex flex-col selection:bg-amber-500 selection:text-military-900">

    <!-- Cabeçalho Institucional -->
    <header class="bg-military-900 text-white shadow-lg border-b-4 border-amber-500 relative z-20">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-3.5">
                <div class="bg-gradient-to-br from-military-700 to-military-900 p-3 rounded-xl border border-amber-500/40 shadow-md flex items-center justify-center">
                    <i class="fa-solid fa-shield-halved text-amber-400 text-2xl"></i>
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <span class="text-[10px] uppercase tracking-widest text-amber-400 font-bold px-2 py-0.5 bg-amber-950/80 rounded border border-amber-500/40 shadow-xs">Exército Brasileiro</span>
                        <span class="text-xs text-slate-300 font-medium">SISCORD v7.1 - Cmdo DAAe Ex (Nuvem em Tempo Real)</span>
                    </div>
                    <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight text-white mt-0.5">Sistema de Controle de Relatório e Documentação</h1>
                </div>
            </div>
            
            <div class="flex items-center gap-3 bg-military-800/90 px-4 py-2.5 rounded-xl border border-military-700 shadow-inner">
                <div id="auth-status-indicator" class="w-3.5 h-3.5 bg-red-500 rounded-full shadow-sm"></div>
                <div class="text-xs">
                    <p id="auth-status-title" class="font-bold text-white">Perfil: OMDS (Visualização)</p>
                    <p id="auth-status-desc" class="text-slate-300">Acesso restrito à unidade</p>
                </div>
                <button onclick="openAuthModal()" class="ml-2 px-3 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-military-900 font-bold rounded-lg text-xs transition-all shadow-sm flex items-center gap-1.5">
                    <i class="fa-solid fa-lock text-[10px]"></i> Cmdo
                </button>
            </div>
        </div>
    </header>

    <!-- Navegação por Abas -->
    <nav class="bg-white border-b border-slate-200 shadow-sm overflow-x-auto sticky top-0 z-10">
        <div class="max-w-7xl mx-auto px-4 flex space-x-1.5 py-2.5 min-w-max" id="om-tabs-container"></div>
    </nav>

    <!-- Sub-Abas -->
    <div class="bg-slate-50 border-b border-slate-200 py-2.5 shadow-xs">
        <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-3">
            <div class="flex space-x-2 w-full sm:w-auto">
                <button onclick="switchSubTab('calendar')" id="btn-sub-calendar" class="flex-1 sm:flex-none px-4 py-2 bg-military-700 text-white rounded-xl text-xs font-bold shadow-sm flex items-center justify-center gap-2 transition-all">
                    <i class="fa-regular fa-calendar-days"></i> Calendário (01 a 31)
                </button>
                <button onclick="switchSubTab('files')" id="btn-sub-files" class="flex-1 sm:flex-none px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-100 flex items-center justify-center gap-2 transition-all shadow-xs">
                    <i class="fa-solid fa-folder-open text-military-700"></i> Arquivos & Retorno
                    <span id="badge-active-files" class="ml-1 bg-military-700 text-white px-2 py-0.5 rounded-full text-[10px] font-bold">0</span>
                </button>
            </div>
            <div id="current-om-indicator" class="text-xs font-bold text-military-900 bg-amber-100 px-3.5 py-1.5 rounded-xl border border-amber-300 shadow-xs flex items-center gap-2">
                <i class="fa-solid fa-building-shield text-amber-700"></i> Visualizando: Cmdo DAAe Ex
            </div>
        </div>
    </div>

    <!-- Conteúdo Principal -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 overflow-y-auto space-y-6">
        
        <!-- ALERTA DE PRAZOS VENCENDO HOJE -->
        <div id="urgent-alert-banner" class="hidden bg-red-50 border-4 border-red-600 rounded-2xl p-5 shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-4 animate-bounce ring-4 ring-red-400/50">
            <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-red-600 text-white rounded-xl flex items-center justify-center text-3xl shadow-md shrink-0">
                    <i class="fa-solid fa-triangle-exclamation"></i>
                </div>
                <div>
                    <h3 class="text-red-900 font-black text-lg tracking-wider uppercase">ATENÇÃO OMDS! Novo Documento / Aviso Recebido.</h3>
                    <p id="urgent-alert-text" class="text-xs text-red-800 font-bold mt-1">Confirme o recebimento clicando no botão Ciente.</p>
                </div>
            </div>
            <button onclick="acknowledgeUrgentDeadline()" class="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-extrabold rounded-xl text-sm shadow-xl transition-all whitespace-nowrap flex items-center gap-2 border-2 border-white">
                <i class="fa-solid fa-check-double text-base"></i> Ciente
            </button>
        </div>

        <!-- PAINEL DE CONTROLE DE CIENTES -->
        <div id="cmdo-cientes-panel" class="hidden bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
            <div class="flex justify-between items-center mb-3">
                <h3 class="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <i class="fa-solid fa-clipboard-check text-military-700"></i> Histórico de Recebido - OMDS
                </h3>
                <button onclick="clearCmdoCientes()" class="text-xs bg-red-50 text-red-600 hover:bg-red-100 font-bold px-2.5 py-1 rounded-lg border border-red-200 transition-colors shadow-xs">
                    <i class="fa-solid fa-trash-can mr-1"></i> Limpar Histórico
                </button>
            </div>
            <div id="cmdo-cientes-list" class="space-y-2 max-h-48 overflow-y-auto pr-2"></div>
        </div>

        <!-- SEÇÃO 1: CALENDÁRIO MENSAL -->
        <section id="section-calendar" class="space-y-6">
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6 flex flex-col sm:flex-row justify-between items-center gap-4">
                <div>
                    <h2 id="calendar-header-title" class="text-lg font-bold text-slate-900 flex items-center gap-2.5">
                        <i class="fa-solid fa-calendar-check text-military-700"></i> Calendário Administrativo
                    </h2>
                    <p id="calendar-header-desc" class="text-sm text-slate-500 mt-0.5">Selecione um dia (01 a 31) para gerenciar anotações direcionadas.</p>
                </div>
                <div class="flex items-center gap-3 bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
                    <label for="select-month" class="text-xs font-bold uppercase text-slate-700">Mês / Ano:</label>
                    <input type="month" id="select-month" class="px-3 py-1.5 border border-slate-300 rounded-lg text-sm bg-white font-medium focus:outline-none focus:ring-2 focus:ring-military-600" min="2020-01" max="2040-12" onchange="renderCalendar()">
                </div>
            </div>
            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
                <div id="calendar-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-3.5"></div>
            </div>
        </section>

        <!-- SEÇÃO 2: GESTÃO DE ARQUIVOS E RETORNOS -->
        <section id="section-files" class="space-y-6 hidden">
            <div id="upload-card-container" class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
                <h2 id="upload-section-title" class="text-lg font-bold text-slate-900 flex items-center gap-2.5 mb-1">
                    <i class="fa-solid fa-cloud-arrow-up text-military-700"></i> Envio de Documentos / Diretrizes
                </h2>
                <p id="upload-section-desc" class="text-sm text-slate-500 mb-5">Envie arquivos e selecione as OMDS destinatárias.</p>
                
                <div id="cmdo-target-selection" class="mb-5 p-4 bg-slate-50 rounded-xl border border-slate-200">
                    <div class="flex justify-between items-center mb-2">
                        <label class="block text-xs font-bold uppercase text-slate-700">Selecione as OMDS Destinatárias:</label>
                        <div class="space-x-2">
                            <button type="button" onclick="selectAllOm(true)" class="text-[11px] text-military-700 hover:underline font-semibold">Marcar Todas</button>
                            <span class="text-slate-300">|</span>
                            <button type="button" onclick="selectAllOm(false)" class="text-[11px] text-red-600 hover:underline font-semibold">Desmarcar</button>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2.5" id="checkbox-om-list"></div>
                </div>

                <div class="border-2 border-dashed border-slate-300 rounded-2xl p-8 text-center hover:border-military-600 transition-all bg-slate-50 relative group cursor-pointer shadow-xs mb-4" onclick="document.getElementById('file-input').click()">
                    <input type="file" id="file-input" class="hidden" multiple onchange="handleFileUpload(event)">
                    <div class="w-16 h-16 bg-military-100 text-military-700 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform shadow-sm">
                        <i class="fa-solid fa-file-arrow-up text-2xl"></i>
                    </div>
                    <p class="font-bold text-slate-700">Clique para selecionar arquivos ou arraste-os para esta área</p>
                    <p class="text-xs text-slate-400 mt-1">Sincronizado automaticamente via nuvem em tempo real.</p>
                </div>

                <div class="max-w-xs">
                    <label class="block text-xs font-bold uppercase text-slate-700 mb-1">Data Limite / Prazo (Opcional):</label>
                    <input type="date" id="file-due-date" class="w-full px-3.5 py-2 border border-slate-300 rounded-xl text-xs font-semibold bg-white focus:outline-none focus:ring-2 focus:ring-military-600">
                </div>
            </div>

            <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 sm:p-6">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5">
                    <h3 class="font-bold text-slate-900 flex items-center gap-2.5 text-base">
                        <i class="fa-solid fa-box-archive text-military-700"></i> Repositório de Documentos e Sinal Verde de Retorno
                    </h3>
                    <div class="flex items-center gap-2.5 w-full sm:w-auto">
                        <div class="relative w-full sm:w-72">
                            <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
                                <i class="fa-solid fa-magnifying-glass text-xs"></i>
                            </span>
                            <input type="text" id="search-file" placeholder="Pesquisar por nome ou OM..." class="pl-9 pr-3 py-2 text-sm border border-slate-300 rounded-xl w-full focus:outline-none focus:ring-2 focus:ring-military-600 bg-slate-50" oninput="renderFileList()">
                        </div>
                        <button id="btn-clear-history" onclick="clearAllFiles()" class="text-xs bg-red-50 text-red-600 hover:bg-red-100 font-bold px-3 py-2 rounded-xl border border-red-200 transition-colors whitespace-nowrap hidden shadow-xs">
                            <i class="fa-solid fa-trash-can mr-1"></i> Limpar Tudo
                        </button>
                    </div>
                </div>

                <div class="overflow-x-auto rounded-xl border border-slate-200">
                    <table class="w-full text-left border-collapse">
                        <thead>
                            <tr class="border-b border-slate-200 text-xs font-bold text-slate-600 uppercase bg-slate-50 tracking-wider">
                                <th class="py-3.5 px-4">Nome do Arquivo</th>
                                <th class="py-3.5 px-4">Remetente / Destinatário</th>
                                <th class="py-3.5 px-4">Status / Retorno</th>
                                <th class="py-3.5 px-4">Data/Hora</th>
                                <th class="py-3.5 px-4 text-right">Ações</th>
                            </tr>
                        </thead>
                        <tbody id="file-table-body" class="divide-y divide-slate-100 text-sm"></tbody>
                    </table>
                </div>
                <div id="no-files-msg" class="text-center py-12 text-slate-400 hidden">
                    <i class="fa-regular fa-folder-open text-4xl mb-3 text-slate-300"></i>
                    <p class="font-medium text-slate-600">Nenhum arquivo no histórico desta aba.</p>
                </div>
            </div>
        </section>
    </main>

    <!-- MODAL DE ANOTAÇÃO -->
    <div id="modal-annotation" class="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-200">
            <div class="bg-military-900 text-white px-6 py-4 flex justify-between items-center">
                <h3 id="modal-title" class="font-bold text-base flex items-center gap-2">
                    <i class="fa-solid fa-pen-to-square text-amber-400"></i> Anotação do Dia
                </h3>
                <button onclick="closeAnnotationModal()" class="text-slate-300 hover:text-white p-1.5 rounded-lg"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div class="p-6 space-y-5">
                <div id="annotation-targets-box">
                    <div class="flex justify-between items-center mb-2">
                        <label class="block text-xs font-bold uppercase text-slate-700">Direcionar anotação para quais OMDS?</label>
                        <div class="space-x-2">
                            <button type="button" onclick="selectAnnotationOm(true)" class="text-[11px] text-military-700 hover:underline font-semibold">Todas</button>
                            <span class="text-slate-300">|</span>
                            <button type="button" onclick="selectAnnotationOm(false)" class="text-[11px] text-red-600 hover:underline font-semibold">Nenhuma</button>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-2 max-h-44 overflow-y-auto p-2.5 border border-slate-200 rounded-xl bg-slate-50" id="annotation-checkbox-list"></div>
                </div>
                <div>
                    <label class="block text-xs font-bold uppercase text-slate-600 mb-1.5 font-medium">Texto da Anotação / Diretriz:</label>
                    <textarea id="annotation-text" rows="5" class="w-full p-3.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-military-600 bg-slate-50 font-medium text-slate-700" placeholder="Insira as diretrizes..."></textarea>
                </div>
            </div>
            <div class="bg-slate-50 px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
                <button onclick="closeAnnotationModal()" class="px-4 py-2.5 border border-slate-300 text-slate-700 rounded-xl text-sm font-semibold hover:bg-slate-100">Cancelar</button>
                <button onclick="saveAnnotation()" class="px-5 py-2.5 bg-military-700 text-white rounded-xl text-sm font-semibold hover:bg-military-800 shadow-sm flex items-center gap-2"><i class="fa-solid fa-floppy-disk"></i> Salvar</button>
            </div>
        </div>
    </div>

    <!-- MODAL DE SENHA -->
    <div id="modal-auth" class="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 space-y-4 border border-slate-200 text-center">
            <div class="w-14 h-14 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto text-2xl border border-amber-300">
                <i class="fa-solid fa-key"></i>
            </div>
            <div>
                <h3 id="modal-auth-title" class="font-bold text-lg text-slate-900">Acesso Restrito</h3>
                <p id="modal-auth-desc" class="text-xs text-slate-500 mt-1">Digite a senha da OMDS.</p>
            </div>
            <input type="password" id="auth-password-input" placeholder="SENHA" class="w-full px-4 py-3 border border-slate-300 rounded-xl text-sm text-center font-bold tracking-widest focus:outline-none focus:ring-2 focus:ring-military-600 bg-slate-50" onkeydown="if(event.key==='Enter') verifyCommandPassword()">
            <div class="flex gap-2.5 pt-2">
                <button onclick="closeAuthModal()" class="flex-1 py-2.5 border border-slate-300 text-slate-700 font-bold rounded-xl text-xs hover:bg-slate-100">Cancelar</button>
                <button onclick="verifyCommandPassword()" class="flex-1 py-2.5 bg-military-700 text-white font-bold rounded-xl text-xs hover:bg-military-800 shadow-sm">Autenticar</button>
            </div>
        </div>
    </div>

    <!-- MODAL DE PREVIEW -->
    <div id="modal-preview" class="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden border border-slate-200">
            <div class="bg-military-900 text-white px-6 py-4 flex justify-between items-center">
                <h3 id="preview-modal-title" class="font-bold text-base truncate flex items-center gap-2"><i class="fa-solid fa-file-lines text-amber-400"></i> Visualizar Arquivo</h3>
                <button onclick="closePreviewModal()" class="text-slate-300 hover:text-white p-1"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            <div class="p-6 flex-1 overflow-auto bg-slate-100 flex items-center justify-center" id="preview-content-container"></div>
            <div class="bg-slate-50 px-6 py-3.5 border-t border-slate-200 flex justify-between items-center">
                <span id="preview-file-info" class="text-xs text-slate-500 font-medium"></span>
                <div class="flex gap-3">
                    <a id="preview-download-btn" href="#" download class="px-4 py-2 bg-military-700 text-white rounded-xl text-xs font-bold hover:bg-military-800 flex items-center gap-2"><i class="fa-solid fa-download"></i> Baixar</a>
                    <button onclick="closePreviewModal()" class="px-4 py-2 border border-slate-300 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-100">Fechar</button>
                </div>
            </div>
        </div>
    </div>

    <!-- MODAL CUSTOMIZADO -->
    <div id="custom-modal" class="fixed inset-0 bg-slate-900/70 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 text-center space-y-4 border border-slate-200">
            <div id="custom-modal-icon" class="w-14 h-14 rounded-full flex items-center justify-center mx-auto text-xl"></div>
            <div>
                <h3 id="custom-modal-title" class="font-bold text-lg text-slate-900"></h3>
                <p id="custom-modal-message" class="text-sm text-slate-600 mt-1"></p>
            </div>
            <button onclick="closeCustomModal()" class="w-full py-2.5 bg-military-700 text-white font-bold rounded-xl hover:bg-military-800 text-sm shadow-sm">Entendido</button>
        </div>
    </div>

    <script>
        const omList = ['1º GAAAe', '2º GAAAe', '3º GAAAe', '4º GAAAe', '5º GAAAe Sl', '11º GAAAe', '12º GAAAe', 'B Mnt Sup AAAe', 'Bia C/Cmdo DAAe Ex', 'Cia Com DAAe'];
        const omPasswords = {
            '1º GAAAe': '1G', '2º GAAAe': '2G', '3º GAAAe': '3G', '4º GAAAe': '4G', '5º GAAAe Sl': '5GS',
            '11º GAAAe': '11G', '12º GAAAe': '12G', 'B Mnt Sup AAAe': 'BMnt', 'Bia C/Cmdo DAAe Ex': 'BiaC', 'Cia Com DAAe': 'Com'
        };

        let serverData = { annotations: {}, files: [], cientes: {} };
        let currentOmTab = 'Cmdo DAAe Ex';
        let currentSubTab = 'calendar';
        let authenticatedOms = JSON.parse(sessionStorage.getItem('siscord_auth_v71') || '{}');
        let pendingOmTab = null;
        let currentSelectedDayKey = null;

        async function fetchServerData() {
            try {
                const res = await fetch('/api/data');
                if (res.ok) {
                    serverData = await res.json();
                    renderAll();
                }
            } catch(e) {
                console.error("Erro ao buscar dados do servidor:", e);
            }
        }

        async function saveServerData() {
            try {
                await fetch('/api/data', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(serverData)
                });
            } catch(e) {
                console.error("Erro ao salvar dados no servidor:", e);
            }
        }

        window.initOmTabs = function() {
            const container = document.getElementById('om-tabs-container');
            if(!container) return;
            container.innerHTML = '';
            
            const cmdoBtn = document.createElement('button');
            cmdoBtn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-xs flex items-center gap-2 " + 
                (currentOmTab === 'Cmdo DAAe Ex' ? 'bg-military-900 text-white ring-2 ring-amber-500' : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-300');
            cmdoBtn.innerHTML = '<i class="fa-solid fa-shield-halved text-amber-500"></i> Cmdo DAAe Ex';
            cmdoBtn.onclick = () => trySwitchOmTab('Cmdo DAAe Ex');
            container.appendChild(cmdoBtn);

            omList.forEach(om => {
                const btn = document.createElement('button');
                const isSelected = currentOmTab === om;
                btn.className = "px-4 py-2 rounded-xl text-xs font-bold transition-all shadow-xs flex items-center gap-2 " + 
                    (isSelected ? 'bg-military-700 text-white ring-2 ring-military-600' : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-300');
                btn.innerHTML = '<i class="fa-solid fa-building-shield"></i> ' + om;
                btn.onclick = () => trySwitchOmTab(om);
                container.appendChild(btn);
            });
        }

        window.initOmCheckboxes = function() {
            ['checkbox-om-list', 'annotation-checkbox-list'].forEach(id => {
                const el = document.getElementById(id);
                if (!el) return;
                el.innerHTML = '';
                const nameAttr = id.includes('annotation') ? 'annot-target-om' : 'target-om';
                omList.forEach(om => {
                    const label = document.createElement('label');
                    label.className = "flex items-center gap-2 text-xs font-semibold text-slate-700 bg-white p-2 rounded-lg border border-slate-200 cursor-pointer hover:bg-slate-50";
                    label.innerHTML = `<input type="checkbox" name="${nameAttr}" value="${om}" class="rounded text-military-700 focus:ring-military-600"> <span class="truncate">${om}</span>`;
                    el.appendChild(label);
                });
            });
        }

        window.selectAllOm = (status) => document.querySelectorAll('input[name="target-om"]').forEach(cb => cb.checked = status);
        window.selectAnnotationOm = (status) => document.querySelectorAll('input[name="annot-target-om"]').forEach(cb => cb.checked = status);

        const monthInputEl = document.getElementById('select-month');
        const now = new Date();
        if (monthInputEl && !monthInputEl.value) {
            monthInputEl.value = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0');
        }

        window.trySwitchOmTab = (omName) => {
            if (authenticatedOms[omName]) {
                switchOmTab(omName);
            } else {
                pendingOmTab = omName;
                openAuthModal(omName);
            }
        }

        window.switchOmTab = (omName) => {
            currentOmTab = omName;
            initOmTabs();
            document.getElementById('current-om-indicator').innerHTML = `<i class="fa-solid fa-building-shield text-amber-700"></i> Visualizando: ${omName}`;
            updatePermissionsUI();
            renderAll();
        }

        window.switchSubTab = (subName) => {
            currentSubTab = subName;
            const calSection = document.getElementById('section-calendar');
            const filesSection = document.getElementById('section-files');
            const btnCal = document.getElementById('btn-sub-calendar');
            const btnFiles = document.getElementById('btn-sub-files');

            if (subName === 'calendar') {
                calSection.classList.remove('hidden');
                filesSection.classList.add('hidden');
                btnCal.className = "flex-1 sm:flex-none px-4 py-2 bg-military-700 text-white rounded-xl text-xs font-bold shadow-sm flex items-center justify-center gap-2 transition-all";
                btnFiles.className = "flex-1 sm:flex-none px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-100 flex items-center justify-center gap-2 transition-all shadow-xs";
            } else {
                calSection.classList.add('hidden');
                filesSection.classList.remove('hidden');
                btnFiles.className = "flex-1 sm:flex-none px-4 py-2 bg-military-700 text-white rounded-xl text-xs font-bold shadow-sm flex items-center justify-center gap-2 transition-all";
                btnCal.className = "flex-1 sm:flex-none px-4 py-2 bg-white border border-slate-300 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-100 flex items-center justify-center gap-2 transition-all shadow-xs";
            }
            renderFileList();
        }

        function updatePermissionsUI() {
            const indicator = document.getElementById('auth-status-indicator');
            const title = document.getElementById('auth-status-title');
            const desc = document.getElementById('auth-status-desc');
            const cmdoTargetBox = document.getElementById('cmdo-target-selection');
            const uploadTitle = document.getElementById('upload-section-title');
            const clearHistoryBtn = document.getElementById('btn-clear-history');
            const annotTargetsBox = document.getElementById('annotation-targets-box');
            const isAuth = authenticatedOms[currentOmTab];

            if (currentOmTab === 'Cmdo DAAe Ex') {
                if (isAuth) {
                    indicator.className = "w-3.5 h-3.5 bg-emerald-500 rounded-full animate-pulse shadow-sm";
                    title.textContent = "Cmdo DAAe Ex (Autenticado)";
                    desc.textContent = "Privilégios administrativos ativos";
                    if(cmdoTargetBox) cmdoTargetBox.classList.remove('hidden');
                    if(clearHistoryBtn) clearHistoryBtn.classList.remove('hidden');
                    if(annotTargetsBox) annotTargetsBox.classList.remove('hidden');
                    if(uploadTitle) uploadTitle.innerHTML = '<i class="fa-solid fa-cloud-arrow-up text-military-700"></i> Envio de Documentos / Diretrizes';
                } else {
                    indicator.className = "w-3.5 h-3.5 bg-amber-500 rounded-full shadow-sm";
                    title.textContent = "Cmdo DAAe Ex (Bloqueado)";
                    desc.textContent = "Insira a senha de comando";
                    if(cmdoTargetBox) cmdoTargetBox.classList.add('hidden');
                    if(clearHistoryBtn) clearHistoryBtn.classList.add('hidden');
                    if(annotTargetsBox) annotTargetsBox.classList.add('hidden');
                }
            } else {
                if (isAuth) {
                    indicator.className = "w-3.5 h-3.5 bg-emerald-500 rounded-full shadow-sm";
                    title.textContent = `Perfil: ${currentOmTab} (Autenticado)`;
                    desc.textContent = "Acesso liberado à unidade";
                    if(cmdoTargetBox) cmdoTargetBox.classList.add('hidden');
                    if(clearHistoryBtn) clearHistoryBtn.classList.add('hidden');
                    if(annotTargetsBox) annotTargetsBox.classList.add('hidden');
                } else {
                    indicator.className = "w-3.5 h-3.5 bg-amber-500 rounded-full shadow-sm";
                    title.textContent = `Perfil: ${currentOmTab} (Bloqueado)`;
                    desc.textContent = "Insira a senha da OM";
                }
            }
        }

        window.openAuthModal = (omName) => {
            pendingOmTab = omName || currentOmTab;
            document.getElementById('modal-auth-title').textContent = 'Acesso Restrito: ' + pendingOmTab;
            document.getElementById('auth-password-input').value = '';
            document.getElementById('modal-auth').classList.remove('hidden');
            setTimeout(() => document.getElementById('auth-password-input').focus(), 100);
        }

        window.closeAuthModal = () => {
            document.getElementById('modal-auth').classList.add('hidden');
            pendingOmTab = null;
        }

        window.verifyCommandPassword = () => {
            const pwd = document.getElementById('auth-password-input').value;
            const targetOm = pendingOmTab || currentOmTab;
            const expectedPwd = targetOm === 'Cmdo DAAe Ex' ? 'ARTILHARIA' : omPasswords[targetOm];

            if (pwd === expectedPwd || (targetOm === 'Cmdo DAAe Ex' && pwd === 'BiaC')) {
                authenticatedOms[targetOm] = true;
                sessionStorage.setItem('siscord_auth_v71', JSON.stringify(authenticatedOms));
                closeAuthModal();
                switchOmTab(targetOm);
                showCustomModal('Acesso Concedido', `Aba de ${targetOm} desbloqueada!`, 'success');
            } else {
                showCustomModal('Senha Incorreta', 'Senha inválida para esta unidade.', 'warning');
            }
        }

        function renderAll() {
            renderCalendar();
            renderFileList();
            checkUrgentDeadlines();
        }

        function checkUrgentDeadlines() {
            const banner = document.getElementById('urgent-alert-banner');
            const alertText = document.getElementById('urgent-alert-text');
            const cmdoPanel = document.getElementById('cmdo-cientes-panel');
            const cmdoCientesList = document.getElementById('cmdo-cientes-list');

            if (!banner) return;

            const todayDate = new Date();
            const todayStr = todayDate.getFullYear() + '-' + String(todayDate.getMonth() + 1).padStart(2, '0') + '-' + String(todayDate.getDate()).padStart(2, '0');

            if (currentOmTab === 'Cmdo DAAe Ex') {
                banner.classList.add('hidden');
                if (cmdoPanel) cmdoPanel.classList.remove('hidden');
                if (cmdoCientesList) {
                    cmdoCientesList.innerHTML = '';
                    let total = 0;
                    for (let fileId in serverData.cientes) {
                        let record = serverData.cientes[fileId];
                        let fileName = 'Documento / Anotação';
                        
                        let fileObj = (serverData.files || []).find(f => f.id === fileId);
                        if (fileObj) {
                            fileName = fileObj.name;
                        } else if (fileId.startsWith('ann_')) {
                            let dayKeyAnn = fileId.replace('ann_', '');
                            if (serverData.annotations && serverData.annotations[dayKeyAnn]) {
                                let annText = serverData.annotations[dayKeyAnn].text || '';
                                if (annText.length > 50) annText = annText.substring(0, 47) + '...';
                                fileName = `Anotação (${dayKeyKeyFormat(dayKeyAnn)}): "${annText}"`;
                            } else {
                                fileName = 'Anotação do Calendário';
                            }
                        } else if (fileId.startsWith('gen_')) {
                            fileName = 'Aviso Geral / Prazo do Dia';
                        }

                        record.forEach(c => {
                            total++;
                            let div = document.createElement('div');
                            div.className = "flex items-center justify-between text-xs bg-emerald-50 border border-emerald-200 p-3 rounded-xl shadow-xs gap-3";
                            div.innerHTML = `<div><span class="font-extrabold text-military-900">${c.om}</span> confirmou o ciente em <span class="font-bold text-slate-800">"${fileName}"</span></div><span class="text-slate-500 font-semibold whitespace-nowrap">${c.dateTime}</span>`;
                            cmdoCientesList.appendChild(div);
                        });
                    }
                    if (total === 0) cmdoCientesList.innerHTML = '<p class="text-xs text-slate-400 italic py-2">Nenhum ciente registrado pelas OMDS até o momento.</p>';
                }
                return;
            } else {
                if (cmdoPanel) cmdoPanel.classList.add('hidden');
            }

            let urgentItems = [];

            (serverData.files || []).forEach(f => {
                if (f.dueDate && f.dueDate === todayStr && f.targets && f.targets.includes(currentOmTab)) {
                    let alreadyAcknowledged = serverData.cientes && serverData.cientes[f.id] && serverData.cientes[f.id].some(c => c.om === currentOmTab);
                    if (!alreadyAcknowledged) {
                        urgentItems.push(f.name);
                    }
                }
            });

            if (serverData.annotations && serverData.annotations[todayStr]) {
                let ann = serverData.annotations[todayStr];
                if (ann.targets && ann.targets.includes(currentOmTab) && ann.text.trim().length > 0) {
                    urgentItems.push(`Anotação: "${ann.text}"`);
                }
            }

            if (urgentItems.length > 0) {
                let textDesc = urgentItems.join(' | ');
                alertText.innerHTML = `Prazos e Avisos para hoje (${todayStr.split('-').reverse().join('/')}): <strong class="underline">${textDesc}</strong>. Confirme o recebimento.`;
                banner.classList.remove('hidden');
            } else {
                banner.classList.add('hidden');
            }
        }

        function dayKeyKeyFormat(dk) {
            let parts = dk.split('-');
            if(parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
            return dk;
        }

        window.acknowledgeUrgentDeadline = async () => {
            const todayDate = new Date();
            const todayStr = todayDate.getFullYear() + '-' + String(todayDate.getMonth() + 1).padStart(2, '0') + '-' + String(todayDate.getDate()).padStart(2, '0');
            
            let targetFiles = (serverData.files || []).filter(f => f.targets && f.targets.includes(currentOmTab));
            let hasTodayAnnotation = serverData.annotations && serverData.annotations[todayStr] && serverData.annotations[todayStr].targets && serverData.annotations[todayStr].targets.includes(currentOmTab);

            if (!serverData.cientes) serverData.cientes = {};

            let recordedIds = [];

            targetFiles.forEach(f => {
                if (f.dueDate === todayStr) {
                    recordedIds.push(f.id);
                }
            });

            if (hasTodayAnnotation) {
                recordedIds.push('ann_' + todayStr);
            }

            if (recordedIds.length === 0) {
                recordedIds.push('gen_' + todayStr + '_' + currentOmTab);
            }

            recordedIds.forEach(idKey => {
                if (!serverData.cientes[idKey]) serverData.cientes[idKey] = [];
                if (!serverData.cientes[idKey].some(c => c.om === currentOmTab)) {
                    serverData.cientes[idKey].push({ om: currentOmTab, dateTime: new Date().toLocaleString('pt-BR') });
                }
            });

            await saveServerData();
            document.getElementById('urgent-alert-banner').classList.add('hidden');
            showCustomModal('Registrado', 'Confirmação de ciente enviada ao Comando com sucesso!', 'success');
        }

        window.clearCmdoCientes = async () => {
            if (!confirm('Deseja realmente limpar todo o histórico de cientes das OMDS?')) return;
            serverData.cientes = {};
            await saveServerData();
            renderAll();
            showCustomModal('Histórico Limpo', 'O registro de cientes foi esvaziado com sucesso.', 'info');
        }

        function renderCalendar() {
            const monthInput = document.getElementById('select-month').value;
            const [year, month] = monthInput.split('-');
            const gridContainer = document.getElementById('calendar-grid');
            if(!gridContainer) return;
            gridContainer.innerHTML = '';
            const totalDays = new Date(year, month, 0).getDate();

            for (let day = 1; day <= 31; day++) {
                const dayStr = day < 10 ? '0' + day : '' + day;
                const dayKey = `${year}-${month}-${dayStr}`;
                const isOutOfBounds = day > totalDays;
                const annObj = serverData.annotations[dayKey];

                let visibleAnnotation = '';
                if (annObj) {
                    if (currentOmTab === 'Cmdo DAAe Ex') visibleAnnotation = annObj.text || '';
                    else if (annObj.targets && annObj.targets.includes(currentOmTab)) visibleAnnotation = annObj.text || '';
                }

                const hasAnnotation = visibleAnnotation.trim().length > 0;
                const card = document.createElement('div');

                if (isOutOfBounds) {
                    card.className = "bg-slate-50 border border-slate-200 rounded-xl p-4 opacity-40 flex flex-col justify-between h-36 select-none";
                    card.innerHTML = `<div class="flex justify-between items-center"><span class="text-base font-bold text-slate-400">${dayStr}</span></div>`;
                } else {
                    const canEdit = (currentOmTab === 'Cmdo DAAe Ex' && authenticatedOms['Cmdo DAAe Ex']);
                    card.className = `bg-white border rounded-xl p-4 flex flex-col justify-between h-36 transition-all shadow-xs ${canEdit ? 'cursor-pointer hover:shadow-md hover:border-military-600 hover:bg-military-50/20' : ''} ${hasAnnotation ? 'border-military-600 bg-military-50/40 ring-1 ring-military-600/30' : 'border-slate-200'}`;
                    
                    if (canEdit) {
                        card.onclick = () => openAnnotationModal(dayKey, dayStr, month, year);
                    }

                    let previewText = hasAnnotation ? visibleAnnotation : 'Nenhuma anotação...';
                    if (previewText.length > 75) previewText = previewText.substring(0, 72) + '...';

                    card.innerHTML = `<div class="flex justify-between items-center"><span class="text-base font-bold text-slate-900">${dayStr}</span>${hasAnnotation ? '<span class="bg-military-700 text-white text-[10px] px-2 py-0.5 rounded-full font-bold">Ativo</span>' : ''}</div><div class="text-xs text-slate-700 line-clamp-3 mt-2">${previewText}</div>`;
                }
                gridContainer.appendChild(card);
            }
        }

        window.openAnnotationModal = (dayKey, day, month, year) => {
            currentSelectedDayKey = dayKey;
            document.getElementById('modal-title').textContent = `Anotação do Dia ${day}/${month}/${year}`;
            const existing = serverData.annotations[dayKey] || { text: '', targets: [] };
            document.getElementById('annotation-text').value = existing.text || '';
            document.querySelectorAll('input[name="annot-target-om"]').forEach(cb => {
                cb.checked = existing.targets && existing.targets.includes(cb.value);
            });
            document.getElementById('modal-annotation').classList.remove('hidden');
        }

        window.closeAnnotationModal = () => document.getElementById('modal-annotation').classList.add('hidden');

        window.saveAnnotation = async () => {
            const textValue = document.getElementById('annotation-text').value;
            const selectedTargets = [];
            document.querySelectorAll('input[name="annot-target-om"]:checked').forEach(cb => selectedTargets.push(cb.value));

            if(!serverData.annotations) serverData.annotations = {};
            serverData.annotations[currentSelectedDayKey] = { text: textValue, targets: selectedTargets };

            await saveServerData();
            closeAnnotationModal();
            renderCalendar();
            showCustomModal('Sucesso', 'Anotação salva no servidor com sucesso!', 'success');
        }

        window.handleFileUpload = async (event) => {
            const files = event.target.files;
            if (!files.length) return;
            const dueDateVal = document.getElementById('file-due-date').value;
            const targets = [];
            if (currentOmTab === 'Cmdo DAAe Ex') {
                document.querySelectorAll('input[name="target-om"]:checked').forEach(cb => targets.push(cb.value));
                if (!targets.length) { showCustomModal('Atenção', 'Selecione ao menos uma OMDS.', 'warning'); return; }
            } else {
                targets.push('Cmdo DAAe Ex');
            }

            if(!serverData.files) serverData.files = [];

            for (let file of files) {
                const reader = new FileReader();
                reader.onload = async function(e) {
                    serverData.files.unshift({
                        id: 'file_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
                        name: file.name,
                        type: file.type || 'application/octet-stream',
                        size: (file.size / 1024).toFixed(1) + ' KB',
                        date: new Date().toLocaleString('pt-BR'),
                        dueDate: dueDateVal || null,
                        sender: currentOmTab,
                        targets: targets,
                        dataUrl: e.target.result
                    });
                    await saveServerData();
                    renderFileList();
                    event.target.value = '';
                    showCustomModal('Upload', 'Arquivo enviado com sucesso!', 'success');
                };
                reader.readAsDataURL(file);
            }
        }

        function renderFileList() {
            const tbody = document.getElementById('file-table-body');
            const noFilesMsg = document.getElementById('no-files-msg');
            const badgeCount = document.getElementById('badge-active-files');
            if(!tbody) return;
            tbody.innerHTML = '';

            const filtered = (serverData.files || []).filter(f => {
                if (currentOmTab === 'Cmdo DAAe Ex') return f.sender === 'Cmdo DAAe Ex' || (f.targets && f.targets.includes('Cmdo DAAe Ex'));
                return (f.targets && f.targets.includes(currentOmTab)) || f.sender === currentOmTab;
            });

            badgeCount.textContent = filtered.length;
            if (!filtered.length) { noFilesMsg.classList.remove('hidden'); return; }
            noFilesMsg.classList.add('hidden');

            filtered.forEach(file => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 border-b border-slate-100 text-sm";
                const isCmdoAuth = (currentOmTab === 'Cmdo DAAe Ex' && authenticatedOms['Cmdo DAAe Ex']);

                tr.innerHTML = `
                    <td class="py-3.5 px-4 font-semibold text-slate-800 flex items-center gap-3"><i class="fa-solid fa-file text-xl text-military-700"></i><span class="truncate max-w-xs">${file.name}</span></td>
                    <td class="py-3.5 px-4 text-xs font-bold text-slate-700">${file.sender}</td>
                    <td class="py-3.5 px-4"><span class="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-bold">${file.sender === 'Cmdo DAAe Ex' ? 'Enviado' : 'Sinal Verde'}</span></td>
                    <td class="py-3.5 px-4 text-xs text-slate-500">${file.date}</td>
                    <td class="py-3.5 px-4 text-right space-x-1.5">
                        <button onclick="previewFile('${file.id}')" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 rounded-xl text-xs font-bold"><i class="fa-solid fa-eye"></i></button>
                        <a href="${file.dataUrl}" download="${file.name}" class="px-3 py-1.5 bg-military-50 hover:bg-military-100 text-military-700 rounded-xl text-xs font-bold inline-block"><i class="fa-solid fa-download"></i></a>
                        ${isCmdoAuth ? `<button onclick="deleteFile('${file.id}')" class="px-3 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl text-xs font-bold"><i class="fa-solid fa-trash-can"></i></button>` : ''}
                    </td>`;
                tbody.appendChild(tr);
            });
        }

        window.previewFile = (id) => {
            const file = serverData.files.find(f => f.id === id);
            if (!file) return;
            document.getElementById('preview-modal-title').textContent = file.name;
            document.getElementById('preview-file-info').textContent = `Remetente: ${file.sender} | Data: ${file.date}`;
            document.getElementById('preview-download-btn').href = file.dataUrl;
            document.getElementById('preview-download-btn').setAttribute('download', file.name);
            const container = document.getElementById('preview-content-container');
            container.innerHTML = file.type.includes('image') ? `<img src="${file.dataUrl}" class="max-h-[60vh] object-contain">` : `<div class="text-center py-12"><p class="font-bold text-slate-800">Baixe o arquivo para visualizá-lo.</p></div>`;
            document.getElementById('modal-preview').classList.remove('hidden');
        }

        window.closePreviewModal = () => document.getElementById('modal-preview').classList.add('hidden');

        window.deleteFile = async (id) => {
            serverData.files = serverData.files.filter(f => f.id !== id);
            await saveServerData();
            renderFileList();
            showCustomModal('Excluído', 'Arquivo removido com sucesso.', 'info');
        }

        window.clearAllFiles = async () => {
            serverData.files = [];
            await saveServerData();
            renderFileList();
            showCustomModal('Repositório Limpo', 'Todos os arquivos foram removidos.', 'info');
        }

        window.showCustomModal = (title, msg, type) => {
            document.getElementById('custom-modal-title').textContent = title;
            document.getElementById('custom-modal-message').textContent = msg;
            document.getElementById('custom-modal').classList.remove('hidden');
        }
        window.closeCustomModal = () => document.getElementById('custom-modal').classList.add('hidden');

        window.onload = async () => {
            initOmTabs();
            initOmCheckboxes();
            updatePermissionsUI();
            await fetchServerData();
            setInterval(fetchServerData, 10000); // Sincroniza a cada 10 segundos automaticamente
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
