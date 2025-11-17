import tkinter as tk
from tkinter import ttk, messagebox
import pymysql
import bcrypt
import webbrowser
import subprocess
import sys
import re
from configDB import conectarDB

#Validador de cpf
def validar_cpf(cpf):
    #Limpa o CPF de qualquer formatação
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    #Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
        
    #Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
        
    #Cálculo do primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    
    if resto != int(cpf[9]):
        return False
        
    #Cálculo do segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
        
    if resto != int(cpf[10]):
        return False
        
    #Se passou por tudo, o CPF é válido
    return True

#Criptografador de senhas para os novos usuários.
def hash_senha(senha):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt)

def buscar_usuario_por_cpf(cpf, campos="id, nome, tipo"):
    #Chama a função de verificar o CPF.
    if not cpf or not validar_cpf(cpf):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return None
    
    #Conecta ao banco.
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = f"SELECT {campos} FROM usuarios WHERE cpf = %s"
        cursor.execute(sql, (cpf,))
        return cursor.fetchone()
    #Mensagem de erro se não conseguir conectar ao banco.
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar CPF: {e}")
        return None
    #Fecha a conexão e o cursor se ainda estiverem conectados ao banco.
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

def buscar_todas_disciplinas():
    #Conecta ao banco e lista todas as disciplinas.
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT id, nome FROM disciplinas ORDER BY nome"
        cursor.execute(sql)
        return cursor.fetchall()
    #Mensagem de erro se não conseguir conectar ao banco.
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar disciplinas: {e}")
        return []
    #Fecha a conexão e o cursor se ainda estiverem conectados ao banco.
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
            entrada_nova_senha.delete(0, tk.END); entrada_confirma_senha.delete(0, tk.END)
            return
        try:
            senha_hash = hash_senha(nova_senha)
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()
            sql_senha = "UPDATE usuarios SET senha = %s WHERE id = %s"
            cursor.execute(sql_senha, (senha_hash.decode('utf-8'), usuario_id))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!", parent=trocarSenha_tk)
            ao_fechar()
        except pymysql.Error as erro:
            messagebox.showerror("Erro de Banco", f"Não foi possível atualizar a senha: {erro}", parent=trocarSenha_tk)
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close(); conexao.close()
    
    def mostrar_senha():
        show = "" if var_mostrar.get() else "*"
        entrada_nova_senha.config(show=show); entrada_confirma_senha.config(show=show)
    def ao_fechar():
        trocarSenha_tk.destroy(); janela_pai.deiconify()
    tk.Label(trocarSenha_tk, text=f"Usuário (CPF): {cpf_usuario}").pack(pady=(10, 10))
    tk.Label(trocarSenha_tk, text="Nova Senha:").pack()
    entrada_nova_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_nova_senha.pack(pady=5)
    tk.Label(trocarSenha_tk, text="Confirmar Nova Senha:").pack()
    entrada_confirma_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_confirma_senha.pack(pady=5)
    var_mostrar = tk.BooleanVar()
    check_mostrar = tk.Checkbutton(trocarSenha_tk, text="Mostrar senha", variable=var_mostrar, command=mostrar_senha)
    check_mostrar.pack(pady=5)
    btn_salvar = tk.Button(trocarSenha_tk, text="Confirmar", command=salvar_nova_senha)
    btn_salvar.pack(pady=10)
    trocarSenha_tk.bind("<Return>", lambda e: salvar_nova_senha())
    #Garante que, se o usuário fechar a janela de trocar a senha, a janela do professor reapareça novamente.
    trocarSenha_tk.protocol("WM_DELETE_WINDOW", ao_fechar)

#Funçao para excluir um usuário, ela pede o cpf para excluir um usuário desejado.
def excluir_usuario(cpf_para_excluir):
    if not cpf_para_excluir:
        messagebox.showwarning("Aviso", "Digite o CPF do usuário a ser excluído.")
        return
        
    #Chama a função para verificar o cpf.
    if not validar_cpf(cpf_para_excluir):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return

    #Chama a função que busca o usuário por cpf no banco de dados.    
    dados_usuario = buscar_usuario_por_cpf(cpf_para_excluir, "id, nome, tipo")
    
    #Se não encontrar nada no banco, exibe essa mensagem de erro.
    if not dados_usuario:
        messagebox.showerror("Erro", "CPF não encontrado no banco de dados.")
        return
        
    usuario_id, nome, tipo = dados_usuario
    
    #Mensagem para confirmar a exclusão do usuário.
    confirm = messagebox.askyesno("Confirmar Exclusão",
        f"Tem certeza que deseja excluir permanentemente o usuário?\n\n"
        f"Nome: {nome}\n"
        f"CPF: {cpf_para_excluir}\n"
        f"Tipo: {tipo}\n\n"
        "AÇÃO IRREVERSÍVEL:\n"
        "Todos os dados (incluindo notas e matrículas) serão apagados.",
        icon='warning')

    #Caso confirme a exclusão, essa parte irá excluir o usuário no banco de dados.    
    if confirm:
        try:
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()
            sql = "DELETE FROM usuarios WHERE id = %s"
            cursor.execute(sql, (usuario_id,))
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Usuário '{nome}' (CPF: {cpf_para_excluir}) foi excluído.")
        except pymysql.Error as e:
            conexao.rollback()
            if "a foreign key constraint fails" in str(e) and "disciplinas" in str(e):
                 messagebox.showerror("Erro de Exclusão", 
                     f"Não foi possível excluir o professor(a) {nome}.\n\n"
                     "Motivo: Este professor ainda está vinculado a uma ou mais disciplinas.\n"
                     "É necessário desvincular ou excluir as disciplinas primeiro.")
            else:
                messagebox.showerror("Erro de Banco", f"Erro ao excluir usuário: {e}")
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close()
                conexao.close()

