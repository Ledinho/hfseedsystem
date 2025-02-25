from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime
from functools import wraps
from flask import Response
import pandas as pd
from io import BytesIO


app = Flask(__name__)
app.secret_key = "chave-secreta"  # Para mensagens flash

# Inicializa o banco de dados
def init_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Tabela de fluxo_fnfe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fluxo_fnfe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            destino TEXT,
            consultor TEXT,
            transportador TEXT,
            user TEXT,
            notas TEXT,
            obs TEXT
        )
    ''')

    # Tabela de devolutiva_dnfe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devolutiva_dnfe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            data TEXT,
            consultor TEXT,
            entregue TEXT,
            notas TEXT,
            obs TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Decorador para impedir cache
def nocache(view):
    @wraps(view)
    def no_cache_decorator(*args, **kwargs):
        response = view(*args, **kwargs)
        
        if isinstance(response, Response):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    return no_cache_decorator

# Decorador para verificar se o usuário está autenticado
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_email' not in session:
            flash("Faça login para acessar essa página.", "warning")
            return redirect(url_for('index'))
        return view(*args, **kwargs)
    return wrapped_view

# Página de login
@app.route('/', endpoint='index')
def index():
    return render_template('login.html')


# Rota para processar o login
@app.route('/login', methods=['POST'])
def login():
    # Capturar os dados do formulário
    email = request.form.get('email')
    senha = request.form.get('senha')

    # Verificar no banco de dados
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        # Armazenar o e-mail na sessão
        session['user_email'] = email
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Credenciais inválidas. Tente novamente.', 'danger')
        return redirect(url_for('index'))


# Página FNFE (para inserir dados)
@app.route('/fnfe', methods=['GET', 'POST'])
@nocache
@login_required
def fnfe():
    if request.method == 'POST':
        try:
            usuario = session.get('user_email')
            if not usuario:
                flash("Usuário não autenticado. Faça login.", "danger")
                return redirect(url_for('index'))

            # Recuperar dados do formulário
            data = request.form.get('data')
            destino = request.form.get('destino')
            consultor = request.form.get('consultor')
            transportador = request.form.get('transportador')
            obs = request.form.get('obs')
            notas_concatenadas = request.form.get('notas_concatenadas')

            if not all([data, destino, consultor, transportador, notas_concatenadas]):
                flash("Preencha todos os campos obrigatórios!", "danger")
                return redirect(url_for('fnfe'))

            # Salvar no banco de dados
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fluxo_fnfe (data, destino, consultor, transportador, user, notas, obs)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (data, destino, consultor, transportador, usuario, notas_concatenadas, obs))
            conn.commit()

            # Recuperar o ID do registro recém-inserido
            numero_formulario = cursor.lastrowid
            conn.close()

            # Redirecionar para a página de confirmação com o número do formulário
            flash(f"Dados inseridos com sucesso! Número do formulário: {numero_formulario}", "success")
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Erro ao salvar os dados no banco: {e}")
            flash("Erro ao salvar os dados. Tente novamente.", "danger")
            return redirect(url_for('fnfe'))

    
    # Buscar o próximo ID do formulário
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(id) + 1 AS next_id FROM fluxo_fnfe")
    
    result = cursor.fetchone()
    next_id = result[0] if result and result[0] else 1
    conn.close()
    
    return render_template('fnfe.html', numero=next_id)
    

# Página inicial
@app.route('/home')
@nocache
@login_required
def home():
    return render_template('home.html')

# Página fluxo
@app.route('/fluxo')
@nocache
@login_required
def fluxo():
    return render_template('fluxo.html')

# Página de Devolutivas
@app.route('/dnfe', methods=['GET', 'POST'])
@nocache
@login_required
def dnfe():
    if request.method == 'POST':
        try:
            usuario = session.get('user_email')
            if not usuario:
                flash("Usuário não autenticado. Faça login.", "danger")
                return redirect(url_for('index'))

            # Recuperar dados do formulário
            data = request.form.get('data')
            consultor = request.form.get('consultor')
            entregue = request.form.get('entregue')
            notas_concatenadas = request.form.get('notas_concatenadas')  # Recebe as notas agrupadas
            obs = request.form.get('obs')

            if not all([data, consultor, entregue, notas_concatenadas]):
                flash("Preencha todos os campos obrigatórios!", "danger")
                return redirect(url_for('dnfe'))

            # Salvar no banco de dados
            conn = sqlite3.connect('usuarios.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO devolutiva_dnfe (user, data, consultor, entregue, notas, obs)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (usuario, data, consultor, entregue, notas_concatenadas, obs))
            conn.commit()

            numero_formulario = cursor.lastrowid
            conn.close()

            flash(f"Dados inseridos com sucesso! Número do formulário: {numero_formulario}", "success")
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Erro ao salvar os dados no banco: {e}")
            flash("Erro ao salvar os dados. Tente novamente.", "danger")
            return redirect(url_for('dnfe'))


    # Caso seja um método GET, retorne a página com o formulário
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) + 1 AS next_id FROM devolutiva_dnfe")
    result = cursor.fetchone()
    next_id = result[0] if result and result[0] else 1
    conn.close()
    

    return render_template('dnfe.html', numero=next_id)  # Certifique-se de que sempre retorna algo


# Rota de logout
@app.route('/logout')
def logout():
    session.clear()  # Limpa a sessão
    flash('Você foi desconectado com sucesso!', 'info')
    return redirect(url_for('index'))



@app.route('/dashboard', methods=['GET', 'POST'])
@nocache
@login_required
def dashboard():
    pesquisa = request.args.get('pesquisa', '').strip()  

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    if pesquisa == '':
        cursor.execute("SELECT id, data, consultor, destino, transportador, user FROM fluxo_fnfe ORDER BY data DESC LIMIT 5")
    else:
        cursor.execute("""
            SELECT id, data, consultor, destino, transportador, user 
            FROM fluxo_fnfe 
            WHERE id = ? OR notas LIKE ? OR transportador LIKE ? OR consultor LIKE ? 
            LIMIT 5
        """, (pesquisa, f"%{pesquisa}%", f"%{pesquisa}%", f"%{pesquisa}%"))
    
    registros = cursor.fetchall()
    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/tabela.html', registros=registros)  
    
    return render_template('dashboard.html', registros=registros, pesquisa=pesquisa)


@app.route('/detalhes/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_detalhes(id):
    # Conectar ao banco de dados
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Consultar os dados do registro com o ID fornecido
    cursor.execute("SELECT * FROM fluxo_fnfe WHERE id = ?", (id,))
    registro = cursor.fetchone()
    conn.close()

    if registro:
        # Renderiza a página de detalhes com as informações do registro
        return render_template('detalhes.html', registro=registro)
    else:
        flash('Registro não encontrado.', 'danger')
        return redirect(url_for('dashboard'))
    
def get_db_connection():
    conn = sqlite3.connect('usuarios.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/editar_fnfe/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_fnfe(id):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Buscar o registro no banco de dados
        cursor.execute("SELECT * FROM fluxo_fnfe WHERE id = ?", (id,))
        registro = cursor.fetchone()

        # Carregar as notas fiscais existentes
        notas_fiscais = registro['notas'].split(',') if registro['notas'] else []

        if request.method == 'POST':
            data = request.form['data']
            destino = request.form['destino']
            consultor = request.form['consultor']
            transportador = request.form['transportador']
            notas = request.form.getlist('nota')
            obs = request.form['obs']

            # Concatenar notas fiscais para armazenar em um único campo
            notas_concatenadas = ",".join(notas)

            # Atualizar o registro no banco de dados
            cursor.execute("""
                UPDATE fluxo_fnfe
                SET data = ?, destino = ?, consultor = ?, transportador = ?, notas = ?, obs = ?
                WHERE id = ?
            """, (data, destino, consultor, transportador, notas_concatenadas, obs, id))

            conn.commit()  # Commit da transação

            return redirect(url_for('dashboard'))

        # Caso seja um GET, dividir as notas para enviar ao template
        notas_list = registro['notas'].split(' - ') if registro['notas'] else []

    return render_template('editar_fnfe.html', registro=registro, notas_fiscais=notas_fiscais, notas_list=notas_list)

# Função para obter as notas não entregues
def get_pending_notes():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    # Ajustando a consulta para dividir e comparar notas individualmente
    query = """
    WITH fluxo_notas AS (
        SELECT id, data, consultor, transportador, value AS nota
        FROM fluxo_fnfe, json_each(replace(notas, ' - ', '","'))
    ),
    devolutiva_notas AS (
        SELECT value AS nota
        FROM devolutiva_dnfe, json_each(replace(notas, ' - ', '","'))
    )
    SELECT DISTINCT f.id, f.data, f.consultor, f.nota, f.transportador
    FROM fluxo_notas f
    LEFT JOIN devolutiva_notas d
    ON f.nota = d.nota
    WHERE d.nota IS NULL;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results

# Filtro para formatar a data
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    if isinstance(value, datetime):
        return value.strftime(format)
    return value

@app.route('/relatorio')
def relatorio():
    # Recebe os filtros de data e consultor
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    consultor = request.args.get('consultor', '')

    # Prepara a consulta SQL com os filtros
    query = """
    WITH fluxo_notas AS (
        SELECT f.id, f.data, f.consultor, f.transportador, value AS nota
        FROM fluxo_fnfe f, json_each('["' || replace(f.notas, ' - ', '","') || '"]')
    ),
    devolutiva_notas AS (
        SELECT value AS nota
        FROM devolutiva_dnfe d, json_each('["' || replace(d.notas, ' - ', '","') || '"]')
    )
    SELECT DISTINCT f.id, f.data, f.consultor, f.nota, f.transportador
    FROM fluxo_notas f
    LEFT JOIN devolutiva_notas d
    ON f.nota = d.nota
    WHERE d.nota IS NULL
    """

    # Aplica filtros se existirem
    if data_inicio:
        query += " AND f.data >= ?"
    if data_fim:
        query += " AND f.data <= ?"
    if consultor:
        query += " AND f.consultor LIKE ?"

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    params = []
    if data_inicio:
        params.append(data_inicio)
    if data_fim:
        params.append(data_fim)
    if consultor:
        params.append(f'%{consultor}%')

    cursor.execute(query, params)
    pending_notes = cursor.fetchall()

    conn.close()

   # Convertendo a data dos resultados para o formato datetime
    for i in range(len(pending_notes)):
        pending_notes[i] = list(pending_notes[i])  # Convertendo tupla para lista
        # Convertendo string para datetime com hora, se necessário
        try:
            pending_notes[i][1] = datetime.strptime(pending_notes[i][1], '%Y-%m-%dT%H:%M')  # Formato com hora
        except ValueError:
            pending_notes[i][1] = datetime.strptime(pending_notes[i][1], '%Y-%m-%d')  # Caso a data não tenha hora

    return render_template('relatorio.html', pending_notes=pending_notes, data_inicio=data_inicio, data_fim=data_fim, consultor=consultor)



@app.route('/exportar_excel')
def exportar_excel():
    # Recebe os filtros de data e consultor
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    consultor = request.args.get('consultor', '')

    # Prepara a consulta SQL com os filtros
    query = """
    WITH fluxo_notas AS (
        SELECT f.id, f.data, f.consultor, f.transportador, value AS nota
        FROM fluxo_fnfe f, json_each('["' || replace(f.notas, ' - ', '","') || '"]')
    ),
    devolutiva_notas AS (
        SELECT value AS nota
        FROM devolutiva_dnfe d, json_each('["' || replace(d.notas, ' - ', '","') || '"]')
    )
    SELECT DISTINCT f.id, f.data, f.consultor, f.nota, f.transportador
    FROM fluxo_notas f
    LEFT JOIN devolutiva_notas d
    ON f.nota = d.nota
    WHERE d.nota IS NULL
    """

    # Aplica filtros se existirem
    if data_inicio:
        query += " AND f.data >= ?"
    if data_fim:
        query += " AND f.data <= ?"
    if consultor:
        query += " AND f.consultor LIKE ?"

    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    params = []
    if data_inicio:
        params.append(data_inicio)
    if data_fim:
        params.append(data_fim)
    if consultor:
        params.append(f'%{consultor}%')

    cursor.execute(query, params)
    rows = cursor.fetchall()

    conn.close()

    # Converte os dados para um DataFrame do Pandas
    df = pd.DataFrame(rows, columns=['ID', 'Data', 'Consultor', 'Nota', 'Transportador'])

    # Cria um arquivo Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatório')

    output.seek(0)

    # Retorna o arquivo como resposta
    return Response(output, 
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": "attachment;filename=relatorio_notas_nao_entregues.xlsx"})

# Função para obter as notas entregues
def get_delivered_notes():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    query = """
    WITH fluxo_notas AS (
        SELECT id, data, consultor, transportador, value AS nota
        FROM fluxo_fnfe, json_each(replace(notas, ' - ', '","'))
    ),
    devolutiva_notas AS (
        SELECT value AS nota
        FROM devolutiva_dnfe, json_each(replace(notas, ' - ', '","'))
    )
    SELECT DISTINCT f.id, f.data, f.consultor, f.nota, f.transportador
    FROM fluxo_notas f
    JOIN devolutiva_notas d
    ON f.nota = d.nota;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results


# Função para obter as notas entregues
def get_delivered_notes():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()

    query = """
    WITH fluxo_notas AS (
        SELECT id, data, consultor, transportador, value AS nota
        FROM fluxo_fnfe, json_each(replace(notas, ' - ', '","'))
    ),
    devolutiva_notas AS (
        SELECT value AS nota
        FROM devolutiva_dnfe, json_each(replace(notas, ' - ', '","'))
    )
    SELECT DISTINCT f.id, f.data, f.consultor, f.nota, f.transportador
    FROM fluxo_notas f
    JOIN devolutiva_notas d
    ON f.nota = d.nota;
    """
    cursor.execute(query)
    results = cursor.fetchall()

    conn.close()
    return results


@app.route('/relatorio_entregues', methods=['GET'])
def relatorio_entregues():
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    consultor = request.args.get('consultor', '')

    # Formando a consulta SQL com filtros
    query = """
        SELECT f.id, f.data, f.consultor, f.notas, f.transportador
        FROM fluxo_fnfe f
        LEFT JOIN devolutiva_dnfe d ON f.notas = d.notas
        WHERE d.notas IS NOT NULL
    """

    # Adicionando filtros à consulta
    params = []
    if data_inicio:
        query += " AND f.data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND f.data <= ?"
        params.append(data_fim)
    if consultor:
        query += " AND f.consultor LIKE ?"
        params.append(f'%{consultor}%')

    # Executando a consulta
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    delivered_notes = cursor.fetchall()
    conn.close()

    return render_template('relatorio_entregues.html', 
                           delivered_notes=delivered_notes,
                           data_inicio=data_inicio, 
                           data_fim=data_fim, 
                           consultor=consultor)

@app.route('/exportar_excel_entregues', methods=['GET'])
def exportar_excel_entregues():
    data_inicio = request.args.get('data_inicio', '')
    data_fim = request.args.get('data_fim', '')
    consultor = request.args.get('consultor', '')

    # Formando a consulta SQL com filtros
    query = """
        SELECT f.id, f.data, f.consultor, f.notas, f.transportador
        FROM fluxo_fnfe f
        LEFT JOIN devolutiva_fnfe d ON f.notas = d.notas
        WHERE d.notas IS NOT NULL
    """

    # Adicionando filtros à consulta
    params = []
    if data_inicio:
        query += " AND f.data >= ?"
        params.append(data_inicio)
    if data_fim:
        query += " AND f.data <= ?"
        params.append(data_fim)
    if consultor:
        query += " AND f.consultor LIKE ?"
        params.append(f'%{consultor}%')

    # Executando a consulta
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    delivered_notes = cursor.fetchall()
    conn.close()

    # Criando o DataFrame
    df = pd.DataFrame(delivered_notes, columns=['ID', 'Data', 'Consultor', 'Nota', 'Transportador'])

    # Convertendo para Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Notas Entregues')

    output.seek(0)

    return Response(output, 
                    mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
                    headers={"Content-Disposition": "attachment;filename=relatorio_notas_entregues.xlsx"})


@app.route('/devolutiva', methods=['GET', 'POST'])
@nocache
@login_required
def devolutiva():
    pesquisa = request.args.get('pesquisa', '').strip()  # Pegando a pesquisa da URL
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    
    if pesquisa == '':  # Se não houver pesquisa
        # Pega os 5 últimos registros
        cursor.execute("SELECT id, data, consultor, user, entregue, notas FROM devolutiva_dnfe ORDER BY data DESC LIMIT 5")
    else:
        # Pesquisa por ID, nota, consultor, user ou entregue
        cursor.execute("""
            SELECT id, data, consultor, user, entregue, notas
            FROM devolutiva_dnfe
            WHERE id = ? OR notas LIKE ? OR consultor LIKE ? OR entregue LIKE ?
            LIMIT 5
        """, (pesquisa, f"%{pesquisa}%", f"%{pesquisa}%", f"%{pesquisa}%"))
    
    registros = cursor.fetchall()
    conn.close()

    # Verificar se a requisição é AJAX para atualizar apenas a tabela
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('partials/tabela2.html', devolutiva=registros)  
    
    return render_template('devolutiva.html', devolutiva=registros, pesquisa=pesquisa)


@app.route("/detalhesdnfe/<int:id>")
def detalhesdnfe(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, user, data, consultor, entregue, notas, OBS FROM devolutiva_dnfe WHERE id = ?", (id,))
    devolutiva = cursor.fetchone()
    
    if devolutiva:
        dados = {
            "id": devolutiva[0],
            "user": devolutiva[1],
            "data": devolutiva[2],
            "consultor": devolutiva[3],
            "entregue": devolutiva[4],
            "notas": devolutiva[5],
            "OBS": devolutiva[6],
        }
        return render_template("detalhesdnfe.html", devolutiva=dados)
    else:
        return "Devolutiva não encontrada", 404

if __name__ == '__main__':
    app.run(debug=True)
