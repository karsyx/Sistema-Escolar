import tkinter as tk
from tkinter import messagebox
import bcrypt
import pymysql
from configDB import conectarDB

#Criando uma nova janela independente da janela principal com "tk.Toplevel".
def trocarSenha(trocarSenha_tk, usuario_id, cpf, janelaLogin, primeiro_acesso):
   
    #Cria e gerencia a janela Toplevel para troca de senha.
    geometria = "300x260"
    #Texto na tela de troca de senha.
    if primeiro_acesso == 1:
        tk.Label(trocarSenha_tk, text="No primeiro a acesso a troca de senha é obrigatória!").pack(pady=10)
    else:
        geometria = "300x230"

    trocarSenha_tk.title("Trocar Senha")
    trocarSenha_tk.geometry(geometria)
    janelaLogin.eval(f'tk::PlaceWindow {trocarSenha_tk} center')
        
    def salvar_nova_senha():
        #Paga a nova senha e a confirmação da nova senha enviadas pelo o usuário.
        nova_senha = entrada_nova_senha.get()
        confirma_senha = entrada_confirma_senha.get()

        #Exibe um erro se um ou ambos os campos estiverem em branco
        if not nova_senha or not confirma_senha:
            messagebox.showerror("", "Ambos os campos são obrigatórios.", parent=trocarSenha_tk)
            return

        #Exibe um erro se as senhas não coincidirem e deleta as informações de ambos os campos.
        if nova_senha != confirma_senha:
            messagebox.showerror("Erro", "As senhas não coincidem.", parent=trocarSenha_tk)
            entrada_nova_senha.delete(0, tk.END)
            entrada_confirma_senha.delete(0, tk.END)
            return
        
        try:
            #Criptografa a nova senha
            salt = bcrypt.gensalt()
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), salt)
            
            #Conecta ao banco
            conexao = pymysql.connect(**conectarDB)
            cursor = conexao.cursor()

            #Atualizar a senha usando o id do usuário da função da 'janela login'
            sql_senha = "UPDATE usuarios SET senha = %s WHERE id = %s"
            cursor.execute(sql_senha, (senha_hash.decode('utf-8'), usuario_id))
            
            # Atualizar o status de primeiro acesso de verdadeiro para falso caso seja o primeiro acesso
            sql_acesso = "UPDATE usuarios SET primeiro_acesso = 0 WHERE id = %s"
            cursor.execute(sql_acesso, (usuario_id,))
            
            #Valida as mudanças de senha no banco de dados, e também valida a mudança de status de primeiro acesso no banco se for o caso.
            conexao.commit()
            
            messagebox.showinfo("", "Senha alterada com sucesso! Faça o login novamente.", parent=trocarSenha_tk)
            
            #Fechar esta janela de troca de senha e exibe novamente a de login
            ao_fechar()

        except pymysql.Error as erro:
            messagebox.showerror("Erro de Banco", f"Não foi possível atualizar a senha: {erro}", parent=trocarSenha_tk)
        except Exception as e:
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro: {e}", parent=trocarSenha_tk)
        finally:
            if 'conexao' in locals() and conexao.open:
                cursor.close()
                conexao.close()
    
    #Mostrar ou ocultar os campos 'nova senha' e 'confirmar nova senha'
    def mostrar_senha():
        if var_mostrar.get():
            entrada_nova_senha.config(show="")
            entrada_confirma_senha.config(show="")
        else:
            entrada_nova_senha.config(show="*")
            entrada_confirma_senha.config(show="*")

    def ao_fechar():
        trocarSenha_tk.destroy() #Fecha esta janela (Toplevel)
        janelaLogin.deiconify() #Reexibe a janela de login principal

    tk.Label(trocarSenha_tk, text=f"Usuário (CPF): {cpf}").pack(pady=(0, 10))

    #Campo da nova senha.
    tk.Label(trocarSenha_tk, text="Nova Senha:").pack()
    entrada_nova_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_nova_senha.pack(pady=5)

    #Campo para confirmar a nova senha.
    tk.Label(trocarSenha_tk, text="Confirmar Nova Senha:").pack()
    entrada_confirma_senha = tk.Entry(trocarSenha_tk, width=30, show="*")
    entrada_confirma_senha.pack(pady=5)

    #Opção gráfica para mostrar ou não a senha.
    var_mostrar = tk.BooleanVar()
    check_mostrar = tk.Checkbutton(trocarSenha_tk, text="Mostrar senha", variable=var_mostrar, command=mostrar_senha)
    check_mostrar.pack(pady=5)

    #Botão para chamar a função para salvar a senha
    btn_salvar = tk.Button(trocarSenha_tk, text="Confirmar", command=salvar_nova_senha)
    btn_salvar.pack(pady=10)
    trocarSenha_tk.bind("<Return>", lambda e: salvar_nova_senha())

    #Garante que se o usuário clicar no "X" para fechar a janela, a janela de login reapareça.
    trocarSenha_tk.protocol("WM_DELETE_WINDOW", ao_fechar)