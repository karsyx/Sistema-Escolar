import tkinter as tk
from tkinter import messagebox
import pymysql
import bcrypt
import sys
import subprocess
import importlib

########################################################################################################################################
########################################################################################################################################
#################################################### Instalar Banco ####################################################################
########################################################################################################################################
########################################################################################################################################

def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="teste12345",
        database=""
    )

def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor(pymysql.cursors.DictCursor)

    try:
        messagebox.showinfo("Conectando e Criando", "Conectando e criando banco de dados...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS gerenciamento_notas;")
        cursor.execute("USE gerenciamento_notas;")
        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cpf varchar(11) NOT NULL UNIQUE,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            senha VARCHAR(200) NOT NULL,
            primeiro_acesso INT NOT NULL,
            tipo ENUM('secretaria', 'professor', 'aluno') NOT NULL);""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS alunos (
            id INT PRIMARY KEY,
            curso VARCHAR(40),
            FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE);""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS professores (
            id INT PRIMARY KEY,
            titulacao VARCHAR(20),
            area_atuacao VARCHAR(20),
            FOREIGN KEY (id) REFERENCES usuarios(id) ON DELETE CASCADE);""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS disciplinas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            professor_id INT NOT NULL,
            FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE RESTRICT);""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS matriculas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            aluno_id INT NOT NULL,
            disciplina_id INT NOT NULL,
            UNIQUE (aluno_id, disciplina_id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE);""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS notas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            disciplina_id INT NOT NULL,
            aluno_id INT NOT NULL,
            professor_id INT NOT NULL,
            nota_trabalho DECIMAL(4,2) NOT NULL CHECK (nota_trabalho >= 0 AND nota_trabalho <= 5),
            nota_prova DECIMAL(4,2) NOT NULL CHECK (nota_prova >= 0 AND nota_prova <= 5),
            matricula_id INT NOT NULL,

            FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY (matricula_id) REFERENCES matriculas(id) ON DELETE CASCADE,
            FOREIGN KEY (professor_id) REFERENCES professores(id) ON DELETE CASCADE,
            FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE);""")
        
        conexao.commit()
        messagebox.showinfo("Banco Criado","Banco criado! Adicionando usuário de Administrador...")
        senha = "teste12345"
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'),bcrypt.gensalt())
        cursor.execute("USE gerenciamento_notas")
        comando_sql = "INSERT INTO usuarios(cpf, nome, email, senha, primeiro_acesso, tipo) VALUES ('00000000000', 'Admin', 'admin@faculdade.com.br', %s, 0, 'secretaria')"
        cursor.execute(comando_sql,(senha_hash))
        conexao.commit()
        conexao.close()
        cursor.close()
        messagebox.showinfo("Admin Cadastrado","Usuário administrador cadastrado!")
    except pymysql.err.IntegrityError as e:
        messagebox.showerror("Erro",e)

########################################################################################################################################
########################################################################################################################################
##################################################### Resetar Banco ####################################################################
########################################################################################################################################
########################################################################################################################################

def resetar_banco():
    conexao = conectar()
    cursor = conexao.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("DROP DATABASE gerenciamento_notas;")
        conexao.commit()
        conexao.close()
        cursor.close()
        messagebox.showinfo("Resetado!","Banco de dados resetado!")
    except pymysql.err.OperationalError as e:
        messagebox.showerror("Erro",e)

########################################################################################################################################
########################################################################################################################################
###################################################### Bibliotecas #####################################################################
########################################################################################################################################
########################################################################################################################################

bibliotecas_pip = ["bcrypt", "pymysql"]

def bibliotecas():
    for lib in bibliotecas_pip:
        verificar_e_instalar(lib)

def verificar_e_instalar(biblioteca):
    print(f"Verificando {biblioteca}")
    try:
        # Tenta encontrar a biblioteca se já está instalada, se não houver correspondência ele vi instalar a biblioteca.
        importlib.import_module(biblioteca.lower())
        messagebox.showinfo("Instalador de Dependências", f"A biblioteca '{biblioteca}' já está instalada.")
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", biblioteca]
            )
            messagebox.showinfo("Instalador de Dependências", f"'{biblioteca}' instalada com sucesso.")
        except subprocess.CalledProcessError as e:
            messagebox.showwarning("Instalador de Dependências", f"Falha ao instalar '{biblioteca}'. Erro: {e}")
        except FileNotFoundError:
            messagebox.showwarning("Instalador de Dependências","Comando 'pip' não encontrado. Verifique sua instalação do Python.")

########################################################################################################################################
########################################################################################################################################
###################################################### Popular Biblioteca ##############################################################
########################################################################################################################################
########################################################################################################################################

def popularBiblioteca():
    conexao = conectar()
    cursor = conexao.cursor(pymysql.cursors.DictCursor)
    
    try:
        messagebox.showinfo("Popular Banco", "Populando banco de dados com alguns usuários...")
        cursor.execute("USE gerenciamento_notas;")
        cursor.execute("""INSERT INTO usuarios (cpf, nome, email, senha, tipo, primeiro_acesso)
            VALUES ('11111111111', 'Otaviano Martins Monteiro', 
            'otaviano.monteiro@professores.newtonpaiva.br', 
            '$2b$12$D8BICH5JxnOzClcHcdCAAO5dIzbi/8VR8ER5oB9wrN9j5wZEjUoIe', 
            'professor', 1);""")

        cursor.execute("""INSERT INTO usuarios (cpf, nome, email, senha, tipo, primeiro_acesso)
            VALUES ('22222222222', 'Ana Souza Lemos',
            'ana.lemos@alunos.newtonpaiva.br',
            '$2b$12$D8BICH5JxnOzClcHcdCAAO5dIzbi/8VR8ER5oB9wrN9j5wZEjUoIe', 
            'aluno', 1);;""")

        cursor.execute("""INSERT INTO usuarios (cpf, nome, email, senha, tipo, primeiro_acesso)
            VALUES ('33333333333', 'Pedro Augusto Santos', 
            'pedro.santos@alunos.newtonpaiva.br', 
            '$2b$12$D8BICH5JxnOzClcHcdCAAO5dIzbi/8VR8ER5oB9wrN9j5wZEjUoIe', 
            'aluno', 1);""")

        cursor.execute("""INSERT INTO professores (id, titulacao, area_atuacao)
            VALUES (1, 'Doutorado', 'Computação');""")

        cursor.execute("""INSERT INTO alunos (id, curso)
            VALUES (2, 'Sistemas de Informação'), (3, 'Ciência da Computação');""")

        cursor.execute("""INSERT INTO disciplinas (nome, professor_id)
            VALUES ('Desenvolvimento Rápido de Aplicações em Python', 1);""")
        
        cursor.execute("""INSERT INTO matriculas (aluno_id, disciplina_id)
            VALUES (2, 1), (3, 1);""")
        
        cursor.execute("""INSERT INTO notas (disciplina_id, aluno_id, professor_id, nota_trabalho, nota_prova, matricula_id)
            VALUES (1, 2, 1, 4.5, 3.8, 1),  (1, 3, 1, 3.9, 4.7, 2);""")
        
        conexao.commit()
        conexao.close()
        cursor.close()
        messagebox.showinfo("Popular Banco", "Dados Cadastrados!")
    except pymysql.err.IntegrityError as e:
        messagebox.showerror("Erro",e)

janela = tk.Tk()
janela.title("Criar Banco de Dados")
janela.geometry("300x200")
janela.eval('tk::PlaceWindow . center')

#Botão para criar banco
botaoCriar = tk.Button(janela, text="Criar Banco",command=criar_banco)
botaoCriar.pack(pady=10)
botaoReset = tk.Button(janela, text="Excluir Banco",command=resetar_banco)
botaoReset.pack(pady=10)
botaoDependencias = tk.Button(janela, text="Instalar Dependências",command=bibliotecas)
botaoDependencias.pack(pady=10)
botaoPopoluar = tk.Button(janela, text="Popular Biblioteca (Para Teste)",command=popularBiblioteca)
botaoPopoluar.pack(pady=10)

janela.mainloop()