#Função para resetar uma senha de qualquer usuário para a padrão.
def resetar_senha(cpf_para_resetar):
    if not cpf_para_resetar:
        messagebox.showwarning("Aviso", "Digite o CPF do usuário.")
        return

    #Chama a função de verificar o CPF.
    if not validar_cpf(cpf_para_resetar):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return

    #Chama a função para buscar o usuário no banco.
    dados_usuario = buscar_usuario_por_cpf(cpf_para_resetar, "id, nome, tipo")
    
    if not dados_usuario:
        messagebox.showerror("Erro", "CPF não encontrado.")
        return
        
    usuario_id, nome, tipo = dados_usuario
    
    #As senhas padrão para cada tipo de usuário.
    if tipo == 'secretaria':
        senha_padrao = 'admin12345'
    elif tipo == 'professor':
        senha_padrao = 'professor12345'
    elif tipo == 'aluno':
        senha_padrao = 'aluno12345'
    else:
        messagebox.showerror("Erro", f"Tipo de usuário '{tipo}' desconhecido.")
        return

    #Mensagem para confirmar o reset de senha.
    confirm = messagebox.askyesno("Confirmar Reset",
        f"Deseja resetar a senha do usuário?\n\n"
        f"Nome: {nome}\n"
        f"CPF: {cpf_para_resetar}\n"
        f"Tipo: {tipo}\n\n"
        f"A nova senha será: {senha_padrao}\n"
        f"O usuário terá que trocá-la no próximo login.")
        
    #Se confirmado a mensagem acima, se conecta ao banco e reseta a senha. 
    if confirm:
        try:
            nova_senha_hash = hash_senha(senha_padrao)
            
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()
            sql = "UPDATE usuarios SET senha = %s, primeiro_acesso = 1 WHERE id = %s"
            cursor.execute(sql, (nova_senha_hash.decode('utf-8'), usuario_id))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Senha resetada com sucesso!")
        except pymysql.Error as e:
            conexao.rollback()
            messagebox.showerror("Erro de Banco", f"Erro ao resetar senha: {e}")
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close()
                conexao.close()


