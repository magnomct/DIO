# 🚀 AWS CloudFormation: Servidor Web Nginx com Ubuntu e Firewall

> Este repositório contém um template de **Infraestrutura como Código (IaC)** usando o AWS CloudFormation. Ele provisiona de forma automatizada um servidor web rodando Ubuntu 22.04, protegido por um Security Group (Firewall), e instala o Nginx via script de inicialização (`UserData`).

---

## 📋 Índice

- [1. Arquitetura do Projeto](#1-arquitetura-do-projeto)
- [2. Pré-requisitos](#2-pré-requisitos)
- [3. O Template (YAML)](#3-o-template-yaml)
- [4. Como Fazer o Deploy](#4-como-fazer-o-deploy)
  - [Via Console AWS](#via-console-aws)
  - [Via AWS CLI](#via-aws-cli)
- [5. Solução de Problemas Comuns (Troubleshooting)](#5-solução-de-problemas-comuns-troubleshooting)
- [6. Limpeza (Evitando Custos)](#6-limpeza-evitando-custos)

---

## 1. Arquitetura do Projeto

Ao executar esta Stack, os seguintes recursos serão provisionados na sua conta AWS:

- **AWS::EC2::SecurityGroup**: Atua como o firewall da instância, permitindo apenas tráfego de entrada nas portas `80` (HTTP) para acesso ao site e `22` (SSH) para administração.
- **AWS::EC2::Instance**: Um servidor virtual (t2.micro por padrão, qualificado para o Free Tier).
  - **AMI Dinâmica**: Utiliza o AWS Systems Manager (SSM) para buscar sempre a versão mais recente e segura do Ubuntu 22.04 LTS.
  - **UserData Automático**: Um script Bash que roda no primeiro boot para atualizar o sistema, instalar o Nginx, habilitá-lo e criar uma página HTML personalizada.

---

## 2. Pré-requisitos

- Uma conta na AWS.
- Um **Key Pair (Chave SSH)** previamente criado na região onde você fará o deploy (ex: `us-east-1`).
- (Opcional) AWS CLI configurado na sua máquina local caso prefira fazer o deploy via terminal.

---

## 3. O Template (YAML)

O arquivo principal deste projeto é o `code.yaml`. Ele contém toda a declaração de recursos necessária para subir o ambiente.

_(Opcional: Você pode colocar o código YAML neste repositório em um arquivo separado)._

---

## 4. Como Fazer o Deploy

### Via Console AWS (Interface Gráfica)

1. Faça login no Console da AWS e navegue até o **CloudFormation**.
2. Clique em **Create stack > With new resources (standard)**.
3. Escolha **Upload a template file** e selecione o arquivo `.yaml` deste projeto.
4. Dê um nome para a Stack (ex: `StackServidorNginx`).
5. No parâmetro `KeyName`, selecione a sua chave SSH existente no menu suspenso.
6. Avance as próximas telas deixando as opções padrão e clique em **Submit**.
7. Aguarde a criação (status `CREATE_COMPLETE`). Vá até a aba **Outputs** e clique no link para ver o site no ar!

### Via AWS CLI (Terminal)

Execute o comando abaixo na mesma pasta onde está o arquivo, substituindo `NOME_DA_SUA_CHAVE` pelo nome real do seu Key Pair:

```bash
aws cloudformation create-stack \
  --stack-name NginxWebServer \
  --template-body file://nginx-firewall-stack.yaml \
  --parameters ParameterKey=KeyName,ParameterValue=NOME_DA_SUA_CHAVE
```
