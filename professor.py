import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import bcrypt
import webbrowser
import subprocess
import sys
from configDB import conectarDB
import re

#Busca a lista de alunos que tem aula com o professor. Nome do aluno, disciplina matriculada e cpf do aluno.
def buscar_alunos_do_professor(professor_id, cpf_filtro=None):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        
        sql = "SELECT u.nome, d.nome, u.cpf FROM usuarios AS u JOIN matriculas m ON u.id = m.aluno_id JOIN disciplinas AS d ON m.disciplina_id = d.id WHERE d.professor_id = %s"
        params = [professor_id]
        
        #Adiciona o filtro por CPF do aluno
        if cpf_filtro:
            #Evitar SQL injection
            cpf_limpo = re.sub(r'[^0-9]', '', cpf_filtro)
            if len(cpf_limpo) == 11:
                sql += " AND u.cpf = %s"
                params.append(cpf_limpo)
            elif len(cpf_limpo) > 0:
                messagebox.showwarning("Filtro Inválido", "O CPF para filtro deve ter 11 dígitos.")
                
        sql += " ORDER BY d.nome, u.nome"
        
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar os alunos: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca alunos matriculados na disciplina do professor.
def buscar_alunos_da_disciplina(disciplina_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT u.id, u.nome, u.cpf FROM usuarios AS u JOIN matriculas AS m ON u.id = m.aluno_id WHERE m.disciplina_id = %s ORDER BY u.nome"
        cursor.execute(sql, (disciplina_id,))
        return cursor.fetchall()
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar alunos da disciplina: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca dados do professor (nome, cpf, titulação e área de atuação).
def buscar_dados_professor(usuario_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT u.nome, u.cpf, p.titulacao, p.area_atuacao FROM usuarios AS u JOIN professores AS p ON u.id = p.id WHERE u.id = %s"
        cursor.execute(sql, (usuario_id,))
        dados = cursor.fetchone()
        return dados
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar dados do professor: {e}")
        return None
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca as disicplinas em que o professor dá aula. Pega o id e o nome da disciplina.
def buscar_disciplinas_professor(professor_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT id, nome FROM disciplinas WHERE professor_id = %s ORDER BY nome"
        cursor.execute(sql, (professor_id,))
        return cursor.fetchall()
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar suas disciplinas: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca as notas já cadastradas dos alunos na disciplina. Retorna id da matricula, nota do trabalho e prova.
def buscar_dados_para_nota(aluno_id, disciplina_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = " SELECT m.id, n.nota_trabalho, n.nota_prova FROM matriculas AS m LEFT JOIN notas AS n ON m.id = n.matricula_id WHERE m.aluno_id = %s AND m.disciplina_id = %s"
        cursor.execute(sql, (aluno_id, disciplina_id))
        return cursor.fetchone()
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar dados da matrícula: {e}")
        return None
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#O professor pode inserir ou atualizar notas.
def inserir_atualizar_notas(aluno_id, disciplina_id, professor_id, matricula_id, nota_trabalho, nota_prova):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT id FROM notas WHERE matricula_id = %s"
        cursor.execute(sql, (matricula_id,))
        registro_nota = cursor.fetchone()
        if registro_nota:
            sql_update = "UPDATE notas SET nota_trabalho = %s, nota_prova = %s, professor_id = %s WHERE matricula_id = %s"
            cursor.execute(sql_update, (nota_trabalho, nota_prova, professor_id, matricula_id))
        else:
            sql_insert = "INSERT INTO notas (aluno_id, disciplina_id, professor_id, matricula_id, nota_trabalho, nota_prova) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_insert, (aluno_id, disciplina_id, professor_id, matricula_id, nota_trabalho, nota_prova))         
        conexao.commit()
        return True
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível salvar as notas: {e}")
        conexao.rollback()
        return False
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Menu TOPBAR.
#Monsta as informações do usuário
def acao_info_usuario(nome, cpf):
    messagebox.showinfo("Informações do Usuário",
                        f"Nome: {nome}\n"
                        f"CPF: {cpf}")

#Fecha a janela e abre o script de login.py
def acao_sair(janela_atual):
    janela_atual.destroy()
    subprocess.Popen([sys.executable, 'login.py']) #

#redireciona para o navegador web abrir uma página.
def acao_apresentacao():
    webbrowser.open("https://www.youtube.com/watch?v=YYE8ZLlReu4")

def acao_github():
    webbrowser.open("https://github.com/karsyx")

#Usuário consegue trocar a sua senha de acesso.
def abrir_janela_troca_senha_menu(janela_pai, usuario_id, cpf_usuario):
    janela_pai.withdraw()
    trocarSenha_tk = tk.Toplevel(janela_pai)
    trocarSenha_tk.title("Trocar Senha")
    trocarSenha_tk.geometry("300x230")
    janela_pai.eval(f'tk::PlaceWindow {trocarSenha_tk} center')
        
    def salvar_nova_senha():
        nova_senha = entrada_nova_senha.get()
        confirma_senha = entrada_confirma_senha.get()

        #Obrigatório ter os campos preenchidos.
        if not nova_senha or not confirma_senha:
            messagebox.showerror("Erro", "Ambos os campos são obrigatórios.", parent=trocarSenha_tk)
            return
        if nova_senha != confirma_senha:
            messagebox.showerror("Erro", "As senhas não coincidem.", parent=trocarSenha_tk)
            entrada_nova_senha.delete(0, tk.END)
            entrada_confirma_senha.delete(0, tk.END)
            return
        try:
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), salt)
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()
            sql = "UPDATE usuarios SET senha = %s WHERE id = %s"
            cursor.execute(sql, (senha_hash.decode('utf-8'), usuario_id))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!", parent=trocarSenha_tk)
            ao_fechar()
        except pymysql.Error as erro:
            messagebox.showerror("Erro de Banco", f"Não foi possível atualizar a senha: {erro}", parent=trocarSenha_tk)
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close()
                conexao.close()
    
    def fn_mostrar_senha():
        if var_mostrar_senha.get():
            entrada_nova_senha.config(show="")
            entrada_confirma_senha.config(show="")
        else:
            entrada_nova_senha.config(show="*")
            entrada_confirma_senha.config(show="*")

    def ao_fechar():
        trocarSenha_tk.destroy()
        janela_pai.deiconify()

    tk.Label(trocarSenha_tk, text=f"Usuário (CPF): {cpf_usuario}").pack(pady=(10, 10))
    tk.Label(trocarSenha_tk, text="Nova Senha:").pack()
    entrada_nova_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_nova_senha.pack(pady=5)
    tk.Label(trocarSenha_tk, text="Confirmar Nova Senha:").pack()
    entrada_confirma_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_confirma_senha.pack(pady=5)

    var_mostrar_senha = tk.BooleanVar()
    check_mostrar = tk.Checkbutton(trocarSenha_tk, text="Mostrar senha", 
                                  variable=var_mostrar_senha,
                                  command=fn_mostrar_senha)
    check_mostrar.pack(pady=5)
    
    botao_salvar = tk.Button(trocarSenha_tk, text="Confirmar", command=salvar_nova_senha)
    botao_salvar.pack(pady=10)
    trocarSenha_tk.bind("<Return>", lambda e: salvar_nova_senha())
    #Garante que, se o usuário fechar a janela de trocar a senha, a janela do professor reapareça novamente.
    trocarSenha_tk.protocol("WM_DELETE_WINDOW", ao_fechar)

#Tela principal do professor.
def portalProfessor(janelaProfessor, usuario_id):
    
    #Usa a função para buscar os dados do professor.
    dados_professor = buscar_dados_professor(usuario_id)
    #Exibe erro se não achar dados ou se não conectar com o banco.
    if not dados_professor:
        messagebox.showerror("Erro Crítico", "Não foi possível carregar os dados do professor. Encerrando.")
        janelaProfessor.destroy()
        return
        
    nome_prof, cpf_prof, titulacao_prof, area_prof = dados_professor

    janelaProfessor.title(f"Portal do Professor - {nome_prof}")
    janelaProfessor.geometry("600x500")
    janelaProfessor.eval('tk::PlaceWindow . center')

    #Cria o menu no topo da janela.
    menu_topo = tk.Menu(janelaProfessor)
    menu_conta = tk.Menu(menu_topo, tearoff=0)
    menu_conta.add_command(label="Informações do Usuário", 
                           command=lambda: acao_info_usuario(nome_prof, cpf_prof))
    menu_conta.add_command(label="Trocar Senha",
                           command=lambda: abrir_janela_troca_senha_menu(janelaProfessor, usuario_id, cpf_prof))
    menu_conta.add_separator()
    menu_conta.add_command(label="Sair", 
                           command=lambda: acao_sair(janelaProfessor))
    menu_sobre = tk.Menu(menu_topo, tearoff=0)
    menu_sobre.add_command(label="Apresentação", command=acao_apresentacao)
    menu_sobre.add_command(label="Github", command=acao_github)

    #Cria os sub-menu no topo da janela.
    menu_topo.add_cascade(label="Conta", menu=menu_conta)
    menu_topo.add_cascade(label="Sobre", menu=menu_sobre)
    janelaProfessor.config(menu=menu_topo)

    #Cria um frame onde mostra o nome, titulação e área de atuação do professor.
    frame_header = tk.Frame(janelaProfessor, pady=10)
    frame_header.pack(fill='x')
    tk.Label(frame_header, text=f"Professor: {nome_prof}", font=("Arial", 12, "bold")).pack()
    tk.Label(frame_header, text=f"Titulação: {titulacao_prof} | Área: {area_prof}", font=("Arial", 10)).pack()
    
    #Cria duas abas para ver alunos e aplicar notas dos alunos.
    notebook = ttk.Notebook(janelaProfessor)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    notebook.add(tab1, text="Visão Geral dos Alunos")
    notebook.add(tab2, text="Lançar/Editar Notas")

    #Filtro por CPF.
    frame_filtro_prof = tk.Frame(tab1)
    frame_filtro_prof.pack(fill="x", padx=10, pady=5)
    
    tk.Label(frame_filtro_prof, text="Filtrar por CPF:").pack(side=tk.LEFT, padx=5)
    entry_filtro_prof = tk.Entry(frame_filtro_prof, width=20)
    entry_filtro_prof.pack(side=tk.LEFT, padx=5)
    
    #Primeira aba onde mostra uma visão geral dos alunos.
    frame_treeview = tk.Frame(tab1)
    frame_treeview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    #Adiciona uma barra de rolagem.
    scrollbar = tk.Scrollbar(frame_treeview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    tree = ttk.Treeview(frame_treeview, columns=("aluno", "disciplina", "cpf"), show="headings", yscrollcommand=scrollbar.set)
    tree.heading("aluno", text="Aluno")
    tree.heading("disciplina", text="Disciplina")
    tree.heading("cpf", text="CPF")
    tree.column("aluno", width=200)
    tree.column("disciplina", width=200)
    tree.column("cpf", width=100)
    
    tree.pack(fill="both", expand=True)
    scrollbar.config(command=tree.yview)

    #Pra popular a tabela agora usa o filtro.
    def popular_treeview(cpf_filtro=None):
        for i in tree.get_children():
            tree.delete(i)
        
        #Passa o CPF do filtro para a função de busca.
        lista_alunos = buscar_alunos_do_professor(usuario_id, cpf_filtro)
        
        for aluno, disciplina, cpf in lista_alunos:
            tree.insert("", tk.END, values=(aluno, disciplina, cpf))
    
    popular_treeview()
    
    #Botão para limpar filtro.
    btn_limpar_prof = tk.Button(frame_filtro_prof, text="Limpar",
                                 command=lambda: (entry_filtro_prof.delete(0, tk.END), popular_treeview()))
    btn_limpar_prof.pack(side=tk.LEFT, padx=5)

    #O botão filtrar também atualiza a lista.
    btn_filtrar_prof = tk.Button(frame_filtro_prof, text="Filtrar", 
                                  command=lambda: popular_treeview(entry_filtro_prof.get()))
    btn_filtrar_prof.pack(side=tk.LEFT, padx=5)


    #Aba onde o professor pode lançar ou editar as notas dos alunos.
    #Dicionários para guardar os IDs das disciplinas e alunos.
    disciplinas_map = {}
    alunos_map = {}

    #Variável para guardar o ID da matrícula selecionada
    matricula_id_selecionada = None

    #Frame de seleção de aluno e disciplina (são duas combobox).
    frame_selecao = ttk.LabelFrame(tab2, text="1. Seleção", padding=10)
    frame_selecao.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_selecao, text="Disciplina:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_disciplinas = ttk.Combobox(frame_selecao, state="readonly", width=40)
    combo_disciplinas.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_selecao, text="Aluno:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    combo_alunos = ttk.Combobox(frame_selecao, state="disabled", width=50) 
    combo_alunos.grid(row=1, column=1, padx=5, pady=5)
    
    #Frame de adição ou edição de notas (duas entradas nota de trabalho e nota de provas e um botão para salvar).
    frame_edicao = ttk.LabelFrame(tab2, text="2. Lançamento de Notas (0.0 a 5.0)", padding=10)
    frame_edicao.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_edicao, text="Nota Trabalho:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entrada_nota_trabalho = tk.Entry(frame_edicao, width=10, state="disabled")
    entrada_nota_trabalho.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_edicao, text="Nota Prova:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entrada_nota_prova = tk.Entry(frame_edicao, width=10, state="disabled")
    entrada_nota_prova.grid(row=1, column=1, padx=5, pady=5)

    botao_salvar = tk.Button(frame_edicao, text="Salvar Notas", state="disabled", cursor="hand2")
    botao_salvar.grid(row=2, column=0, columnspan=2, pady=10)

    #Limpa as entradas das notas
    def limpar_campos_edicao():
        nonlocal matricula_id_selecionada
        entrada_nota_trabalho.config(state="normal")
        entrada_nota_prova.config(state="normal")
        entrada_nota_trabalho.delete(0, tk.END)
        entrada_nota_prova.delete(0, tk.END)

        #As entradas ficam desabilitadas caso não tenha uma disciplina e um aluno selecionado.
        entrada_nota_trabalho.config(state="disabled")
        entrada_nota_prova.config(state="disabled")
        botao_salvar.config(state="disabled")
        matricula_id_selecionada = None

    #Quando o professor seleciona uma disciplina, a função busca os alunos.
    def disciplina_selecionada(event):
        nonlocal alunos_map
        alunos_map.clear()
        
        #Limpa e desabilita a seleção de alunos e os campos de nota.
        combo_alunos.set("")
        combo_alunos.config(state="disabled", values=[])
        limpar_campos_edicao()
        
        disciplina_nome = combo_disciplinas.get()
        if not disciplina_nome:
            return
            
        disciplina_id = disciplinas_map[disciplina_nome]
        
        #Busca alunos da disciplina selecionada.
        lista_alunos = buscar_alunos_da_disciplina(disciplina_id)
        
        if lista_alunos:
            alunos_map.clear()     
            novos_valores_combo = []
            for id_aluno, nome_aluno, cpf_aluno in lista_alunos:
                #Cria o texto de exibição: "Nome Sobrenome (CPF: 12345678900)"
                display_text = f"{nome_aluno} (CPF: {cpf_aluno})"
                
                #Mapeia o texto de exibição para o ID do aluno
                alunos_map[display_text] = id_aluno
                novos_valores_combo.append(display_text)
            
            #Popula a combobox com os novos valores formatados
            combo_alunos.config(state="readonly", values=novos_valores_combo)
        else:
            combo_alunos.set("(Nenhum aluno matriculado)")

    #Quando o professor seleciona um aluno, essa função busca as notas do aluno.          
    def aluno_selecionado(event):
        nonlocal matricula_id_selecionada
        limpar_campos_edicao()
        
        aluno_nome = combo_alunos.get() 
        disciplina_id = disciplinas_map[combo_disciplinas.get()]
        
        if not aluno_nome or not disciplina_id:
            return
            
        aluno_id = alunos_map[aluno_nome] 
        
        #Busca a matricula_id e as notas existentes.
        dados_nota = buscar_dados_para_nota(aluno_id, disciplina_id)
        
        if dados_nota:
            matricula_id_selecionada = dados_nota[0]
            nota_trabalho = dados_nota[1]
            nota_prova = dados_nota[2]
            
            #Habilita os campos de edição de nota.
            entrada_nota_trabalho.config(state="normal")
            entrada_nota_prova.config(state="normal")

            #Preenche com 0.0 caso o aluno ainda não tenha nota lançada.
            entrada_nota_trabalho.insert(0, f"{float(nota_trabalho or 0.0):.2f}")
            entrada_nota_prova.insert(0, f"{float(nota_prova or 0.0):.2f}")
            botao_salvar.config(state="normal")

    #Se o professor clicar no botão salvar, essa função vai atualizar ou incluir as notas do aluno no banco de dados. 
    def salvar_clique():
        #Coleta os id's do aluno e disciplina.
        try:
            aluno_id = alunos_map[combo_alunos.get()] 
            disciplina_id = disciplinas_map[combo_disciplinas.get()]
            professor_id = usuario_id
        except KeyError:
            messagebox.showwarning("Aviso", "Seleção inválida. Tente novamente.")
            return

        if not matricula_id_selecionada:
            messagebox.showerror("Erro", "Não foi possível identificar a matrícula do aluno.")
            return
        
        #Validação das notas pois elas não podem ser menor que 0 ou maior que 5.
        try:
            nota_trabalho = float(entrada_nota_trabalho.get())
            nota_prova = float(entrada_nota_prova.get())
            
            if not (0.0 <= nota_trabalho <= 5.0 and 0.0 <= nota_prova <= 5.0):
                messagebox.showerror("Erro de Validação", "As notas devem estar entre 0.0 e 5.0.")
                return
        except ValueError:
            messagebox.showerror("Erro de Validação", "Por favor, insira apenas números válidos para as notas.")
            return
        
        #Chama a função para salvar no banco.
        sucesso = inserir_atualizar_notas(aluno_id, disciplina_id, professor_id, matricula_id_selecionada, nota_trabalho, nota_prova)
        
        if sucesso:
            messagebox.showinfo("Sucesso", "Notas salvas com sucesso!")
    
    #Popular a segunda aba só com as disciplinas que o professor da aula, e também vincular as funções de eventos das combobox e botão.
    def popular_disciplinas_prof():
        nonlocal disciplinas_map
        disciplinas_map.clear()
        lista_disciplinas = buscar_disciplinas_professor(usuario_id)
        if lista_disciplinas:
            disciplinas_map = {nome: id_disc for id_disc, nome in lista_disciplinas}
            combo_disciplinas.config(values=list(disciplinas_map.keys()))
        else:
            combo_disciplinas.set("(Nenhuma disciplina associada)")
            combo_disciplinas.config(state="disabled")
            
    popular_disciplinas_prof()

    combo_disciplinas.bind("<<ComboboxSelected>>", disciplina_selecionada)
    combo_alunos.bind("<<ComboboxSelected>>", aluno_selecionado)
    botao_salvar.config(command=salvar_clique)