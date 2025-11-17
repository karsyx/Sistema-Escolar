import tkinter as tk
from tkinter import messagebox
import bcrypt
import pymysql
from configDB import conectarDB
from trocaSenha import trocarSenha
from aluno import portalAluno
from professor import portalProfessor
from secretaria import portalSecretaria

def verificar_usuario():
    cpf = entrada_cpf.get().strip()
    senha = entrada_senha.get()

    #Mensagem de aviso caso o campo de senha ou CPF estejam em branco
    if not cpf or not senha:
        messagebox.showwarning("Aviso","Os campos CPF e Senha são obrigatórios!")
        limpar_campos()
        return
    
    try:
        #Conecta com o banco de dados
        conexao = pymysql.connect(**conectarDB)
        cursor = conexao.cursor()

        #Verifica se exsite o usuário.
        sql = "SELECT id, senha, primeiro_acesso, tipo FROM usuarios WHERE cpf = %s"
        cursor.execute(sql, (cpf,))
        usuario_data = cursor.fetchone()

        #Se 'usuario_data' for None, o CPF não existe
        if not usuario_data:
            messagebox.showerror("", "CPF ou senha inválidos.")
            limpar_campos()
            return

        #Desempacota os dados se o usuário foi encontrado
        usuario_id = usuario_data[0]
        senha_hash_banco = usuario_data[1].encode('utf-8')
        primeiro_acesso = usuario_data[2]
        tipo_de_conta = usuario_data[3]

        #Criptografando a senha fornecida e checando com o banco
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_banco):
            cursor.close()
            conexao.close()
            
            #Se for o primeiro acesso, chama a janela de troca de senha
            if primeiro_acesso == 1:
                janela_troca_senha = tk.Toplevel(janelaLogin)
                janelaLogin.withdraw() #Esconde a tela de login
                trocarSenha(janela_troca_senha, usuario_id, cpf, janelaLogin, primeiro_acesso)
                
            else:
                #Se não for primeiro acesso, redireciona para a janela correta
                #Se o tipo de conta pertence a secretaria, a tela de login redicionará para a janela da secretaria.
                if tipo_de_conta == "secretaria":
                    #Colocar aqui a função de redirecionamento
                    janelaLogin.destroy()
                    janelaSecretaria = tk.Tk() 
                    portalSecretaria(janelaSecretaria, usuario_id) 
                    janelaSecretaria.mainloop()

                #Se o tipo de conta pertence a um aluno, a tela de login redicionará para a janela de alunos.
                elif tipo_de_conta == "aluno":
                    janelaLogin.destroy() # Fecha a janela de login
                    #Cria a nova janela principal (Tk) para o aluno
                    janelaAluno = tk.Tk() 
                    portalAluno(janelaAluno, usuario_id) 
                    janelaAluno.mainloop()

                #Se o tipo de conta pertence a professor, a tela de login redicionará para a janela do professor.
                elif tipo_de_conta == "professor":
                    janelaLogin.destroy()
                    janelaProfessor = tk.Tk() 
                    portalProfessor(janelaProfessor, usuario_id) 
                    janelaProfessor.mainloop()

        
        else:
            #Se a senha estiver incorreta
            messagebox.showerror("", "CPF ou senha inválidos.")
            limpar_campos()

    #Se usuário ou senhas estiverem incorretos, irá exibir uma mensagem de erro para o usuário.
    except TypeError:
        messagebox.showerror("", "CPF ou senha inválidos.")
        limpar_campos()

    #Exibe uma mensagem de erro caso o programa não consiga se conectar com o banco de dados.
    except pymysql.Error as erro:
        messagebox.showerror("Erro","Não foi possível se conectar ao banco de dados!\n" + str(erro))

    finally:
        #Se o login falhar ou a conexão de dados também falhar, esse comando vai fechar a conexao.
        if conexao and conexao.open:
            cursor.close()
            conexao.close()

#Função para mostrar ou não a senha.
def mostrar_senha():
    if var_mostrar.get():
        entrada_senha.config(show="")
    else:
        entrada_senha.config(show="*")

#Função que limpa os campos de entrada CPF e Senha.
def limpar_campos():
    entrada_cpf.delete(0,tk.END)
    entrada_senha.delete(0,tk.END)

#Tela de login
janelaLogin = tk.Tk()
janelaLogin.title("Login")
janelaLogin.geometry("300x200")
janelaLogin.eval('tk::PlaceWindow . center')

#Campo CPF
tk.Label(janelaLogin, text="CPF: ").pack(pady=(10,0))
entrada_cpf = tk.Entry(janelaLogin, width=30)
entrada_cpf.pack()

#Campo senha
tk.Label(janelaLogin, text="Senha: ").pack(pady=(10,0))
entrada_senha = tk.Entry(janelaLogin, width=30, show="*")
entrada_senha.pack()

#Opção gráfica para mostrar ou não a senha.
var_mostrar = tk.BooleanVar()
check_mostrar = tk.Checkbutton(janelaLogin, text="Mostrar senha", variable=var_mostrar, command=mostrar_senha)
check_mostrar.pack(pady=5)

#Botão de login
botao = tk.Button(janelaLogin, text="Entrar", cursor="hand2", command=verificar_usuario)
botao.pack(pady=20)
janelaLogin.bind("<Return>", lambda e: verificar_usuario())

janelaLogin.mainloop()