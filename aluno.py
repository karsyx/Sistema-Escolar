import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import bcrypt
import webbrowser
import subprocess
import sys
from configDB import conectarDB

#Pega dados mais dados do aluno recebendo o id do usuário da janela de login.
def encontrar_dados(usuario_id):
    
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        
        sql = "SELECT u.nome, u.cpf, a.curso FROM usuarios AS u JOIN alunos AS a ON u.id = a.id WHERE u.id = %s"
        
        cursor.execute(sql, (usuario_id,))
        dados = cursor.fetchone()
        return dados  #Retorna (nome, cpf e o curso)

    #Mensagem de erro caso não consiga encontrar os dados do aluno no banco    
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar dados do aluno: {e}")
        return None
    #Caso a conexão com o banco ainda esteja aberta, esses comandos finaliza a conexão e o cursor.
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca as diciplinas em que o aluno está matriculado.
def encontrar_disciplinas(aluno_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        
        sql = "SELECT d.id, d.nome FROM disciplinas AS d JOIN matriculas AS m ON d.id = m.disciplina_id WHERE m.aluno_id = %s ORDER BY d.nome"
        
        cursor.execute(sql, (aluno_id,))
        disciplinas = cursor.fetchall()
        return disciplinas  # Retorna lista de id da disciplina e o nome

    #Mensagem de erro caso não consiga encontrar os dados da disciplina do aluno  
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar disciplinas: {e}")
        return []
    #Caso a conexão com o banco ainda esteja aberta, esses comandos finaliza a conexão e o cursor.
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Busca todas as notas das disciplinas lançadas pelo o professor ou não.
def encontrar_notas(aluno_id, disciplina_id):
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()

        sql = "SELECT nota_trabalho, nota_prova FROM notas WHERE aluno_id = %s AND disciplina_id = %s"
        
        cursor.execute(sql, (aluno_id, disciplina_id))
        notas = cursor.fetchone()
        return notas  #Retorna nota_trabalho, nota_prova ou nada (None)
    
    #Mensagem de erro caso não consiga conectar ao banco notas. 
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Não foi possível buscar as notas: {e}")
        return None
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
    subprocess.Popen([sys.executable, 'login.py'])

#redireciona para o navegador web abrir uma página.
def acao_apresentacao():
    webbrowser.open("https://www.youtube.com/watch?v=YYE8ZLlReu4")

def acao_github():
    webbrowser.open("https://github.com/karsyx")

#Usuário consegue trocar a sua senha de acesso.
def abrir_janela_troca_senha_menu(janela_aluno, usuario_id, cpf_usuario):
    janela_aluno.withdraw()
    
    trocarSenha_tk = tk.Toplevel(janela_aluno)
    trocarSenha_tk.title("Trocar Senha")
    trocarSenha_tk.geometry("300x230")

    janela_aluno.eval(f'tk::PlaceWindow {trocarSenha_tk} center')
        
    def salvar_nova_senha():
        nova_senha = entrada_nova_senha.get()
        confirma_senha = entrada_confirma_senha.get()

        #Obrigatório ter os campos preenchidos.
        if not nova_senha or not confirma_senha:
            messagebox.showerror("Erro", "Ambos os campos são obrigatórios!", parent=trocarSenha_tk)
            return

        if nova_senha != confirma_senha:
            messagebox.showerror("Erro", "As senhas não coincidem!", parent=trocarSenha_tk)
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
    
    def mostrar_senha():
        if mostrar.get():
            entrada_nova_senha.config(show="")
            entrada_confirma_senha.config(show="")
        else:
            entrada_nova_senha.config(show="*")
            entrada_confirma_senha.config(show="*")

    def ao_fechar():
        trocarSenha_tk.destroy()
        janela_aluno.deiconify()

    tk.Label(trocarSenha_tk, text=f"Usuário (CPF): {cpf_usuario}").pack(pady=(10, 10))
    tk.Label(trocarSenha_tk, text="Nova Senha:").pack()

    entrada_nova_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_nova_senha.pack(pady=5)

    tk.Label(trocarSenha_tk, text="Confirmar Nova Senha:").pack()
    entrada_confirma_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_confirma_senha.pack(pady=5)

    mostrar = tk.BooleanVar()
    check_mostrar = tk.Checkbutton(trocarSenha_tk, text="Mostrar senha", variable=mostrar, command=mostrar_senha)
    check_mostrar.pack(pady=5)

    btn_salvar = tk.Button(trocarSenha_tk, text="Confirmar", command=salvar_nova_senha)
    btn_salvar.pack(pady=10)
    trocarSenha_tk.bind("<Return>", lambda e: salvar_nova_senha())

    #Garante que, se o usuário fechar a janela de trocar a senha, a janela do aluno reapareça novamente.
    trocarSenha_tk.protocol("WM_DELETE_WINDOW", ao_fechar)

#A tela principal do aluno.
def portalAluno(janelaAluno, usuario_id):
    #Recebe o id do usuario e caso não tenha id, a janela será fechada.
    dados_aluno = encontrar_dados(usuario_id)
    if not dados_aluno:
        messagebox.showerror("Erro Crítico", "Não foi possível carregar os dados do aluno. Encerrando.")
        janelaAluno.destroy()
        return
        
    nome_aluno, cpf_aluno, curso_aluno = dados_aluno

    #Cria Janela.
    janelaAluno.title(f"Portal do Aluno - {nome_aluno}")
    janelaAluno.geometry("500x400")
    janelaAluno.eval('tk::PlaceWindow . center')

    #Cria o menu no topo da janela.
    menu_topo = tk.Menu(janelaAluno)
    menu_conta = tk.Menu(menu_topo, tearoff=0)
    menu_conta.add_command(label="Informações do Usuário", 
                           command=lambda: acao_info_usuario(nome_aluno, cpf_aluno))
    menu_conta.add_command(label="Trocar Senha",
                           command=lambda: abrir_janela_troca_senha_menu(janelaAluno, usuario_id, cpf_aluno))
    menu_conta.add_separator()
    menu_conta.add_command(label="Sair", 
                           command=lambda: acao_sair(janelaAluno))
    
    menu_sobre = tk.Menu(menu_topo, tearoff=0)
    menu_sobre.add_command(label="Apresentação", command=acao_apresentacao)
    menu_sobre.add_command(label="Github", command=acao_github)

    #Cria os sub-menu no topo da janela.
    menu_topo.add_cascade(label="Conta", menu=menu_conta)
    menu_topo.add_cascade(label="Sobre", menu=menu_sobre)
    janelaAluno.config(menu=menu_topo)

    #Cria um frame onde mostra o nome e o curso do aluno.
    frame_aluno = tk.Frame(janelaAluno, pady=10)
    frame_aluno.pack(fill='x')
    
    tk.Label(frame_aluno, text=f"Aluno: {nome_aluno}", font=("Arial", 12)).pack()
    tk.Label(frame_aluno, text=f"Curso: {curso_aluno}", font=("Arial", 10)).pack()

    #Cria um frame que tem uma combobox onde contém as disciplinas.
    frame_disciplinas = tk.Frame(janelaAluno, pady=10)
    frame_disciplinas.pack(fill='x')

    tk.Label(frame_disciplinas, text="Selecione a Disciplina:", font=("Arial", 10)).pack()
    
    lista_disciplinas = encontrar_disciplinas(usuario_id)
    
    #Guarda o id das disciplinas.
    disciplinas_map = {nome: id_disc for id_disc, nome in lista_disciplinas}
    
    combo_disciplinas = ttk.Combobox(frame_disciplinas, values=list(disciplinas_map.keys()), state="readonly", width=50)
    combo_disciplinas.pack(pady=5)

    #Frame onde exibe as notas.
    frame_notas = tk.Frame(janelaAluno, pady=15, relief=tk.GROOVE, borderwidth=2)
    frame_notas.pack(fill='x', padx=20, pady=10)

    tk.Label(frame_notas, text="Boletim da Disciplina", font=("Arial", 12, "bold")).pack(pady=5)

    #Campos de extos que serão atualizadas com as notas.
    label_trabalho = tk.Label(frame_notas, text="Nota Trabalho: N/A", font=("Arial", 10))
    label_trabalho.pack()
    
    label_prova = tk.Label(frame_notas, text="Nota Prova: N/A", font=("Arial", 10))
    label_prova.pack()
    
    label_soma = tk.Label(frame_notas, text="Soma: N/A", font=("Arial", 10, "bold"))
    label_soma.pack(pady=5)
    
    label_status = tk.Label(frame_notas, text="Status: N/A", font=("Arial", 12, "bold"))
    label_status.pack(pady=10)

    #Função bara buscar as notas e atualizar os dados nos campos de texto acima.
    def atualizar_notas(event):
        disciplina_nome = combo_disciplinas.get()
        if not disciplina_nome:
            return
            
        disciplina_id = disciplinas_map[disciplina_nome]
        
        #Busca as notas no banco
        notas = encontrar_notas(usuario_id, disciplina_id)
        
        n_trabalho = 0.0
        n_prova = 0.0
        
        if notas:
            #Converte de Decimal/None para float.
            n_trabalho = float(notas[0] or 0.0)
            n_prova = float(notas[1] or 0.0)
            
            soma = n_trabalho + n_prova
            status = "Aprovado" if soma >= 6.0 else "Reprovado"
            
            #Atualiza os campos de textos.
            label_trabalho.config(text=f"Nota Trabalho: {n_trabalho:.2f}")
            label_prova.config(text=f"Nota Prova: {n_prova:.2f}")
            label_soma.config(text=f"Soma: {soma:.2f}")
            label_status.config(text=f"Status: {status}", 
                                fg="green" if status == "Aprovado" else "red")
        else:
            #Caso não haja notas lançadas é para deixar as notas como nulas.
            label_trabalho.config(text="Nota Trabalho: (Não lançada)")
            label_prova.config(text="Nota Prova: (Não lançada)")
            label_soma.config(text="Soma: N/A")
            label_status.config(text="Status: Aguardando notas", fg="black")

    #Chama a função de buscar as ao selecionar uma disciplina na combobox.
    combo_disciplinas.bind("<<ComboboxSelected>>", atualizar_notas)