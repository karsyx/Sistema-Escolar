# Sistema de Gerenciamento Acadêmico (Python + Tkinter)

Projeto de faculdade para a disciplina de **Python** do curso de **Análise e Desenvolvimento de Sistemas**.

## 📖 Sobre o Projeto

Este é um sistema de desktop completo para o gerenciamento de notas acadêmicas. Construído inteiramente em Python, ele utiliza a biblioteca nativa **Tkinter** para a interface gráfica e se conecta a um banco de dados **MySQL**.

O programa simula um ambiente acadêmico com três níveis de acesso distintos, cada um com suas próprias funcionalidades:
* **Secretaria (Admin)**
* **Professor**
* **Aluno**

## ✨ Principais Funcionalidades

O sistema é dividido por portais, cada um com responsabilidades específicas:

### 👩‍💼 Portal da Secretaria (Admin)
O portal de secretaria é o núcleo administrativo do sistema, com controle total sobre os dados.
* **Gerenciamento de Usuários:** CRUD completo para Alunos, Professores e outros usuários da Secretaria.
* **Validação de CPF:** Impede o cadastro de CPFs inválidos.
* **Gerenciamento de Disciplinas:** Permite criar ou excluir disciplinas e associá-las a um professor.
* **Matrícula de Alunos:** Permite matricular alunos em uma ou mais disciplinas.
* **Reset de Senha:** Função para resetar a senha de qualquer usuário para um valor padrão.

### 🧑‍🏫 Portal do Professor
O professor tem acesso às ferramentas para gerenciar suas turmas e notas.
* **Visão Geral:** Exibe uma lista de todos os alunos matriculados em suas disciplinas.
* **Filtro:** Permite filtrar a lista de alunos por CPF.
* **Lançamento de Notas:** Interface para lançar ou editar "Nota de Trabalho" e "Nota de Prova" para cada aluno.

### 🎓 Portal do Aluno
O portal do aluno é focado na consulta de seu desempenho acadêmico.
* **Boletim:** Permite ao aluno selecionar uma disciplina matriculada e ver suas notas.
* **Cálculo Automático:** Exibe a soma das notas (Trabalho + Prova) e o status final (Aprovado ou Reprovado).
* **Consulta de Dados:** Exibe o nome do aluno e o curso em que está matriculado.

### 🔐 Funcionalidades Comuns
* **Sistema de Login Seguro:** Autenticação de usuário com senhas criptografadas usando **bcrypt**.
* **Primeiro Acesso:** Força o usuário a trocar sua senha padrão no primeiro login.
* **Gerenciamento de Conta:** Todos os portais possuem um menu para o usuário ver seus dados, trocar a própria senha ou sair (retornando à tela de login).

## 🖥️ Telas do Sistema

<table>
  <tr>
    <td align="center"><strong>Portal da Secretaria</strong></td>
    <td align="center"><strong>Portal do Professor</strong></td>
    <td align="center"><strong>Portal do Aluno</strong></td>
  </tr>
  <tr>
    <td><img src="https://i.ibb.co/tPFR8Q8f/Portal-Secretaria.png" alt="Tela da Secretaria" width="400"></td>
    <td><img src="https://i.ibb.co/n49VhZ4/Portal-Professor.png" alt="Tela do Professor" width="400"></td>
    <td><img src="https://i.ibb.co/pvcFGKb0/Portal-Aluno.png" alt="Tela do Aluno" width="400"></td>
  </tr>
</table>

## 🛠️ Tecnologias Utilizadas

* **Python 3**
* **Tkinter** (Biblioteca nativa do Python para GUI)
* **MySQL** (Banco de dados)
* **pymysql** (Conector Python-MySQL)
* **bcrypt** (Para hashing e segurança de senhas)

## 🚀 Como Executar

1.  Clone este repositório: `git clone <url-do-seu-repositorio>`
2.  Crie um banco de dados MySQL (você pode usar o `Banco Referência.txt` como referência para a estrutura).
3.  Configure suas credenciais de acesso ao banco no arquivo `configDB.py`.
4.  Instale as dependências necessárias:
    ```bash
    pip install pymysql bcrypt
    ```
5.  Execute o arquivo de login para iniciar o programa:
    ```bash
    python login.py
    ```