#Primeira aba "secretaria" onde monstra todos os usuários do tipo "secretaria".
def popular_tree_secretaria(tree, cpf_filtro=None):
    for i in tree.get_children():
        tree.delete(i)
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        #Busca todos os usuários da secretaria.
        sql = "SELECT nome, cpf FROM usuarios WHERE tipo = 'secretaria'"
        params = []
        #Chama a função de verificar CPF ao informar um CPF na opção de filtro.
        if cpf_filtro:
            if not validar_cpf(cpf_filtro):
                messagebox.showwarning("CPF Inválido", "O CPF de filtro é inválido.")
                return
            sql += " AND cpf = %s"
            params.append(cpf_filtro.strip())
    
        sql += " ORDER BY nome"
        cursor.execute(sql, tuple(params))
        
        for (nome, cpf) in cursor.fetchall():
            tree.insert("", tk.END, values=(nome, cpf))
            
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar usuários: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Função para adicionar um novo usuário do tipo "secretaria".
def adicionar_secretaria(cpf, nome, email, entry_cpf, entry_nome, entry_email, tree):
    #Todos os campos são obrigatórios.
    if not cpf or not nome or not email:
        messagebox.showwarning("Aviso", "CPF, Nome e E-mail são obrigatórios.")
        return
    
    #Novamente validando o CPF.
    if not validar_cpf(cpf):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return
        
    senha_hash = hash_senha("admin12345")
    
    #Faz a inclusão no banco.
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "INSERT INTO usuarios (cpf, nome, email, senha, primeiro_acesso, tipo) VALUES (%s, %s, %s, %s, 1, 'secretaria')"
        cursor.execute(sql, (cpf.strip(), nome, email, senha_hash.decode('utf-8')))
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Usuário da secretaria adicionado com sucesso!")
        entry_cpf.delete(0, tk.END); entry_nome.delete(0, tk.END); entry_email.delete(0, tk.END)
        popular_tree_secretaria(tree)
        
    except pymysql.Error as e:
        conexao.rollback()
        if "Duplicate entry" in str(e):
            messagebox.showerror("Erro", "CPF ou E-mail já cadastrado.")
        else:
            messagebox.showerror("Erro de Banco", f"Erro ao adicionar usuário: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Segunda aba "professores" onde monstra todos os usuários do tipo "professores".
def popular_tree_professores(tree, cpf_filtro=None):
    for i in tree.get_children():
        tree.delete(i)
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        
        sql = "SELECT u.nome, u.cpf, p.titulacao, p.area_atuacao FROM usuarios u JOIN professores p ON u.id = p.id"
        params = []
        #Novamente validando o CPF.
        if cpf_filtro:
            if not validar_cpf(cpf_filtro):
                messagebox.showwarning("CPF Inválido", "O CPF de filtro é inválido.")
                return
            sql += " WHERE u.cpf = %s"
            params.append(cpf_filtro.strip())
            
        sql += " ORDER BY u.nome"
        cursor.execute(sql, tuple(params))
        
        for (nome, cpf, titulacao, area) in cursor.fetchall():
            tree.insert("", tk.END, values=(nome, cpf, titulacao, area))
            
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar professores: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Função para adicionar um novo usuário do tipo "professor".
def adicionar_professor(cpf, nome, email, titulacao, area_atuacao, nome_disciplina, entries, combo, tree, update_callbacks=None):
    if not cpf or not nome or not email or not titulacao or not area_atuacao or not nome_disciplina:
        messagebox.showwarning("Aviso", "Todos os campos de professor são obrigatórios.")
        return
    
    #Novamente validando o CPF.
    if not validar_cpf(cpf):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return

    senha_hash = hash_senha("professor12345")
    
    conexao = pymysql.connect(**conectarDB)
    cursor = conexao.cursor()
    
    #Registra usuário no banco (professor e pelo menos uma disciplina que ele leciona).
    try:
        conexao.begin()
        
        sql_user = "INSERT INTO usuarios (cpf, nome, email, senha, primeiro_acesso, tipo) VALUES (%s, %s, %s, %s, 1, 'professor')"
        cursor.execute(sql_user, (cpf.strip(), nome, email, senha_hash.decode('utf-8')))
        
        novo_professor_id = cursor.lastrowid
        
        sql_prof = "INSERT INTO professores (id, titulacao, area_atuacao) VALUES (%s, %s, %s)"
        cursor.execute(sql_prof, (novo_professor_id, titulacao, area_atuacao))
        
        sql_disc = "INSERT INTO disciplinas (nome, professor_id) VALUES (%s, %s)"
        cursor.execute(sql_disc, (nome_disciplina, novo_professor_id))
        
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Professor e sua primeira disciplina foram cadastrados com sucesso!")
        #Deixa todas as entradas limpas após o cadastro.
        for entry in entries:
            entry.delete(0, tk.END)
        combo.set("")
        #Atualiza a tela.
        popular_tree_professores(tree)

        #Chama as funções de callback para atualizar as outras abas
        if update_callbacks:
            update_callbacks['tree_disc_update_func']()
            update_callbacks['combo_prof_update_func']()
            update_callbacks['combo_excluir_update_func']()
            update_callbacks['listbox_aluno_update_func']()
        
    except pymysql.Error as e:
        conexao.rollback()
        if "Duplicate entry" in str(e):
            messagebox.showerror("Erro", "CPF ou E-mail já cadastrado.")
        else:
            messagebox.showerror("Erro de Banco", f"Erro na transação: {e}")
    finally:
        cursor.close()
        conexao.close()

#Terceira aba "alunos" onde monstra todos os usuários do tipo "alunos".
def popular_tree_alunos(tree, cpf_filtro=None):
    for i in tree.get_children():
        tree.delete(i)
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        
        sql = "SELECT u.nome, u.cpf, u.email, a.curso FROM usuarios AS u JOIN alunos AS a ON u.id = a.id"
        params = []
        #Novamente validando o CPF.
        if cpf_filtro:
            if not validar_cpf(cpf_filtro):
                messagebox.showwarning("CPF Inválido", "O CPF de filtro é inválido.")
                return
            sql += " WHERE u.cpf = %s"
            params.append(cpf_filtro.strip())
            
        sql += " ORDER BY u.nome"
        cursor.execute(sql, tuple(params))
        
        for (nome, cpf, email, curso) in cursor.fetchall():
            tree.insert("", tk.END, values=(nome, cpf, email, curso))
            
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar alunos: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Registra um novo aluno no banco seu curso e disciplina matriculada.
def adicionar_aluno(cpf, nome, email, curso, disciplinas_selecionadas_ids, entries, listbox, tree):
    
    if not cpf or not nome or not email or not curso:
        messagebox.showwarning("Aviso", "CPF, Nome, E-mail e Curso são obrigatórios.")
        return
    
    if not validar_cpf(cpf):
        messagebox.showwarning("CPF Inválido", "O CPF digitado é inválido.")
        return

    if not disciplinas_selecionadas_ids:
        messagebox.showwarning("Aviso", "Selecione ao menos uma disciplina para o aluno.")
        return

    senha_hash = hash_senha("aluno12345")
    
    conexao = pymysql.connect(**conectarDB)
    cursor = conexao.cursor()
    
    try:
        conexao.begin()
        
        sql_user = "INSERT INTO usuarios (cpf, nome, email, senha, primeiro_acesso, tipo) VALUES (%s, %s, %s, %s, 1, 'aluno')"
        cursor.execute(sql_user, (cpf.strip(), nome, email, senha_hash.decode('utf-8')))
        
        novo_aluno_id = cursor.lastrowid
        
        sql_aluno = "INSERT INTO alunos (id, curso) VALUES (%s, %s)"
        cursor.execute(sql_aluno, (novo_aluno_id, curso))
        
        sql_matricula = "INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (%s, %s)"
        dados_matriculas = [(novo_aluno_id, disc_id) for disc_id in disciplinas_selecionadas_ids]
        cursor.executemany(sql_matricula, dados_matriculas)
        
        conexao.commit()
        
        messagebox.showinfo("Sucesso", "Aluno e matrículas cadastrados com sucesso!")
        for entry in entries:
            entry.delete(0, tk.END)
        listbox.selection_clear(0, tk.END)
        popular_tree_alunos(tree)
        
    except pymysql.Error as e:
        conexao.rollback()
        if "Duplicate entry" in str(e):
            if "(aluno_id, disciplina_id)" in str(e):
                 messagebox.showerror("Erro", "Erro de lógica de matrícula (Duplicada). Contate o ADM.")
            else:
                 messagebox.showerror("Erro", "CPF ou E-mail já cadastrado.")
        else:
            messagebox.showerror("Erro de Banco", f"Erro na transação: {e}")
    finally:
        cursor.close()
        conexao.close()

#Quinta aba que lista todas as disciplinas e o professor da disciplina. Nessa primeira estamos buscando só os professores.
def buscar_todos_professores_lista():
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT id, nome FROM usuarios WHERE tipo = 'professor' ORDER BY nome"
        cursor.execute(sql)
        return cursor.fetchall() # Lista de (id, nome)
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar lista de professores: {e}")
        return []
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Aqui busca as disciplinas e junta com os nomes dos professores.
def popular_tree_disciplinas(tree):
    for i in tree.get_children():
        tree.delete(i)
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()

        sql = "SELECT d.nome, u.nome FROM disciplinas AS d JOIN usuarios AS u ON d.professor_id = u.id ORDER BY d.nome"
        cursor.execute(sql)
        
        for (disc_nome, prof_nome) in cursor.fetchall():
            tree.insert("", tk.END, values=(disc_nome, prof_nome))
            
    except pymysql.Error as e:
        messagebox.showerror("Erro de Banco", f"Erro ao buscar disciplinas: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Função para adicionar uma nova disciplina e vincular a um professor.
def adicionar_nova_disciplina(nome_disciplina, professor_id):
    if not nome_disciplina or not professor_id:
        messagebox.showwarning("Aviso", "Nome da disciplina e Professor são obrigatórios.")
        return False
        
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        #
        sql = "INSERT INTO disciplinas (nome, professor_id) VALUES (%s, %s)"
        cursor.execute(sql, (nome_disciplina, professor_id))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Disciplina adicionada com sucesso!")
        return True
    except pymysql.Error as e:
        conexao.rollback()
        if "Duplicate entry" in str(e):
             messagebox.showerror("Erro", f"A disciplina '{nome_disciplina}' já existe.")
        else:
            messagebox.showerror("Erro de Banco", f"Erro ao adicionar disciplina: {e}")
        return False
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

#Excluir uma disciplina vinculada a um professor.
def excluir_disciplina_selecionada(disciplina_id):
    if not disciplina_id:
        messagebox.showwarning("Aviso", "Selecione uma disciplina para excluir.")
        return False
    #Mensagem para confirmar a exclusão.
    confirm = messagebox.askyesno("Confirmar Exclusão",
        f"Tem certeza que deseja excluir esta disciplina?\n\n"
        "AÇÃO IRREVERSÍVEL:\n"
        "Todas as matrículas e notas associadas a esta disciplina serão apagadas.",
        icon='warning')
    #Se confirmado, exclui.
    if confirm:
        try:
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()
            # (ON DELETE CASCADE fará a limpeza)
            sql = "DELETE FROM disciplinas WHERE id = %s"
            cursor.execute(sql, (disciplina_id,))
            conexao.commit()
            messagebox.showinfo("Sucesso", "Disciplina excluída com sucesso.")
            return True
        except pymysql.Error as e:
            conexao.rollback()
            messagebox.showerror("Erro de Banco", f"Erro ao excluir disciplina: {e}")
            return False
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close()
                conexao.close()
    return False

#Função principal para chamar a janela portalSecretaria.
def portalSecretaria(janelaSecretaria, usuario_id):
    #Busca os dados do usuário da secretaria logado.
    try:
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()
        sql = "SELECT nome, cpf FROM usuarios WHERE id = %s"
        cursor.execute(sql, (usuario_id,))
        dados_usuario = cursor.fetchone()
        if not dados_usuario:
             raise Exception("Usuário não encontrado")
    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Não foi possível buscar dados do usuário logado: {e}")
        janelaSecretaria.destroy()
        return
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()

    nome_secretaria, cpf_secretaria = dados_usuario

    #Configuração da janela
    janelaSecretaria.title(f"Portal da Secretaria - {nome_secretaria}")
    janelaSecretaria.geometry("900x650")
    janelaSecretaria.eval('tk::PlaceWindow . center')

    #Cria o menu no topo da janela.
    menu_topo = tk.Menu(janelaSecretaria)
    menu_conta = tk.Menu(menu_topo, tearoff=0)
    menu_conta.add_command(label="Informações do Usuário", 
                           command=lambda: acao_info_usuario(nome_secretaria, cpf_secretaria))
    menu_conta.add_command(label="Trocar Senha",
                           command=lambda: abrir_janela_troca_senha_menu(janelaSecretaria, usuario_id, cpf_secretaria))
    menu_conta.add_separator()
    menu_conta.add_command(label="Sair", 
                           command=lambda: acao_sair(janelaSecretaria))
    menu_sobre = tk.Menu(menu_topo, tearoff=0)
    menu_sobre.add_command(label="Apresentação", command=acao_apresentacao)
    menu_sobre.add_command(label="Github", command=acao_github)

    #Cria os sub-menu no topo da janela.
    menu_topo.add_cascade(label="Conta", menu=menu_conta)
    menu_topo.add_cascade(label="Sobre", menu=menu_sobre)
    janelaSecretaria.config(menu=menu_topo)

    #Cria um frame onde mostra o nome e cpf do usuário da secretaria.
    frame_header = tk.Frame(janelaSecretaria, pady=5)
    frame_header.pack(fill='x')
    tk.Label(frame_header, text=f"Logado como: {nome_secretaria}", font=("Arial", 12)).pack()

    #Cria todas as cinco abas.
    notebook = ttk.Notebook(janelaSecretaria)
    notebook.pack(fill="both", expand=True, padx=10, pady=5)
    
    tab1 = ttk.Frame(notebook); notebook.add(tab1, text=" Secretarias ")
    tab2 = ttk.Frame(notebook); notebook.add(tab2, text=" Professores ")
    tab3 = ttk.Frame(notebook); notebook.add(tab3, text=" Alunos ")
    tab4 = ttk.Frame(notebook); notebook.add(tab4, text=" Resetar Senhas ")
    tab5 = ttk.Frame(notebook); notebook.add(tab5, text=" Disciplinas ")

    #Cria o frame do texto "Usuários da Secretaria"    
    frame_view_sec = ttk.LabelFrame(tab1, text="Usuários da Secretaria", padding=10)
    frame_view_sec.pack(fill="x", padx=10, pady=10)
    
    #Cria o frame e adiciona um campo e botão de filtro por CPF.
    frame_filtro_sec = tk.Frame(frame_view_sec)
    frame_filtro_sec.pack(fill="x")
    tk.Label(frame_filtro_sec, text="Filtrar por CPF:").pack(side=tk.LEFT, padx=5)
    entrada_filtro_sec = tk.Entry(frame_filtro_sec, width=20)
    entrada_filtro_sec.pack(side=tk.LEFT, padx=5)
    
    tree_sec = ttk.Treeview(frame_view_sec, columns=("nome", "cpf"), show="headings", height=5)
    tree_sec.heading("nome", text="Nome"); tree_sec.heading("cpf", text="CPF")
    tree_sec.column("nome", width=400); tree_sec.column("cpf", width=150)
    #Botão filtra por CPF e atualiza a tela.
    botao_filtrar_sec = tk.Button(frame_filtro_sec, text="Filtrar", 
                               command=lambda: popular_tree_secretaria(tree_sec, entrada_filtro_sec.get()))
    botao_filtrar_sec.pack(side=tk.LEFT, padx=5)
    #Tira o filtro e atualiza a tela.
    botao_limpar_sec = tk.Button(frame_filtro_sec, text="Limpar", 
                               command=lambda: (entrada_filtro_sec.delete(0, tk.END), popular_tree_secretaria(tree_sec)))
    botao_limpar_sec.pack(side=tk.LEFT, padx=5)
    
    tree_sec.pack(fill="x", pady=10)
    popular_tree_secretaria(tree_sec)
    
    #Cria o frama geerenciamento onde tem os campos CPF, nome, email e o botão de adicionar usuário.
    frame_mng_sec = ttk.LabelFrame(tab1, text="Gerenciamento", padding=10)
    frame_mng_sec.pack(fill="x", padx=10)

    frame_add_sec = ttk.LabelFrame(frame_mng_sec, text="Adicionar Secretaria", padding=10)
    frame_add_sec.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    
    tk.Label(frame_add_sec, text="CPF:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
    entrada_cpf_sec = tk.Entry(frame_add_sec, width=30)
    entrada_cpf_sec.grid(row=0, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_sec, text="Nome:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
    entrada_nome_sec = tk.Entry(frame_add_sec, width=30)
    entrada_nome_sec.grid(row=1, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_sec, text="E-mail:").grid(row=2, column=0, sticky="w", pady=2, padx=5)
    entrada_email_sec = tk.Entry(frame_add_sec, width=30)
    entrada_email_sec.grid(row=2, column=1, pady=2, padx=5)
    
    botao_add_sec = tk.Button(frame_add_sec, text="Adicionar Usuário", 
                            command=lambda: adicionar_secretaria(entrada_cpf_sec.get(), entrada_nome_sec.get(), entrada_email_sec.get(), entrada_cpf_sec, entrada_nome_sec, entrada_email_sec, tree_sec))
    botao_add_sec.grid(row=3, column=0, columnspan=2, pady=10)

    #Adiciona um frame onde tem um campo para digitar um CPF e um botão para excluir um usuário.
    frame_del_sec = ttk.LabelFrame(frame_mng_sec, text="Excluir Usuário", padding=10)
    frame_del_sec.pack(side=tk.LEFT, fill="y", padx=5)
    
    tk.Label(frame_del_sec, text="CPF do Usuário:").pack(pady=5)
    entrada_del_cpf_sec = tk.Entry(frame_del_sec, width=20)
    entrada_del_cpf_sec.pack(pady=5, padx=5)
    botao_del_sec = tk.Button(frame_del_sec, text="Excluir", bg="#E06464", fg="white",
                            command=lambda: (excluir_usuario(entrada_del_cpf_sec.get()), popular_tree_secretaria(tree_sec), entrada_del_cpf_sec.delete(0, tk.END)))
    botao_del_sec.pack(pady=10)

    #Aba professores.
    #Cria um frame de professores cadastrados onde tem um filtro por CPF e listagem de todos os professores (quase a mesma estrutura da secretaria).
    frame_view_prof = ttk.LabelFrame(tab2, text="Professores Cadastrados", padding=10)
    frame_view_prof.pack(fill="x", padx=10, pady=10)
    
    frame_filtro_prof = tk.Frame(frame_view_prof)
    frame_filtro_prof.pack(fill="x")
    tk.Label(frame_filtro_prof, text="Filtrar por CPF:").pack(side=tk.LEFT, padx=5)
    entrada_filtro_prof = tk.Entry(frame_filtro_prof, width=20)
    entrada_filtro_prof.pack(side=tk.LEFT, padx=5)
    
    tree_prof = ttk.Treeview(frame_view_prof, columns=("nome", "cpf", "titulacao", "area"), show="headings", height=5)
    tree_prof.heading("nome", text="Nome"); tree_prof.heading("cpf", text="CPF")
    tree_prof.heading("titulacao", text="Titulação"); tree_prof.heading("area", text="Área de Atuação")
    tree_prof.column("nome", width=250); tree_prof.column("cpf", width=100)
    tree_prof.column("titulacao", width=100); tree_prof.column("area", width=150)
    
    botao_filtrar_prof = tk.Button(frame_filtro_prof, text="Filtrar",
                                 command=lambda: popular_tree_professores(tree_prof, entrada_filtro_prof.get()))
    botao_filtrar_prof.pack(side=tk.LEFT, padx=5)
    botao_limpar_prof = tk.Button(frame_filtro_prof, text="Limpar",
                                 command=lambda: (entrada_filtro_prof.delete(0, tk.END), popular_tree_professores(tree_prof)))
    botao_limpar_prof.pack(side=tk.LEFT, padx=5)
    
    tree_prof.pack(fill="x", pady=10)
    popular_tree_professores(tree_prof)
    
    #Frame dos dados para serem preenchidos para cadastrar um novo professor.
    frame_mng_prof = ttk.LabelFrame(tab2, text="Gerenciamento", padding=10)
    frame_mng_prof.pack(fill="x", padx=10)

    frame_add_prof = ttk.LabelFrame(frame_mng_prof, text="Adicionar Professor", padding=10)
    frame_add_prof.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    
    tk.Label(frame_add_prof, text="CPF:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
    entrada_cpf_prof = tk.Entry(frame_add_prof, width=30)
    entrada_cpf_prof.grid(row=0, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_prof, text="Nome:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
    entrada_nome_prof = tk.Entry(frame_add_prof, width=30)
    entrada_nome_prof.grid(row=1, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_prof, text="E-mail:").grid(row=2, column=0, sticky="w", pady=2, padx=5)
    entrada_email_prof = tk.Entry(frame_add_prof, width=30)
    entrada_email_prof.grid(row=2, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_prof, text="Titulação:").grid(row=0, column=2, sticky="w", pady=2, padx=5)
    combo_titulacao = ttk.Combobox(frame_add_prof, values=["Doutorado", "Mestrado", "Bacharel"], state="readonly")
    combo_titulacao.grid(row=0, column=3, pady=2, padx=5)
    
    tk.Label(frame_add_prof, text="Área de Atuação:").grid(row=1, column=2, sticky="w", pady=2, padx=5)
    entrada_area_prof = tk.Entry(frame_add_prof, width=30)
    entrada_area_prof.grid(row=1, column=3, pady=2, padx=5)
    
    tk.Label(frame_add_prof, text="Nome 1ª Disciplina:").grid(row=2, column=2, sticky="w", pady=2, padx=5)
    eentrada_disc_prof = tk.Entry(frame_add_prof, width=30)
    eentrada_disc_prof.grid(row=2, column=3, pady=2, padx=5)
    
    botao_add_prof = tk.Button(frame_add_prof, text="Adicionar Professor")
    botao_add_prof.grid(row=3, column=1, columnspan=2, pady=10)

    #Frame para deletar um professor.
    frame_del_prof = ttk.LabelFrame(frame_mng_prof, text="Excluir Usuário", padding=10)
    frame_del_prof.pack(side=tk.LEFT, fill="y", padx=5)
    
    tk.Label(frame_del_prof, text="CPF do Usuário:").pack(pady=5)
    entrada_del_cpf_prof = tk.Entry(frame_del_prof, width=20)
    entrada_del_cpf_prof.pack(pady=5, padx=5)
    botao_del_prof = tk.Button(frame_del_prof, text="Excluir", bg="#E06464", fg="white",
                             command=lambda: (excluir_usuario(entrada_del_cpf_prof.get()), popular_tree_professores(tree_prof), entrada_del_cpf_prof.delete(0, tk.END)))
    botao_del_prof.pack(pady=10)

    #Frame para exibir lista de alunos e filtrar por cpf como os frames já citados a cima.    
    frame_view_aluno = ttk.LabelFrame(tab3, text="Alunos Cadastrados", padding=10)
    frame_view_aluno.pack(fill="x", padx=10, pady=10)
    
    frame_filtro_aluno = tk.Frame(frame_view_aluno)
    frame_filtro_aluno.pack(fill="x")
    tk.Label(frame_filtro_aluno, text="Filtrar por CPF:").pack(side=tk.LEFT, padx=5)
    entrada_filtro_aluno = tk.Entry(frame_filtro_aluno, width=20)
    entrada_filtro_aluno.pack(side=tk.LEFT, padx=5)
    
    tree_aluno = ttk.Treeview(frame_view_aluno, columns=("nome", "cpf", "email", "curso"), show="headings", height=5)
    tree_aluno.heading("nome", text="Nome"); tree_aluno.heading("cpf", text="CPF")
    tree_aluno.heading("email", text="E-mail"); tree_aluno.heading("curso", text="Curso")
    tree_aluno.column("nome", width=250); tree_aluno.column("cpf", width=100)
    tree_aluno.column("email", width=150); tree_aluno.column("curso", width=100)
    
    botao_filtrar_aluno = tk.Button(frame_filtro_aluno, text="Filtrar",
                                  command=lambda: popular_tree_alunos(tree_aluno, entrada_filtro_aluno.get()))
    botao_filtrar_aluno.pack(side=tk.LEFT, padx=5)
    botao_limpar_aluno = tk.Button(frame_filtro_aluno, text="Limpar",
                                  command=lambda: (entrada_filtro_aluno.delete(0, tk.END), popular_tree_alunos(tree_aluno)))
    botao_limpar_aluno.pack(side=tk.LEFT, padx=5)
    
    tree_aluno.pack(fill="x", pady=10)
    popular_tree_alunos(tree_aluno)
    
    #Frame para incluir aluno, curso e disciplina.
    frame_mng_aluno = ttk.LabelFrame(tab3, text="Gerenciamento", padding=10)
    frame_mng_aluno.pack(fill="x", padx=10)

    frame_add_aluno = ttk.LabelFrame(frame_mng_aluno, text="Adicionar Aluno", padding=10)
    frame_add_aluno.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    
    tk.Label(frame_add_aluno, text="CPF:").grid(row=0, column=0, sticky="w", pady=2, padx=5)
    entrada_cpf_aluno = tk.Entry(frame_add_aluno, width=30)
    entrada_cpf_aluno.grid(row=0, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_aluno, text="Nome:").grid(row=1, column=0, sticky="w", pady=2, padx=5)
    entrada_nome_aluno = tk.Entry(frame_add_aluno, width=30)
    entrada_nome_aluno.grid(row=1, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_aluno, text="E-mail:").grid(row=2, column=0, sticky="w", pady=2, padx=5)
    entrada_email_aluno = tk.Entry(frame_add_aluno, width=30)
    entrada_email_aluno.grid(row=2, column=1, pady=2, padx=5)
    
    tk.Label(frame_add_aluno, text="Curso:").grid(row=3, column=0, sticky="w", pady=2, padx=5)
    entrada_curso_aluno = tk.Entry(frame_add_aluno, width=30)
    entrada_curso_aluno.grid(row=3, column=1, pady=2, padx=5)
    
    frame_label_disc = tk.Frame(frame_add_aluno)
    frame_label_disc.grid(row=0, column=2, sticky="nw", pady=2, padx=5)
    tk.Label(frame_label_disc, text="Disciplinas (Ctrl+Click):").pack(side=tk.LEFT)
    
    frame_listbox = tk.Frame(frame_add_aluno)
    frame_listbox.grid(row=0, column=3, rowspan=4, pady=2, padx=5, sticky="ns")
    
    scrollbar_disc = tk.Scrollbar(frame_listbox, orient=tk.VERTICAL)
    listbox_disciplinas = tk.Listbox(frame_listbox, selectmode=tk.MULTIPLE, height=6, yscrollcommand=scrollbar_disc.set)
    scrollbar_disc.config(command=listbox_disciplinas.yview)
    
    scrollbar_disc.pack(side=tk.RIGHT, fill=tk.Y)
    listbox_disciplinas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    disciplinas_map = {}
    
    #Esta função agora é chamada automaticamente ao abrir a quinta aba para mostrar todas as disciplinas.
    def _popular_lista_disciplinas():
        nonlocal disciplinas_map
        listbox_disciplinas.delete(0, tk.END)
        disciplinas_map.clear()
        lista_disciplinas = buscar_todas_disciplinas()
        for disc_id, disc_nome in lista_disciplinas:
            listbox_disciplinas.insert(tk.END, disc_nome)
            disciplinas_map[disc_nome] = disc_id

    botao_atualizar_disc = tk.Button(frame_label_disc, text="Atualizar", 
                                   command=_popular_lista_disciplinas,
                                   font=("Arial", 8), cursor="hand2")
    botao_atualizar_disc.pack(side=tk.LEFT, padx=5)

    _popular_lista_disciplinas()

    #Função para pegar uma ou várias disciplinas para serem adicionadas ao aluno.
    def _adicionar_aluno_click():
        selected_indices = listbox_disciplinas.curselection()
        selected_ids = [disciplinas_map[listbox_disciplinas.get(i)] for i in selected_indices]
        
        adicionar_aluno(
            entrada_cpf_aluno.get(), entrada_nome_aluno.get(), entrada_email_aluno.get(),
            entrada_curso_aluno.get(), selected_ids,
            [entrada_cpf_aluno, entrada_nome_aluno, entrada_email_aluno, entrada_curso_aluno],
            listbox_disciplinas, tree_aluno
        )

    botao_add_aluno = tk.Button(frame_add_aluno, text="Adicionar Aluno",
                              command=_adicionar_aluno_click)
    botao_add_aluno.grid(row=4, column=1, columnspan=2, pady=10)

    #Frame para excluir aluno.
    frame_del_aluno = ttk.LabelFrame(frame_mng_aluno, text="Excluir Usuário", padding=10)
    frame_del_aluno.pack(side=tk.LEFT, fill="y", padx=5)
    
    tk.Label(frame_del_aluno, text="CPF do Usuário:").pack(pady=5)
    entrada_del_cpf_aluno = tk.Entry(frame_del_aluno, width=20)
    entrada_del_cpf_aluno.pack(pady=5, padx=5)
    botao_del_aluno = tk.Button(frame_del_aluno, text="Excluir", bg="#E06464", fg="white",
                              command=lambda: (excluir_usuario(entrada_del_cpf_aluno.get()), popular_tree_alunos(tree_aluno), entrada_del_cpf_aluno.delete(0, tk.END)))
    botao_del_aluno.pack(pady=10)

    #Quarta aba tem um frame que recebe CPF e um botão para resetar a senha do usuário.
    frame_reset = ttk.LabelFrame(tab4, text="Resetar Senha de Usuário", padding=20)
    frame_reset.pack(padx=20, pady=20)
    
    tk.Label(frame_reset, text="CPF do Usuário:").grid(row=0, column=0, padx=10, pady=10)
    entrada_reset_cpf = tk.Entry(frame_reset, width=30)
    entrada_reset_cpf.grid(row=0, column=1, padx=10, pady=10)
    
    botao_reset = tk.Button(frame_reset, text="Confirmar Reset de Senha", 
                          command=lambda: (resetar_senha(entrada_reset_cpf.get()),
                                           entrada_reset_cpf.delete(0, tk.END)))
    botao_reset.grid(row=1, column=0, columnspan=2, pady=10)

    #Quinta aba de disciplinas, lista as disciplinas cadastradas e seu professor e um botão de filtrar listar.
    professores_map = {} 
    disciplinas_excluir_map = {} 

    frame_view_disc = ttk.LabelFrame(tab5, text="Disciplinas Cadastradas", padding=10)
    frame_view_disc.pack(fill="x", padx=10, pady=10)
    
    tree_disc = ttk.Treeview(frame_view_disc, columns=("disciplina", "professor"), show="headings", height=6)
    tree_disc.heading("disciplina", text="Nome da Disciplina")
    tree_disc.heading("professor", text="Professor Responsável")
    tree_disc.column("disciplina", width=350)
    
    tree_disc.pack(fill="x", side=tk.LEFT, expand=True)
    
    btn_atualizar_tree_disc = tk.Button(frame_view_disc, text="Atualizar Lista",
                                        command=lambda: popular_tree_disciplinas(tree_disc))
    btn_atualizar_tree_disc.pack(side=tk.LEFT, padx=10)
    
    popular_tree_disciplinas(tree_disc)

    #Frame para cadastrar uma disciplina e vincular um professor existente na nova disciplina.
    frame_mng_disc = ttk.LabelFrame(tab5, text="Gerenciamento", padding=10)
    frame_mng_disc.pack(fill="x", padx=10)

    frame_add_disc = ttk.LabelFrame(frame_mng_disc, text="Adicionar Nova Disciplina", padding=10)
    frame_add_disc.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    
    tk.Label(frame_add_disc, text="Nome da Disciplina:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
    entrada_nome_disc = tk.Entry(frame_add_disc, width=35)
    entrada_nome_disc.grid(row=0, column=1, pady=5, padx=5)
    
    tk.Label(frame_add_disc, text="Professor Responsável:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
    combo_prof_disc = ttk.Combobox(frame_add_disc, state="readonly", width=33)
    combo_prof_disc.grid(row=1, column=1, pady=5, padx=5)
    
    #Lista todos os professores na combobox.
    def _popular_combo_professores():
        nonlocal professores_map
        professores_map.clear()
        lista_profs = buscar_todos_professores_lista()
        prof_nomes = []
        for prof_id, prof_nome in lista_profs:
            prof_nomes.append(prof_nome)
            professores_map[prof_nome] = prof_id
        combo_prof_disc.config(values=prof_nomes)
        
    _popular_combo_professores()

    #Função para adicionar a nova disciplina.
    def _adicionar_disciplina_click():
        nome = entrada_nome_disc.get()
        prof_nome = combo_prof_disc.get()
        
        if not nome or not prof_nome:
            messagebox.showwarning("Aviso", "Preencha o nome e selecione o professor.")
            return
            
        prof_id = professores_map[prof_nome]
        
        sucesso = adicionar_nova_disciplina(nome, prof_id)
        if sucesso:
            #Atualiza a lista e deleta as entradas.
            popular_tree_disciplinas(tree_disc)
            _popular_lista_disciplinas()
            entrada_nome_disc.delete(0, tk.END)
            combo_prof_disc.set("")
            #Atualiza a combobox de exclusão também
            _popular_combo_disciplinas_excluir()

    botao_add_disc = tk.Button(frame_add_disc, text="Adicionar Disciplina",
                             command=_adicionar_disciplina_click)
    botao_add_disc.grid(row=2, column=0, columnspan=2, pady=10)


    #Frame para excluir disciplina.
    frame_del_disc = ttk.LabelFrame(frame_mng_disc, text="Excluir Disciplina", padding=10)
    frame_del_disc.pack(side=tk.LEFT, fill="y", padx=5)
    
    tk.Label(frame_del_disc, text="Selecione a Disciplina:").pack(pady=5)
    combo_excluir_disc = ttk.Combobox(frame_del_disc, state="readonly", width=30)
    combo_excluir_disc.pack(pady=5, padx=5)
    
    #Popula a combobox com disciplinas.
    def _popular_combo_disciplinas_excluir():
        nonlocal disciplinas_excluir_map
        disciplinas_excluir_map.clear()
        lista_disc = buscar_todas_disciplinas()
        disc_nomes = []
        for disc_id, disc_nome in lista_disc:
            disc_nomes.append(disc_nome)
            disciplinas_excluir_map[disc_nome] = disc_id
        combo_excluir_disc.config(values=disc_nomes)
        combo_excluir_disc.set("")
        
    _popular_combo_disciplinas_excluir()
    
    #Exibe uma mensagem de confirmação de deleção de disciplina caso clique no botão excluir.
    def _excluir_disciplina_click():
        disc_nome = combo_excluir_disc.get()
        if not disc_nome:
            messagebox.showwarning("Aviso", "Selecione uma disciplina para excluir.")
            return
            
        disc_id = disciplinas_excluir_map[disc_nome]
        
        sucesso = excluir_disciplina_selecionada(disc_id)
        if sucesso:
            #Atualiza a lista.
            popular_tree_disciplinas(tree_disc)
            _popular_lista_disciplinas()
            _popular_combo_disciplinas_excluir()
    
    botao_del_disc = tk.Button(frame_del_disc, text="Excluir", bg="#E06464", fg="white", command=_excluir_disciplina_click)
    botao_del_disc.pack(pady=10)


    #Atualiza as combobox da aba de disciplinas.
    update_callbacks_dict = {
        'tree_disc_update_func': lambda: popular_tree_disciplinas(tree_disc), 
        'combo_prof_update_func': _popular_combo_professores,
        'combo_excluir_update_func': _popular_combo_disciplinas_excluir,
        'listbox_aluno_update_func': _popular_lista_disciplinas 
    }
    
    botao_add_prof.config(command=lambda: adicionar_professor(
                             entrada_cpf_prof.get(), entrada_nome_prof.get(), entrada_email_prof.get(), 
                             combo_titulacao.get(), entrada_area_prof.get(), eentrada_disc_prof.get(), 
                             [entrada_cpf_prof, entrada_nome_prof, entrada_email_prof, entrada_area_prof, eentrada_disc_prof],
                             combo_titulacao, 
                             tree_prof,
                             update_callbacks_dict
                         ))